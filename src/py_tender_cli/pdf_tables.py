from __future__ import annotations

from pathlib import Path

import pymupdf

from .models import TableFragment


def extract_table_fragments(
    pdf_path: str | Path,
) -> list[TableFragment]:
    """Extract physical table fragments from a PDF.

    Page numbers are one-based so they correspond directly to the
    page numbers visible in the tender document.
    """

    pdf_path = Path(pdf_path)

    fragments: list[TableFragment] = []

    with pymupdf.open(pdf_path) as document:
        for page_index, page in enumerate(document):
            page_number = page_index + 1

            tables = page.find_tables()

            for table_index, table in enumerate(tables.tables):
                rows = table.extract()

                if not rows:
                    continue

                col_count = len(rows[0])

                fragments.append(
                    TableFragment(
                        page_number=page_number,
                        table_index=table_index,
                        row_count=len(rows),
                        col_count=col_count,
                        bbox=tuple(table.bbox),
                        column_edges=_column_edges(table),
                        rows=rows,
                    )
                )

    return fragments


def _column_edges(table: object) -> tuple[float, ...] | None:
    """Return detected vertical column boundaries when available."""

    edges = getattr(table, "edges", None)

    if not edges:
        return None

    vertical_edges = [edge for edge in edges if edge.get("orientation") == "v"]

    if not vertical_edges:
        return None

    positions = sorted(
        {float(edge["x0"]) for edge in vertical_edges}
        | {float(edge["x1"]) for edge in vertical_edges}
    )

    return tuple(positions)
