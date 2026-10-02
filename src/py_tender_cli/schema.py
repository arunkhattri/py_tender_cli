"""DataFrame contracts for the tender CLI domain."""

from __future__ import annotations

import pandas as pd

MAKE_LIST_COLUMNS = [
    "source_document",
    "section",
    "item_no",
    "material",
    "make",
    "remarks",
    "source_page",
]

BOQ_COLUMNS = [
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

SOQ_MAKES_COLUMNS = [
    "tender_id",
    "boq_item_no",
    "make",
    "make_type",
    "context",
    "source_page",
]


def empty_make_list() -> pd.DataFrame:
    """Return an empty DataFrame conforming to the Make List contract."""
    return pd.DataFrame(columns=MAKE_LIST_COLUMNS)


def empty_boq() -> pd.DataFrame:
    """Return an empty DataFrame conforming to the BOQ/SOQ contract."""
    return pd.DataFrame(columns=BOQ_COLUMNS)


def empty_soq_makes() -> pd.DataFrame:
    """Return an empty DataFrame conforming to the SOQ-makes contract."""
    return pd.DataFrame(columns=SOQ_MAKES_COLUMNS)
