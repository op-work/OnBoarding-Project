import re
import datetime
from typing import Dict, Tuple

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
PHONE_REGEX = r"^\+?[0-9\s\-\(\)]{8,20}$"

def validate_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    return bool(re.match(EMAIL_REGEX, email.strip()))

def validate_phone(phone: str) -> bool:
    if not phone or not isinstance(phone, str):
        return False
    return bool(re.match(PHONE_REGEX, phone.strip()))

def validate_associate_form(data: dict) -> Tuple[bool, Dict[str, str]]:
    errors = {}

    # Required text fields
    first_name = (data.get("first_name") or "").strip()
    if not first_name:
        errors["first_name"] = "First name / Associate name is required."

    last_name = (data.get("last_name") or "").strip()
    if not last_name:
        errors["last_name"] = "Last name is required."

    personal_email = (data.get("personal_email") or "").strip()
    if not personal_email:
        errors["personal_email"] = "Personal email is required."
    elif not validate_email(personal_email):
        errors["personal_email"] = "Please enter a valid email address (e.g. associate@example.com)."

    phone = (data.get("phone") or "").strip()
    if not phone:
        errors["phone"] = "Phone number is required."
    elif not validate_phone(phone):
        errors["phone"] = "Please enter a valid phone number (at least 8 digits)."

    designation = (data.get("designation") or "").strip()
    if not designation:
        errors["designation"] = "Designation / Position is required."

    department = (data.get("department") or "").strip()
    if not department:
        errors["department"] = "Department is required."

    location = (data.get("location") or "").strip()
    if not location:
        errors["location"] = "Location is required."

    reporting_manager = (data.get("reporting_manager") or "").strip()
    if not reporting_manager:
        errors["reporting_manager"] = "Reporting manager is required."

    doj = data.get("date_of_joining")
    if not doj:
        errors["date_of_joining"] = "Date of joining is required."

    work_mode = data.get("work_mode", "Online")
    if work_mode == "Online":
        asset_addr = (data.get("asset_shipment_address") or "").strip()
        if not asset_addr:
            errors["asset_shipment_address"] = "Asset shipment address is required for Online joiners."

    is_valid = len(errors) == 0
    return is_valid, errors
