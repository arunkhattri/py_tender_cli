from __future__ import annotations

import re

import pandas as pd

from .schema import BOQ_COLUMNS


_ITEM_NUMBER = re.compile(r"^\d+(?:\.\d+)*\.?$")


def _is_empty(value: object) -> bool:
    """Return whether a value is empty or missing."""

    return pd.isna(value) or (isinstance(value, str) and not value.strip())


def _clean_text(value: object) -> str:
    """Convert a table value to clean text."""

    if _is_empty(value):
        return ""

    return str(value).strip()


def _clean_item_number(value: object) -> str:
    """Normalize a BOQ item number."""

    return _clean_text(value).removesuffix(".")


def _is_item_number(value: object) -> bool:
    """Return whether a value represents a BOQ item number."""

    return bool(_ITEM_NUMBER.fullmatch(_clean_text(value)))


def _parent_item_no(item_no: str) -> str:
    """Return the parent item number for a hierarchical BOQ item."""

    if "." not in item_no:
        return ""

    return item_no.rsplit(".", 1)[0]


def _combine_description(
    current: str,
    continuation: str,
) -> str:
    """Append continuation text to a BOQ description."""

    if not current:
        return continuation

    if not continuation:
        return current

    return f"{current} {continuation}"


def normalize_boq(
    dataframe: pd.DataFrame,
    *,
    tender_id: str = "",
    section: str = "",
    source_page: int | None = None,
) -> pd.DataFrame:
    """Normalize a raw BOQ/SOQ table.

    The raw table is expected to contain:

        item number
        description
        quantity
        unit
        rate
        amount

    Hierarchical item numbers such as ``1.1`` retain their parent
    item number in ``parent_item_no``.
    """

    records: list[dict[str, object]] = []

    current_record: dict[str, object] | None = None

    for _, row in dataframe.iloc[1:].iterrows():
        item = row.iloc[0]
        description = row.iloc[1]
        quantity = row.iloc[2]
        unit = row.iloc[3]
        rate = row.iloc[4]
        amount = row.iloc[5]

        if _is_item_number(item):
            item_no = _clean_item_number(item)

            current_record = {
                "tender_id": tender_id,
                "section": section,
                "item_no": item_no,
                "parent_item_no": _parent_item_no(item_no),
                "description": _clean_text(description),
                "unit": _clean_text(unit),
                "quantity": _clean_text(quantity),
                "rate": _clean_text(rate),
                "amount": _clean_text(amount),
                "remarks": "",
                "source_page": source_page,
            }

            records.append(current_record)
            continue

        # A row without an item number is normally a continuation
        # of the preceding BOQ description.
        if current_record is not None and not _is_empty(description):
            current_record["description"] = _combine_description(
                str(current_record["description"]),
                _clean_text(description),
            )

    return pd.DataFrame(
        records,
        columns=BOQ_COLUMNS,
    )
