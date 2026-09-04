"""
Unit tests for ImportService.
Verifies CSV, Excel, and JSON file parsing, flexible 71-column schema mapping, missing column tolerance, duplicate email handling, and bulk database ingestion.
"""

import pytest
import json
import csv
import io
import openpyxl
from database import init_db, get_db
from models import Associate
from services.import_service import ImportService, ALL_HR_COLUMNS


def test_column_mapping_with_missing_columns():
    """Verifies that missing columns do not cause errors and provided columns map accurately."""
    # Row with only a subset of columns (missing Middle Name, Blood Group, Exit Date, etc.)
    partial_row = {
        "Employee Number": "EMP7001",
        "First Name": "Alice",
        "Last Name": "Smith",
        "Work Email": "alice.smith@company.com",
        "Job Title": "Senior Data Scientist",
        "Department": "Analytics",
        "Location": "Bangalore",
        "Date Joined": "2026-08-15",
        "Worker Type": "In-Person",
        "Aadhaar Number": "9999 8888 7777"
    }

    mapped = ImportService.map_row_to_associate_schema(partial_row)
    assert mapped["full_name"] == "Alice Smith"
    assert mapped["employee_id"] == "EMP7001"
    assert mapped["email"] == "alice.smith@company.com"
    assert mapped["designation"] == "Senior Data Scientist"
    assert mapped["department"] == "Analytics"
    assert mapped["location"] == "Bangalore"
    assert mapped["work_mode"] == "In-Person"
    assert mapped["name_as_per_aadhar"] == "Alice Smith"


def test_csv_excel_json_file_parsing():
    """Verifies parsing of CSV, Excel, and JSON file formats."""
    test_record = {
        "Employee Number": "EMP7002",
        "Full Name": "Bob Builder",
        "Work Email": "bob.builder@company.com",
        "Job Title": "DevOps Engineer",
        "Department": "Infrastructure",
        "Location": "Virtual",
        "Worker Type": "Virtual"
    }

    # Test CSV parsing
    csv_out = io.StringIO()
    writer = csv.DictWriter(csv_out, fieldnames=list(test_record.keys()))
    writer.writeheader()
    writer.writerow(test_record)
    csv_bytes = csv_out.getvalue().encode("utf-8")

    csv_rows = ImportService.parse_file(csv_bytes, "test.csv")
    assert len(csv_rows) == 1
    assert csv_rows[0]["Work Email"] == "bob.builder@company.com"

    # Test Excel parsing
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(list(test_record.keys()))
    ws.append(list(test_record.values()))
    xlsx_out = io.BytesIO()
    wb.save(xlsx_out)

    xlsx_rows = ImportService.parse_file(xlsx_out.getvalue(), "test.xlsx")
    assert len(xlsx_rows) == 1
    assert xlsx_rows[0]["Job Title"] == "DevOps Engineer"

    # Test JSON parsing
    json_bytes = json.dumps([test_record]).encode("utf-8")
    json_rows = ImportService.parse_file(json_bytes, "test.json")
    assert len(json_rows) == 1
    assert json_rows[0]["Employee Number"] == "EMP7002"


def test_bulk_ingestion_and_duplicate_handling(db_session):
    """Verifies batch validation, duplicate email detection, and database ingestion."""
    # Clean up existing test associate if present
    existing = db_session.query(Associate).filter((Associate.personal_email == "ingest.user@company.com") | (Associate.work_email == "ingest.user@company.com")).first()
    if existing:
        db_session.delete(existing)
        db_session.commit()

    records = [
        {
            "Employee Number": "EMP7003",
            "First Name": "Charlie",
            "Last Name": "Brown",
            "Work Email": "ingest.user@company.com",
            "Job Title": "Product Manager",
            "Department": "Product",
            "Location": "Mumbai",
            "Date Joined": "2026-09-01"
        }
    ]

    valid, invalid = ImportService.process_and_validate(records, db_session)
    assert len(valid) == 1
    assert len(invalid) == 0

    # Ingest records
    created = ImportService.ingest_records(db_session, valid)
    assert len(created) == 1
    assert created[0].personal_email == "ingest.user@company.com"


    # Re-validating the same email/employee ID should mark it as "Update" status for UPSERT
    valid_2, invalid_2 = ImportService.process_and_validate(records, db_session)
    assert len(valid_2) == 1
    assert valid_2[0]["import_status"] == "Update"
    assert "will update" in valid_2[0]["import_issue"].lower()



def test_detect_file_format():
    """Verifies file format recognition and unsupported file detection."""
    is_csv, label_csv, _ = ImportService.detect_file_format(b"col1,col2", "employees.csv")
    assert is_csv is True
    assert "CSV" in label_csv

    is_json, label_json, _ = ImportService.detect_file_format(b'[{"a": 1}]', "data.json")
    assert is_json is True
    assert "JSON" in label_json

    is_xlsx, label_xlsx, _ = ImportService.detect_file_format(b"PK\x03\x04...", "data.xlsx")
    assert is_xlsx is True
    assert "Excel" in label_xlsx

    is_unsupported, label_unsupported, _ = ImportService.detect_file_format(b"%PDF-1.4...", "document.pdf")
    assert is_unsupported is False
    assert label_unsupported == "File Not Supported"

