"""
Unit tests for Display Name field functionality.
Verifies column display_name mapping, full_name property prioritizing display_name, and import handling.
"""

import pytest
from models import Associate
from services.import_service import ImportService


def test_display_name_column_and_property(db_session):
    """Verifies that Associate model has display_name column and full_name property prioritizes display_name."""
    assoc = Associate(
        display_name="Pawar",
        first_name="Pawar",
        last_name="",
        personal_email="pawar@example.com",
        designation="Software Engineer",
        location="Pune",
        work_mode="Virtual",
        employee_id="EMP-TEST-99"
    )
    db_session.add(assoc)
    db_session.commit()
    db_session.refresh(assoc)

    assert hasattr(assoc, "display_name")
    assert assoc.display_name == "Pawar"
    assert assoc.full_name == "Pawar"

    db_session.delete(assoc)
    db_session.commit()


def test_display_name_import_mapping():
    """Verifies that ImportService maps 'Display Name' column accurately."""
    row = {
        "Employee Number": "EMP7005",
        "Display Name": "Pawar",
        "Personal Email": "pawar.import@company.com",
        "Job Title": "Quality Engineer"
    }
    mapped = ImportService.map_row_to_associate_schema(row)
    assert mapped["display_name"] == "Pawar"
    assert mapped["full_name"] == "Pawar"


def test_display_name_bulk_ingestion(db_session):
    """Verifies bulk ingestion populates display_name and full_name correctly."""
    row = {
        "Employee Number": "EMP7006",
        "Display Name": "Om Pawar",
        "Work Email": "om.pawar@company.com",
        "Job Title": "Lead Architect"
    }
    valid, invalid = ImportService.process_and_validate([row], db_session)
    assert len(valid) == 1
    
    created = ImportService.ingest_records(db_session, valid)
    assert len(created) == 1
    assert created[0].display_name == "Om Pawar"
    assert created[0].full_name == "Om Pawar"

    db_session.delete(created[0])
    db_session.commit()
