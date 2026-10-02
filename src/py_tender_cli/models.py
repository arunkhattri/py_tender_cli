from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class TableFragment:
    """A physical table extracted from one PDF page."""

    page_number: int
    table_index: int
    row_count: int
    col_count: int
    bbox: tuple[float, float, float, float]
    column_edges: tuple[float, ...] | None
    rows: list[list[str | None]]

    def to_dataframe(self) -> pd.DataFrame:
        """Convert this physical table fragment to a DataFrame."""

        return pd.DataFrame(self.rows)


@dataclass
class LogicalTable:
    """A logical table composed of one or more physical table fragments."""

    fragments: list[TableFragment]

    @property
    def page_start(self) -> int:
        """Return the first page containing this logical table."""

        return self.fragments[0].page_number

    @property
    def page_end(self) -> int:
        """Return the last page containing this logical table."""

        return self.fragments[-1].page_number

    @property
    def col_count(self) -> int:
        """Return the number of columns in the logical table."""

        return self.fragments[0].col_count

    @property
    def row_count(self) -> int:
        """Return the total number of rows across all fragments."""

        return sum(fragment.row_count for fragment in self.fragments)

    def to_dataframe(self) -> pd.DataFrame:
        """Combine all physical fragments into one DataFrame."""

        rows: list[list[str | None]] = []

        for fragment in self.fragments:
            rows.extend(fragment.rows)

        return pd.DataFrame(rows)


@dataclass(frozen=True)
class Section:
    """A document section located by its page range."""

    title: str
    page_start: int
    page_end: int
