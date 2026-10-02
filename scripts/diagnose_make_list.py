from __future__ import annotations

import pymupdf

from py_tender_cli.make_list import normalize_make_list, _sub_item_parts
from py_tender_cli.paths import DATA_DIR
from py_tender_cli.pdf_tables import extract_table_fragments
from py_tender_cli.section_locator import find_section
from py_tender_cli.section_tables import tables_for_section
from py_tender_cli.table_grouping import group_table_fragments


PDF_PATH = DATA_DIR / "NIT11.pdf"


def _pdf_text(pdf_path) -> str:
    """Extract plain text from the complete PDF."""

    with pymupdf.open(pdf_path) as document:
        return "\n".join(page.get_text() for page in document)


def test_make_list_integration() -> None:
    """Diagnostic: inspect Make List rows 72(i) and 72(ii)."""

    text = _pdf_text(PDF_PATH)

    section = find_section(
        text,
        "List of material of approved make(for Civil work)",
    )

    assert section is not None

    fragments = extract_table_fragments(PDF_PATH)
    logical_tables = group_table_fragments(fragments)

    tables = tables_for_section(
        logical_tables,
        section,
    )

    assert len(tables) == 1

    dataframe = tables[0].to_dataframe()

    assert dataframe.shape == (111, 3)

    print("\n" + "=" * 80)
    print("RAW DATAFRAME ROWS 72-75")
    print("=" * 80)

    for idx in range(71, 75):
        row = dataframe.iloc[idx]

        print(f"\nDataFrame index: {idx}")
        print(f"item   : {repr(row.iloc[0])}")
        print(f"material: {repr(row.iloc[1])}")
        print(f"make   : {repr(row.iloc[2])}")

        material = str(row.iloc[1]).strip()

        print(f"material after strip: {repr(material)}")
        print(f"_sub_item_parts(): {_sub_item_parts(material)}")

    print("\n" + "=" * 80)
    print("NORMALIZATION")
    print("=" * 80)

    normalized = normalize_make_list(
        dataframe,
        source_document=PDF_PATH.name,
        section=section.title,
        source_page=section.page_start,
    )

    print("\nNormalized shape:", normalized.shape)

    print("\nNormalized rows around item 72:")

    mask = normalized["item_no"].astype(str).str.startswith("72")

    print(
        normalized.loc[
            mask,
            ["item_no", "material", "make"],
        ].to_string(index=False)
    )

    print("\n" + "=" * 80)
    print("ALL NORMALIZED ITEM NUMBERS")
    print("=" * 80)

    print(normalized["item_no"].tolist())

    print("\n" + "=" * 80)
    print("ASSERTIONS")
    print("=" * 80)

    assert len(normalized) == 106
