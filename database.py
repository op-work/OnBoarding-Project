"""
Database Initialization and Connection Engine
Manages PostgreSQL database creation, session management, and realistic demo data seeding for Onboarding Operations.
"""

import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from config import DB_URI
from models import Base, Associate, OnboardingRecord, ActivityLog, User
from services.auth_service import AuthService
from utils.logger import app_logger
from utils.constants import (
    WORK_MODE_ONLINE,
    WORK_MODE_OFFLINE,
    STATUS_NOT_STARTED,
    STATUS_IN_PROGRESS,
    STATUS_COMPLETED,
    STAGE_PRE_ONBOARDING,
    STAGE_ONBOARDING_DAY,
    STAGE_POST_ONBOARDING,
)

engine = create_engine(DB_URI, pool_pre_ping=True, pool_size=10, max_overflow=20)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))



def get_db():
    """Returns a database session instance."""
    return SessionLocal()

def init_db():
    """Initializes tables and seeds initial demo data if database is empty or schema changed."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT display_name FROM associates LIMIT 1"))
            conn.execute(text("SELECT name_as_per_aadhar FROM associates LIMIT 1"))
            conn.execute(text("SELECT post_id_card_status FROM onboarding_records LIMIT 1"))
            conn.execute(text("SELECT post_probation_completed FROM onboarding_records LIMIT 1"))
            conn.execute(text("SELECT password_token FROM users LIMIT 1"))
    except Exception as e:
        app_logger.info(f"DATABASE: Schema change or missing columns detected ({e}). Recreating tables cleanly.")
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
    app_logger.info("DATABASE: Tables initialized successfully.")
    db = get_db()
    try:
        # Seed default admin user if empty
        AuthService.seed_default_user(db)
        
        associate_count = db.query(Associate).count()
        if associate_count == 0:
            app_logger.info("DATABASE: Seeding initial demo data.")
            seed_demo_data(db)
        else:
            # Sanitize legacy database records and populate display_name
            for assoc in db.query(Associate).all():
                changed = False
                if assoc.name_as_per_aadhar and assoc.name_as_per_aadhar.replace(" ", "").replace("-", "").isdigit():
                    assoc.name_as_per_aadhar = f"{assoc.first_name} {assoc.last_name}".strip() if (assoc.first_name and not assoc.first_name.isdigit()) else "Associate"
                    changed = True
                if assoc.first_name and assoc.first_name.replace(" ", "").replace("-", "").isdigit():
                    assoc.first_name = "Associate"
                    changed = True
                if assoc.first_name and assoc.first_name.lower() == "associate" and assoc.last_name:
                    assoc.first_name = assoc.last_name
                    assoc.last_name = ""
                    changed = True
                if not assoc.display_name:
                    if assoc.first_name and assoc.first_name.lower() != "associate":
                        assoc.display_name = f"{assoc.first_name} {assoc.last_name}".strip() if assoc.last_name else assoc.first_name
                    elif assoc.name_as_per_aadhar and not assoc.name_as_per_aadhar.replace(" ", "").replace("-", "").isdigit():
                        assoc.display_name = assoc.name_as_per_aadhar
                    else:
                        assoc.display_name = assoc.last_name or assoc.employee_id or "Associate"
                    changed = True
                if changed:
                    db.commit()
    finally:
        db.close()


def recalculate_associate_progress(db, associate_id: int):
    """
    Recalculates dynamic overall progress % and overall status for an associate based on milestone stage completion.
    Returns (overall_progress, overall_status)
    """
    record = db.query(OnboardingRecord).filter(OnboardingRecord.associate_id == associate_id).first()
    assoc = db.query(Associate).filter(Associate.id == associate_id).first()
    if not record or not assoc:
        return 0.0, STATUS_NOT_STARTED

    # Calculate Pre-Onboarding Stage Status based on 6 checklist items
    pre_items = [
        bool(record.pre_info_received),
        bool(record.pre_connect_joiner),
        record.pre_it_tickets_status == "Raised",
        bool(record.pre_notify_stakeholders),
        bool(record.pre_prepare_schedule),
        bool(record.pre_share_schedule)
    ]
    pre_completed_count = sum(1 for item in pre_items if item)
    if pre_completed_count == 6:
        record.pre_onboarding_status = STATUS_COMPLETED
        if assoc.work_mode in ["Virtual", "Online"] and record.it_equipment_status == "Pending Dispatch":
            record.it_equipment_status = "Dispatched"
    elif pre_completed_count > 0:
        record.pre_onboarding_status = STATUS_IN_PROGRESS
    else:
        record.pre_onboarding_status = STATUS_NOT_STARTED

    # Calculate Onboarding Day Stage Status based on 4 checklist items
    day1_items = [
        bool(record.day1_mandatory_forms),
        bool(record.day1_employment_docs),
        bool(record.day1_hr_induction),
        bool(record.day1_announce_joiner)
    ]
    day1_completed_count = sum(1 for item in day1_items if item)
    if day1_completed_count == 4:
        record.day1_orientation_status = STATUS_COMPLETED
    elif day1_completed_count > 0:
        record.day1_orientation_status = STATUS_IN_PROGRESS
    else:
        record.day1_orientation_status = STATUS_NOT_STARTED

    # Calculate Post-Onboarding Stage Status based on 4 checklist items
    post_items = [
        record.post_id_card_status == "Raised",
        record.post_hrms_doc_status == "Approved",
        bool(record.post_feedback_1week),
        bool(record.post_insurance_pf)
    ]
    post_completed_count = sum(1 for item in post_items if item)
    if post_completed_count == 4:
        record.post_onboarding_status = STATUS_COMPLETED
    elif post_completed_count > 0:
        record.post_onboarding_status = STATUS_IN_PROGRESS
    else:
        record.post_onboarding_status = STATUS_NOT_STARTED

    # Calculate 4th Stage: Feedback & Probation (does not affect primary onboarding progress)
    fb_items = [
        bool(record.post_feedback_30days),
        bool(record.post_feedback_60days),
        bool(record.post_feedback_90days),
        bool(record.post_probation_completed)
    ]
    fb_completed_count = sum(1 for item in fb_items if item)
    if fb_completed_count == 4:
        record.feedback_probation_status = STATUS_COMPLETED
        record.probation_status = "Confirmed"
    elif fb_completed_count > 0:
        record.feedback_probation_status = STATUS_IN_PROGRESS
        if bool(record.post_probation_completed):
            record.probation_status = "Confirmed"
        else:
            record.probation_status = "Under Review"
    else:
        record.feedback_probation_status = STATUS_NOT_STARTED
        record.probation_status = "Under Review"

    total_completed = pre_completed_count + day1_completed_count + post_completed_count
    total_items = 14  # 6 Pre + 4 Day1 + 4 Post items

    if total_completed == total_items:
        progress = 100.0
        new_status = STATUS_COMPLETED
        record.current_stage = STAGE_POST_ONBOARDING
        record.it_equipment_status = "Delivered"
        record.bgv_status = "Verified"
        if not record.completed_at:
            record.completed_at = datetime.datetime.utcnow()
    elif total_completed == 0:
        progress = 0.0
        new_status = "Draft" if assoc.status == "Draft" else STATUS_NOT_STARTED
        record.current_stage = STAGE_PRE_ONBOARDING
        record.completed_at = None
    else:
        progress = round((total_completed / float(total_items)) * 100.0, 1)
        new_status = STATUS_IN_PROGRESS
        record.completed_at = None
        if pre_completed_count < 6:
            record.current_stage = STAGE_PRE_ONBOARDING
        elif day1_completed_count < 4:
            record.current_stage = STAGE_ONBOARDING_DAY
        else:
            record.current_stage = STAGE_POST_ONBOARDING

    record.overall_progress = progress
    record.overall_status = new_status
    assoc.status = new_status

    db.commit()
    app_logger.info(f"PROGRESS: Recalculated for {assoc.full_name} ({assoc.employee_id}) -> Progress: {progress}%, Overall Status: {new_status}, Stage: {record.current_stage}")
    return progress, new_status

def seed_demo_data(db):
    """Seeds realistic associate profiles with varied departments, work modes, and milestone states."""
    today = datetime.date.today()

    demo_associates = [
        {
            "display_name": "Rahul Sharma",
            "first_name": "Rahul",
            "last_name": "Sharma",
            "personal_email": "rahul.sharma@example.com",
            "phone": "+91 9876543210",
            "designation": "Software Engineer",
            "department": "Engineering",
            "grade": "L2 - Senior Associate",
            "date_of_joining": today - datetime.timedelta(days=40),
            "location": "Pune",
            "reporting_manager": "Vikram Malhotra",
            "employee_id": "EMP-2026-001",
            "work_email": "rahul.sharma@company.com",
            "work_mode": WORK_MODE_ONLINE,
            "asset_shipment_address": "Flat 402, Baner, Pune 411045",
            "record": {
                "pre_info_received": True,
                "pre_connect_joiner": True,
                "pre_it_tickets_status": "Raised",
                "pre_notify_stakeholders": True,
                "pre_prepare_schedule": True,
                "pre_share_schedule": True,
                "day1_mandatory_forms": True,
                "day1_employment_docs": True,
                "day1_hr_induction": True,
                "day1_announce_joiner": True,
                "post_id_card_status": "Raised",
                "post_hrms_doc_status": "Approved",
                "post_feedback_1week": True,
                "post_insurance_pf": True,
                "post_feedback_30days": True,
                "post_feedback_60days": True,
                "post_feedback_90days": True,
                "it_equipment_status": "Delivered",
                "bgv_status": "Verified",
                "probation_status": "Confirmed",
            }
        },
        {
            "display_name": "Priya Patel",
            "first_name": "Priya",
            "last_name": "Patel",
            "personal_email": "priya.patel@example.com",
            "phone": "+91 9876543211",
            "designation": "HR Associate",
            "department": "Human Resources",
            "grade": "L1 - Associate",
            "date_of_joining": today - datetime.timedelta(days=15),
            "location": "Bengaluru",
            "reporting_manager": "Ananya Desai",
            "employee_id": "EMP-2026-002",
            "work_email": "priya.patel@company.com",
            "work_mode": WORK_MODE_OFFLINE,
            "asset_shipment_address": None,
            "record": {
                "pre_info_received": True,
                "pre_connect_joiner": True,
                "pre_it_tickets_status": "Raised",
                "pre_notify_stakeholders": True,
                "pre_prepare_schedule": True,
                "pre_share_schedule": True,
                "day1_mandatory_forms": True,
                "day1_employment_docs": True,
                "day1_hr_induction": True,
                "day1_announce_joiner": True,
                "post_id_card_status": "Raised",
                "post_hrms_doc_status": "Approved",
                "post_feedback_1week": False,
                "post_insurance_pf": False,
                "post_feedback_30days": False,
                "post_feedback_60days": False,
                "post_feedback_90days": False,
                "it_equipment_status": "Delivered",
                "bgv_status": "Verified",
                "probation_status": "Under Review",
            }
        },
        {
            "display_name": "Amit Verma",
            "first_name": "Amit",
            "last_name": "Verma",
            "personal_email": "amit.verma@example.com",
            "phone": "+91 9876543212",
            "designation": "Data Analyst",
            "department": "Data",
            "grade": "L1 - Associate",
            "date_of_joining": today - datetime.timedelta(days=5),
            "location": "Hyderabad",
            "reporting_manager": "Suresh Nair",
            "employee_id": "EMP-2026-003",
            "work_email": "amit.verma@company.com",
            "work_mode": WORK_MODE_ONLINE,
            "asset_shipment_address": "Plot 12, Jubilee Hills, Hyderabad 500033",
            "record": {
                "pre_info_received": True,
                "pre_connect_joiner": True,
                "pre_it_tickets_status": "Raised",
                "pre_notify_stakeholders": True,
                "pre_prepare_schedule": True,
                "pre_share_schedule": True,
                "day1_mandatory_forms": True,
                "day1_employment_docs": True,
                "day1_hr_induction": False,
                "day1_announce_joiner": False,
                "post_id_card_status": "Not Raised",
                "post_hrms_doc_status": "Pending Approval",
                "post_feedback_1week": False,
                "post_insurance_pf": False,
                "post_feedback_30days": False,
                "post_feedback_60days": False,
                "post_feedback_90days": False,
                "it_equipment_status": "Dispatched",
                "bgv_status": "Verified",
                "probation_status": "Under Review",
            }
        },
        {
            "display_name": "Sneha Joshi",
            "first_name": "Sneha",
            "last_name": "Joshi",
            "personal_email": "sneha.joshi@example.com",
            "phone": "+91 9876543213",
            "designation": "AI Engineer",
            "department": "AI",
            "grade": "L2 - Senior Associate",
            "date_of_joining": today + datetime.timedelta(days=3),
            "location": "Mumbai",
            "reporting_manager": "Dr. Rajesh Kulkarni",
            "employee_id": "EMP-2026-004",
            "work_email": "sneha.joshi@company.com",
            "work_mode": WORK_MODE_ONLINE,
            "asset_shipment_address": "Powai, Mumbai 400076",
            "record": {
                "pre_info_received": True,
                "pre_connect_joiner": True,
                "pre_it_tickets_status": "Raised",
                "pre_notify_stakeholders": False,
                "pre_prepare_schedule": False,
                "pre_share_schedule": False,
                "day1_mandatory_forms": False,
                "day1_employment_docs": False,
                "day1_hr_induction": False,
                "day1_announce_joiner": False,
                "post_id_card_status": "Not Raised",
                "post_hrms_doc_status": "Pending Approval",
                "post_feedback_1week": False,
                "post_insurance_pf": False,
                "post_feedback_30days": False,
                "post_feedback_60days": False,
                "post_feedback_90days": False,
                "it_equipment_status": "Dispatched",
                "bgv_status": "Verified",
                "probation_status": "Under Review",
            }
        },
        {
            "display_name": "Arjun Mehta",
            "first_name": "Arjun",
            "last_name": "Mehta",
            "personal_email": "arjun.mehta@example.com",
            "phone": "+91 9876543214",
            "designation": "Finance Associate",
            "department": "Finance",
            "grade": "L1 - Associate",
            "date_of_joining": today + datetime.timedelta(days=10),
            "location": "Delhi NCR",
            "reporting_manager": "Kavita Rao",
            "employee_id": "EMP-2026-005",
            "work_email": "arjun.mehta@company.com",
            "work_mode": WORK_MODE_OFFLINE,
            "asset_shipment_address": None,
            "record": {
                "pre_info_received": False,
                "pre_connect_joiner": False,
                "pre_it_tickets_status": "Not Raised",
                "pre_notify_stakeholders": False,
                "pre_prepare_schedule": False,
                "pre_share_schedule": False,
                "day1_mandatory_forms": False,
                "day1_employment_docs": False,
                "day1_hr_induction": False,
                "day1_announce_joiner": False,
                "post_id_card_status": "Not Raised",
                "post_hrms_doc_status": "Pending Approval",
                "post_feedback_1week": False,
                "post_insurance_pf": False,
                "post_feedback_30days": False,
                "post_feedback_60days": False,
                "post_feedback_90days": False,
                "it_equipment_status": "Pending Dispatch",
                "bgv_status": "In Progress",
                "probation_status": "Under Review",
            }
        },
    ]

    for item in demo_associates:
        rec_data = item.pop("record")
        assoc = Associate(**item, status=STATUS_NOT_STARTED)
        db.add(assoc)
        db.commit()
        db.refresh(assoc)

        rec = OnboardingRecord(
            associate_id=assoc.id,
            started_at=datetime.datetime.utcnow(),
            **rec_data
        )
        db.add(rec)
        db.commit()

        log = ActivityLog(
            associate_id=assoc.id,
            action="Associate Onboarding Initiated",
            description=f"Initiated onboarding record for {assoc.full_name} ({assoc.designation}). Work mode: {assoc.work_mode}.",
            performed_by="System Seed Engine",
        )
        db.add(log)
        db.commit()

        recalculate_associate_progress(db, assoc.id)

