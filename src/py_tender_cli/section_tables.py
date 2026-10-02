from __future__ import annotations

from .models import LogicalTable, Section


def tables_for_section(
    tables: list[LogicalTable],
    section: Section,
) -> list[LogicalTable]:
    """Return logical tables contained within a document section."""

    return [
        table
        for table in tables
        if (
            table.page_start >= section.page_start
            and table.page_end <= section.page_end
        )
    ]
