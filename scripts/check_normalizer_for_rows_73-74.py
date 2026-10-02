from py_tender_cli.make_list import _sub_item_parts, normalize_make_list
from py_tender_cli.section_tables import extract_section_tables
from py_tender_cli.pdf_tables import extract_tables
from py_tender_cli.section_locator import locate_sections
from py_tender_cli.paths import DATA_DIR

pdf = DATA_DIR / "NIT11.pdf"

# Reproduce the same extraction pipeline used by the integration test.
# If your test uses a different extraction call, use that exact call here.
import pymupdf

doc = pymupdf.open(pdf)

# Find the Make List section and its tables.
sections = locate_sections(doc)
print("SECTIONS:")
for section in sections:
    print(section)

print("\n--- TABLES ---")

tables = extract_tables(doc)

for i, table in enumerate(tables):
    df = table.dataframe

    if len(df) == 111 and len(df.columns) == 3:
        print(f"\nCandidate table: {i}")
        print("shape:", df.shape)

        print("\nRAW ROWS 72-75:")
        for idx in range(71, 75):
            row = df.iloc[idx]
            print(
                idx,
                "|",
                repr(row.iloc[0]),
                "|",
                repr(row.iloc[1]),
                "|",
                repr(row.iloc[2]),
            )

        print("\nSUB-ITEM DETECTION:")
        for idx in (72, 73):
            material = str(df.iloc[idx, 1]).strip()
            print(
                idx,
                repr(material),
                "=>",
                _sub_item_parts(material),
            )

        print("\nNORMALIZATION:")
        normalized = normalize_make_list(
            df,
            source_document="NIT11.pdf",
            section="make_list",
            source_page=None,
        )

        print("normalized shape:", normalized.shape)

        print("\nNORMALIZED ITEMS AROUND 72:")
        print(
            normalized[
                normalized["item_no"].astype(str).str.startswith("72")
            ].to_string(index=False)
        )

        print("\nITEM COUNT:")
        print(normalized["item_no"].tolist())

        break
