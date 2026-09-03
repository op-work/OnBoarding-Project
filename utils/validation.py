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

    # 1. Name as per Aadhar
    name = (data.get("name_as_per_aadhar") or data.get("first_name") or "").strip()
    if not name:
        errors["name_as_per_aadhar"] = "Name as per Aadhar is required."

    # 2. Confirmed Date of Joining
    doj = data.get("date_of_joining")
    if not doj:
        errors["date_of_joining"] = "Confirmed Date of Joining is required."

    # 3. Personal Email ID
    personal_email = (data.get("personal_email") or "").strip()
    if not personal_email:
        errors["personal_email"] = "Personal Email ID is required."
    elif not validate_email(personal_email):
        errors["personal_email"] = "Please enter a valid email address (e.g. associate@example.com)."

    # 4. Last Working Day (if not fresher)
    is_fresher = data.get("is_fresher", False)
    if not is_fresher:
        lwd = data.get("last_working_day")
        if not lwd:
            errors["last_working_day"] = "Last Working Day with Previous Employer is required (or tick Fresher)."

    # 5. Communicated Designation
    designation = (data.get("designation") or "").strip()
    if not designation:
        errors["designation"] = "Communicated Designation is required."

    # 6. Job Location
    location = (data.get("location") or "").strip()
    if not location:
        errors["location"] = "Job Location is required."

    # 7. Mode of Joining & Asset Delivery
    work_mode = data.get("work_mode", "Virtual")
    if work_mode in ["Virtual", "Online"]:
        asset_addr = (data.get("asset_shipment_address") or "").strip()
        if not asset_addr:
            errors["asset_shipment_address"] = "Associate address for asset delivery is required for Virtual joiners."

    is_valid = len(errors) == 0
    return is_valid, errors
