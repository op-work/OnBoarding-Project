"""
Associate Management Service
Provides CRUD operations, candidate search filters, and record updates for Onboarding Operations.
"""

import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models import Associate, OnboardingRecord, ActivityLog
from database import recalculate_associate_progress
from utils.logger import app_logger

class AssociateService:
    @staticmethod
    def create_associate(db: Session, data: Dict[str, Any], is_draft: bool = False) -> Associate:
        """Creates a new associate record along with onboarding milestone record."""
        if not data.get("employee_id"):
            count = db.query(Associate).count() + 1
            data["employee_id"] = f"EMP-{datetime.date.today().year}-{count:03d}"

        work_mode = data.get("work_mode", "Virtual")
        status = "Draft" if is_draft else "Not Started"

        raw_first = (data.get("first_name") or "").strip()
        raw_last = (data.get("last_name") or "").strip()
        raw_aadhar_name = (data.get("name_as_per_aadhar") or "").strip()

        # Filter out numeric card/ID numbers passed in name fields
        if raw_aadhar_name and raw_aadhar_name.replace(" ", "").replace("-", "").isdigit():
            name_aadhar = f"{raw_first} {raw_last}".strip() if raw_first else ""
        else:
            name_aadhar = raw_aadhar_name

        if raw_first and not raw_first.replace(" ", "").replace("-", "").isdigit():
            first_name = raw_first
            last_name = raw_last
        elif name_aadhar and " " in name_aadhar:
            parts = name_aadhar.split(" ")
            first_name = parts[0]
            last_name = " ".join(parts[1:])
        else:
            first_name = name_aadhar or raw_first or "Associate"
            last_name = raw_last

        display_name_raw = (data.get("display_name") or "").strip()
        if display_name_raw and not display_name_raw.replace(" ", "").replace("-", "").isdigit():
            display_name = display_name_raw
        elif first_name and first_name.lower() != "associate":
            display_name = f"{first_name} {last_name}".strip() if last_name else first_name
        elif name_aadhar:
            display_name = name_aadhar
        elif last_name:
            display_name = last_name
        else:
            display_name = data.get("employee_id") or "Associate"

        assoc = Associate(
            display_name=display_name,
            name_as_per_aadhar=name_aadhar,
            first_name=first_name,
            last_name=last_name,
            preferred_name=data.get("preferred_name"),
            personal_email=data.get("personal_email", "").strip(),
            phone=data.get("phone", ""),
            date_of_birth=data.get("date_of_birth"),
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            postal_code=data.get("postal_code"),
            country=data.get("country"),
            emergency_contact_name=data.get("emergency_contact_name"),
            emergency_contact_phone=data.get("emergency_contact_phone"),
            emergency_contact_relationship=data.get("emergency_contact_relationship"),
            designation=data.get("designation", "").strip(),
            department=data.get("department", "General").strip() or "General",
            grade=data.get("grade"),
            date_of_joining=data.get("date_of_joining"),
            is_fresher=data.get("is_fresher", False),
            last_working_day=None if data.get("is_fresher") else data.get("last_working_day"),
            location=data.get("location", "").strip(),
            reporting_manager=data.get("reporting_manager", "HR Manager").strip() or "HR Manager",
            employee_id=data.get("employee_id", "").strip(),
            work_email=data.get("work_email"),
            work_mode=work_mode,
            asset_shipment_address=data.get("asset_shipment_address") if work_mode in ["Virtual", "Online"] else None,
            status=status,
        )
        db.add(assoc)
        db.commit()
        db.refresh(assoc)

        onboarding_rec = OnboardingRecord(
            associate_id=assoc.id,
            overall_status=status,
            overall_progress=0.0,
            current_stage="Pre-Onboarding",
            pre_onboarding_status="In Progress",
            it_equipment_status="Pending Dispatch" if work_mode in ["Virtual", "Online"] else "Delivered",
            bgv_status="In Progress",
            day1_orientation_status="Scheduled",
            post_onboarding_status="Not Started",
            probation_status="Under Review",
            started_at=datetime.datetime.utcnow() if not is_draft else None,
        )
        db.add(onboarding_rec)
        db.commit()

        recalculate_associate_progress(db, assoc.id)

        action = "Draft Saved" if is_draft else "Associate Created"
        log = ActivityLog(
            associate_id=assoc.id,
            action=action,
            description=f"{action} for {assoc.full_name} ({assoc.designation}). Work mode: {assoc.work_mode}.",
            performed_by="Onboarding Admin"
        )
        db.add(log)
        db.commit()

        app_logger.info(f"ASSOCIATE: {action} - {assoc.full_name} ({assoc.employee_id}, {assoc.designation}, {assoc.department})")

        return assoc

    @staticmethod
    def get_associate_by_id(db: Session, associate_id: int) -> Optional[Associate]:
        """Returns associate by primary key ID."""
        return db.query(Associate).filter(Associate.id == associate_id).first()

    @staticmethod
    def search_associates(
        db: Session,
        search_query: str = "",
        department: str = "All",
        location: str = "All",
        status: str = "All",
        work_mode: str = "All"
    ) -> List[Associate]:
        """Searches associates by text query and filtering criteria."""
        query = db.query(Associate)

        if search_query:
            pattern = f"%{search_query.strip()}%"
            query = query.filter(
                (Associate.display_name.ilike(pattern)) |
                (Associate.first_name.ilike(pattern)) |
                (Associate.last_name.ilike(pattern)) |
                (Associate.employee_id.ilike(pattern)) |
                (Associate.designation.ilike(pattern)) |
                (Associate.personal_email.ilike(pattern))
            )

        if department and department != "All":
            query = query.filter(Associate.department == department)

        if location and location != "All":
            query = query.filter(Associate.location == location)

        if status and status != "All":
            query = query.filter(Associate.status == status)

        if work_mode and work_mode != "All":
            query = query.filter(Associate.work_mode == work_mode)

        return query.order_by(Associate.created_at.desc()).all()

    @staticmethod
    def update_associate(db: Session, associate_id: int, updates: Dict[str, Any]) -> Optional[Associate]:
        """Updates associate attributes and refreshes timestamp."""
        assoc = db.query(Associate).filter(Associate.id == associate_id).first()
        if not assoc:
            return None

        for key, value in updates.items():
            if hasattr(assoc, key):
                setattr(assoc, key, value)

        assoc.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(assoc)
        app_logger.info(f"ASSOCIATE: Updated profile for {assoc.full_name} ({assoc.employee_id}) - Fields updated: {list(updates.keys())}")
        return assoc

    @staticmethod
    def delete_associate(db: Session, associate_id: int) -> bool:
        """Deletes an associate record along with all associated onboarding records and audit logs."""
        assoc = db.query(Associate).filter(Associate.id == associate_id).first()
        if not assoc:
            return False

        name_emp = f"{assoc.full_name} ({assoc.employee_id})"
        db.delete(assoc)
        db.commit()
        app_logger.info(f"ASSOCIATE: Deleted record for {name_emp}")
        return True

