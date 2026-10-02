"""Tests documenting the domain rules before extraction is implemented."""

import pandas as pd


def test_make_list_does_not_imply_project_requirement():
    make_list = pd.DataFrame(
        [
            {
                "source_document": "master.pdf",
                "section": "Boards",
                "item_no": "1",
                "material": "MDF",
                "make": "E3",
                "remarks": None,
                "source_page": 10,
            },
            {
                "source_document": "master.pdf",
                "section": "Boards",
                "item_no": "2",
                "material": "ACP",
                "make": "E3 Panels",
                "remarks": None,
                "source_page": 10,
            },
        ]
    )
    boq = pd.DataFrame(
        [
            {
                "tender_id": "T1",
                "item_no": "12",
                "description": "18mm MDF board",
                "quantity": 100,
                "unit": "sqm",
            }
        ]
    )

    assert len(make_list) == 2
    assert len(boq) == 1
    assert "ACP" not in boq.iloc[0]["description"]


def test_soq_make_is_project_specific():
    soq_makes = pd.DataFrame(
        [
            {
                "tender_id": "T1",
                "boq_item_no": "91",
                "make": "E3",
                "make_type": "material_make",
                "context": "HDHMR Board - approved make",
                "source_page": 70,
            }
        ]
    )

    assert soq_makes.iloc[0]["tender_id"] == "T1"
    assert soq_makes.iloc[0]["boq_item_no"] == "91"


def test_oem_is_distinguished_from_material_make():
    soq_makes = pd.DataFrame(
        [
            {
                "tender_id": "T1",
                "boq_item_no": "91",
                "make": "E3",
                "make_type": "material_make",
                "context": "HDHMR Board - approved make",
                "source_page": 70,
            },
            {
                "tender_id": "T1",
                "boq_item_no": "91",
                "make": "Godrej",
                "make_type": "oem_fabricator",
                "context": "Authorized OEM",
                "source_page": 70,
            },
        ]
    )

    assert soq_makes.loc[0, "make_type"] == "material_make"
    assert soq_makes.loc[1, "make_type"] == "oem_fabricator"
