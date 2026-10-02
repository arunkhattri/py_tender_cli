from __future__ import annotations

from .models import LogicalTable, TableFragment


def _compatible(
    first: TableFragment,
    second: TableFragment,
    *,
    tolerance: float,
) -> bool:
    """Return whether two fragments can be continuations."""

    if first.col_count != second.col_count:
        return False

    first_left, _, first_right, _ = first.bbox
    second_left, _, second_right, _ = second.bbox

    if abs(first_left - second_left) > tolerance:
        return False

    if abs(first_right - second_right) > tolerance:
        return False

    return True


def group_table_fragments(
    fragments: list[TableFragment],
    *,
    column_tolerance: float = 2.0,
) -> list[LogicalTable]:
    """Group consecutive compatible table fragments."""

    if not fragments:
        return []

    ordered = sorted(
        fragments,
        key=lambda fragment: (
            fragment.page_number,
            fragment.table_index,
        ),
    )

    logical_tables: list[LogicalTable] = []

    current_fragments = [ordered[0]]

    for fragment in ordered[1:]:
        previous = current_fragments[-1]

        continues = fragment.page_number == previous.page_number + 1 and _compatible(
            previous,
            fragment,
            tolerance=column_tolerance,
        )

        if continues:
            current_fragments.append(fragment)
        else:
            logical_tables.append(
                LogicalTable(
                    fragments=current_fragments,
                )
            )
            current_fragments = [fragment]

    logical_tables.append(
        LogicalTable(
            fragments=current_fragments,
        )
    )

    return logical_tables
