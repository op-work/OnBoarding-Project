"""
Database Initialization and Connection Engine
Manages PostgreSQL database creation, session management, and realistic demo data seeding for Onboarding Operations.
"""

import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from config import DB_URI, IS_DB_CONFIGURED
from models import Base, Associate, OnboardingRecord, ActivityLog, User
from services.auth_service import AuthService
from utils.logger import app_logger
from utils.constants import (
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

def init_db() -> bool:
    """Initializes tables and seeds initial demo data if database is empty or schema changed. Returns True on success, False on connection failure."""
    if not IS_DB_CONFIGURED:
        app_logger.warning("DATABASE: Unconfigured database parameters in .env file.")
        return False

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT display_name FROM associates LIMIT 1"))
            conn.execute(text("SELECT name_as_per_aadhar FROM associates LIMIT 1"))
            conn.execute(text("SELECT post_id_card_status FROM onboarding_records LIMIT 1"))
            conn.execute(text("SELECT post_probation_completed FROM onboarding_records LIMIT 1"))
            conn.execute(text("SELECT password_token FROM users LIMIT 1"))
    except Exception as e:
        app_logger.info(f"DATABASE: Schema check/migration attempt ({e}). Attempting table creation.")

    try:
        Base.metadata.create_all(bind=engine)
        app_logger.info("DATABASE: Tables initialized successfully.")
        db = get_db()
        try:
            # Seed default admin user if empty
            AuthService.seed_default_user(db)
            
            # Purge any legacy hardcoded demo records from previous test seeds if present
            demo_emp_ids = ["EMP-2026-001", "EMP-2026-002", "EMP-2026-003", "EMP-2026-004", "EMP-2026-005"]
            demo_associates = db.query(Associate).filter(Associate.employee_id.in_(demo_emp_ids)).all()
            if demo_associates:
                for d_assoc in demo_associates:
                    db.delete(d_assoc)
                db.commit()
                app_logger.info("DATABASE: Purged legacy demo associates for production readiness.")

            # Purge legacy hardcoded demo admin if present
            demo_user = db.query(User).filter(User.email == "admin@company.com").first()
            if demo_user:
                db.delete(demo_user)
                db.commit()
                app_logger.info("DATABASE: Purged legacy demo admin user.")

            # Sanitize existing database records and ensure valid display_name
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
        return True
    except Exception as err:
        app_logger.error(f"DATABASE: Failed to initialize PostgreSQL database: {err}")
        return False


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


