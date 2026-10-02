from __future__ import annotations

import pymupdf

from py_tender_cli.make_list import normalize_make_list
from py_tender_cli.paths import DATA_DIR
from py_tender_cli.pdf_tables import extract_table_fragments
from py_tender_cli.section_locator import find_section
from py_tender_cli.section_tables import tables_for_section
from py_tender_cli.table_grouping import group_table_fragments


PDF_PATH = DATA_DIR / "NIT11.pdf"


def _pdf_text(pdf_path) -> str:
    with pymupdf.open(pdf_path) as document:
        return "\n".join(page.get_text() for page in document)


def test_make_list_integration() -> None:
    text = _pdf_text(PDF_PATH)

    section = find_section(
        text,
        "List of material of approved make(for Civil work)",
    )

    assert section is not None

    fragments = extract_table_fragments(PDF_PATH)
    logical_tables = group_table_fragments(fragments)
    tables = tables_for_section(logical_tables, section)

    assert len(tables) == 1

    dataframe = tables[0].to_dataframe()

    assert dataframe.shape == (111, 3)

    assert dataframe.iloc[0].tolist() == [
        "Sl.No.",
        "Details of Materials",
        "Manufacturer Name",
    ]

    normalized = normalize_make_list(
        dataframe,
        source_document=PDF_PATH.name,
        section=section.title,
        source_page=section.page_start,
    )

    assert len(normalized) == 106

    assert normalized.columns.tolist() == [
        "source_document",
        "section",
        "item_no",
        "material",
        "make",
        "remarks",
        "source_page",
    ]

    # 72(i)
    row = normalized.iloc[71]

    assert row["item_no"] == "72(i)"
    assert row["material"] == "Metal False Ceiling"
    assert row["make"] == (
        "Armstrong (Knauf), Hunter douglas, Durlum, "
        "Gyptech, HI-STEEL, Saint Gobain, Royal Kraft, R.K.Ceiling"
    )

    # 72(ii)
    row = normalized.iloc[72]

    assert row["item_no"] == "72(ii)"
    assert row["material"] == ("Gypsum False Ceiling/ Calcium Silicate/GRG Ceiling")
    assert row["make"] == (
        "USG Boral, Saint Gobain, Aerolite, Interarch, Dexune, Gyptech, HI-STEEL"
    )

    # 75(a)
    row = normalized.iloc[75]

    assert row["item_no"] == "75a)"
    assert row["material"] == "R.C. Matteress"
    assert row["make"] == ("Pearl Rupa Super Ortho model, New Ortho of Kurlon model,")

    # 92
    row = normalized.iloc[96]

    assert row["item_no"] == "92"
    assert row["material"] == "Fire rated clear glass"
    # assert row["make"] == (
    #     "Saint Gobain / Schott/ Pilkington/Pyroguard/Glabervel / Firelite"
    # )
    assert row["make"] == (
        "Saint Gobain / Schott/ Pilkington/Pyroguard/ Glabervel / Firelite"
    )
    assert normalized["source_document"].eq(PDF_PATH.name).all()
    assert normalized["section"].eq(section.title).all()
