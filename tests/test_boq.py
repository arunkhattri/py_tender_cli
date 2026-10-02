from __future__ import annotations

import pymupdf

from py_tender_cli.boq import normalize_boq
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


def test_boq_integration() -> None:
    """Extract and normalize the BOQ/SOQ from NIT11."""

    text = _pdf_text(PDF_PATH)

    section = find_section(
        text,
        "Schedule of Quantity",
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

    # Real source table.
    assert dataframe.shape == (30, 6)

    assert dataframe.iloc[0].tolist() == [
        "S.No.",
        "Description of Items",
        "Quantity",
        "Unit",
        "Rate",
        "Amount",
    ]

    normalized = normalize_boq(
        dataframe,
        tender_id=PDF_PATH.stem,
        section=section.title,
        source_page=section.page_start,
    )

    # The source table contains 30 rows and produces
    # 24 normalized BOQ records.
    assert len(normalized) == 24

    # Verify the frozen BOQ schema.
    assert normalized.columns.tolist() == [
        "tender_id",
        "section",
        "item_no",
        "parent_item_no",
        "description",
        "unit",
        "quantity",
        "rate",
        "amount",
        "remarks",
        "source_page",
    ]

    # First item.
    row = normalized.iloc[0]

    assert row["item_no"] == "1"
    assert row["parent_item_no"] == ""
    assert row["description"] != ""

    # Hierarchical item.
    row = normalized.iloc[1]

    assert row["item_no"] == "1.1"
    assert row["parent_item_no"] == "1"

    # Third item.
    row = normalized.iloc[2]

    assert row["item_no"] == "2"

    # Last item.
    row = normalized.iloc[-1]

    assert row["item_no"] == "19"

    # Metadata should have propagated into every record.
    assert normalized["tender_id"].eq(PDF_PATH.stem).all()

    assert normalized["section"].eq(section.title).all()

    assert normalized["source_page"].eq(section.page_start).all()
