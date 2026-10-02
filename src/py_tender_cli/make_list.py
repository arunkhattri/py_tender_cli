from __future__ import annotations

import re

import pandas as pd

from .schema import MAKE_LIST_COLUMNS


_SUB_ITEM = re.compile(
    r"^(?P<marker>\([ivx]+\)|[a-z]\))\s*(?P<material>.+)$",
    flags=re.IGNORECASE | re.DOTALL,
)


def _is_empty(value: object) -> bool:
    """Return whether a value is empty or missing."""

    return pd.isna(value) or (isinstance(value, str) and not value.strip())


def _is_item_number(value: object) -> bool:
    """Return whether a value is a normal Make List item number."""

    if not isinstance(value, str):
        return False

    return bool(
        re.fullmatch(
            r"\d+\.",
            value.strip(),
        )
    )


def _sub_item_parts(
    value: object,
) -> tuple[str, str] | None:
    """Return sub-item marker and material text."""

    if not isinstance(value, str):
        return None

    match = _SUB_ITEM.match(value.strip())

    if match is None:
        return None

    return (
        match.group("marker"),
        _normalize_cell_text(match.group("material")),
    )


def _clean_item_number(value: str) -> str:
    """Remove the trailing period from a normal item number."""

    return value.strip().removesuffix(".")


def _normalize_cell_text(value: object) -> str:
    """Remove PDF line breaks inside a logical table cell.

    Physical line wrapping is normalized, while the actual textual
    content and formatting of the cell are otherwise preserved.
    """

    if _is_empty(value):
        return ""

    text = str(value).strip()

    # A slash at the end of a physical line means the next text
    # continues immediately. Remove horizontal whitespace and the
    # complete line ending.
    text = re.sub(r"/[ \t]*(?:\r\n|\r|\n)[ \t]*", "/", text)

    # Other physical line breaks represent a text boundary.
    # Replace the complete line ending and surrounding horizontal
    # whitespace with one space.
    text = re.sub(r"[ \t]*(?:\r\n|\r|\n)[ \t]*", " ", text)

    return text


def _combine_text(*values: object) -> str:
    """Combine continuation-cell fragments into one text value."""

    parts: list[str] = []

    for value in values:
        if _is_empty(value):
            continue

        text = _normalize_cell_text(value)

        if text:
            parts.append(text)

    return " ".join(parts)


def normalize_make_list(
    dataframe: pd.DataFrame,
    *,
    source_document: str = "",
    section: str = "",
    source_page: int | None = None,
) -> pd.DataFrame:
    """Normalize a raw Make List table into project records.

    The raw table is expected to contain:

        item number
        material
        manufacturer / make

    Metadata identifies where the normalized records came from.
    """

    records: list[dict[str, object]] = []

    parent_item: str | None = None

    for _, row in dataframe.iloc[1:].iterrows():
        item = row.iloc[0]
        material = row.iloc[1]
        make = row.iloc[2]

        # Ignore standalone section headings.
        if (
            _is_empty(item)
            and isinstance(material, str)
            and material.startswith("LIST OF APPROVED MAKE")
        ):
            continue

        # Normal numbered item.
        if _is_item_number(item):
            parent_item = _clean_item_number(item)

            if not _is_empty(make):
                records.append(
                    {
                        "source_document": source_document,
                        "section": section,
                        "item_no": parent_item,
                        "material": (
                            _normalize_cell_text(material)
                            if not _is_empty(material)
                            else ""
                        ),
                        "make": _normalize_cell_text(make),
                        "remarks": "",
                        "source_page": source_page,
                    }
                )

            continue

        # Sub-item: (i), (ii), a), b), etc.
        sub_item = _sub_item_parts(material)

        if sub_item is not None:
            if parent_item is None:
                continue

            marker, child_material = sub_item

            records.append(
                {
                    "source_document": source_document,
                    "section": section,
                    "item_no": f"{parent_item}{marker}",
                    "material": child_material,
                    "make": (_normalize_cell_text(make) if not _is_empty(make) else ""),
                    "remarks": "",
                    "source_page": source_page,
                }
            )

            continue

        # Continuation row: no item number and no material.
        if records and _is_empty(item) and _is_empty(material) and not _is_empty(make):
            records[-1]["make"] = _combine_text(
                records[-1]["make"],
                make,
            )

    return pd.DataFrame(
        records,
        columns=MAKE_LIST_COLUMNS,
    )
