import pymupdf

from py_tender_cli.make_list import normalize_make_list
from py_tender_cli.paths import DATA_DIR
from py_tender_cli.pdf_tables import extract_table_fragments
from py_tender_cli.section_locator import find_section
from py_tender_cli.section_tables import tables_for_section
from py_tender_cli.table_grouping import group_table_fragments


PDF_PATH = DATA_DIR / "NIT11.pdf"


def main() -> None:
    with pymupdf.open(PDF_PATH) as document:
        pdf_text = "\n".join(page.get_text() for page in document)

    section = find_section(
        pdf_text,
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

    print("RAW ROWS AROUND ITEMS 72–73")
    print("=" * 100)

    for index in range(68, 76):
        print(f"{index:3}: {[repr(value) for value in dataframe.iloc[index].tolist()]}")

    normalized = normalize_make_list(
        dataframe,
        source_document=PDF_PATH.name,
        section=section.title,
        source_page=section.page_start,
    )

    print()
    print("NORMALIZED ROWS AROUND ITEMS 72–73")
    print("=" * 100)

    for index, row in normalized.iterrows():
        if 68 <= index <= 74:
            print(
                f"{index:3}: "
                f"{row['item_no']!r:8} | "
                f"{row['material']!r:70} | "
                f"{row['make']!r}"
            )

    print()
    print(f"Raw shape:        {dataframe.shape}")
    print(f"Normalized shape: {normalized.shape}")


if __name__ == "__main__":
    main()
