from py_tender_cli.schema import (
    BOQ_COLUMNS,
    MAKE_LIST_COLUMNS,
    SOQ_MAKES_COLUMNS,
    empty_boq,
    empty_make_list,
    empty_soq_makes,
)


def test_make_list_contract():
    frame = empty_make_list()
    assert frame.empty
    assert frame.columns.tolist() == MAKE_LIST_COLUMNS


def test_boq_contract():
    frame = empty_boq()
    assert frame.empty
    assert frame.columns.tolist() == BOQ_COLUMNS


def test_soq_makes_contract():
    frame = empty_soq_makes()
    assert frame.empty
    assert frame.columns.tolist() == SOQ_MAKES_COLUMNS
