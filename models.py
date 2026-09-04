"""
Database Models for Onboarding Operations System
Contains SQLAlchemy ORM definitions for Associates, Onboarding Records, and Activity Logs.
"""

import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Date,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Associate(Base):
    """
    Represents an associate (employee) undergoing onboarding operations.
    Stores personal details, employment specifications, location, and work mode.
    """
    __tablename__ = "associates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    display_name = Column(String(150), nullable=True)
    name_as_per_aadhar = Column(String(150), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True, default="")
    preferred_name = Column(String(100), nullable=True)
    personal_email = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=True, default="")
    date_of_birth = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    emergency_contact_name = Column(String(150), nullable=True)
    emergency_contact_phone = Column(String(50), nullable=True)
    emergency_contact_relationship = Column(String(50), nullable=True)
    
    designation = Column(String(150), nullable=False)
    department = Column(String(100), nullable=True, default="General")
    grade = Column(String(50), nullable=True)
    date_of_joining = Column(Date, nullable=False)
    is_fresher = Column(Boolean, default=False)
    last_working_day = Column(Date, nullable=True)
    location = Column(String(100), nullable=False)
    reporting_manager = Column(String(150), nullable=True, default="HR Manager")
    employee_id = Column(String(50), unique=True, nullable=False)
    work_email = Column(String(150), nullable=True)
    work_mode = Column(String(20), nullable=False, default="Virtual")  # In-person or Virtual
    asset_shipment_address = Column(Text, nullable=True)
    
    status = Column(String(50), nullable=False, default="Not Started")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    onboarding_record = relationship("OnboardingRecord", back_populates="associate", uselist=False, cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="associate", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        """Returns the full display name of the associate."""
        # 1. Prioritize display_name if set and valid non-numeric
        if self.display_name and not self.display_name.replace(" ", "").replace("-", "").isdigit():
            clean_display = self.display_name.strip()
            if clean_display.lower().startswith("associate ") and len(clean_display.split()) > 1:
                return " ".join(clean_display.split()[1:])
            return clean_display

        # 2. Prioritize first_name and last_name if first_name is a valid non-numeric string
        if self.first_name and not self.first_name.replace(" ", "").replace("-", "").isdigit():
            if self.first_name.strip().lower() == "associate" and self.last_name:
                return self.last_name.strip()
            if self.last_name:
                return f"{self.first_name} {self.last_name}".strip()
            if self.first_name.strip().lower() != "associate":
                return self.first_name.strip()

        # 3. Use name_as_per_aadhar if it exists and is not purely numeric
        if self.name_as_per_aadhar and not self.name_as_per_aadhar.replace(" ", "").replace("-", "").isdigit():
            return self.name_as_per_aadhar.strip()
            
        # 4. Fallbacks
        if self.last_name:
            return self.last_name.strip()
        if self.first_name and self.first_name.strip().lower() != "associate":
            return self.first_name.strip()
        return self.employee_id or "Associate"


class OnboardingRecord(Base):
    """
    Tracks onboarding milestone progress, stage transitions, IT dispatch, and verification.
    """
    __tablename__ = "onboarding_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    associate_id = Column(Integer, ForeignKey("associates.id", ondelete="CASCADE"), nullable=False)
    overall_status = Column(String(50), default="Not Started")  # Not Started, In Progress, Completed
    overall_progress = Column(Float, default=0.0)
    current_stage = Column(String(100), default="Pre-Onboarding")  # Pre-Onboarding, Onboarding Day, Post-Onboarding
    
    # Milestone Stages
    pre_onboarding_status = Column(String(50), default="Not Started")
    it_equipment_status = Column(String(50), default="Pending Dispatch")  # Pending Dispatch, Dispatched, Delivered
    bgv_status = Column(String(50), default="In Progress")  # Not Started, In Progress, Verified
    day1_orientation_status = Column(String(50), default="Scheduled")  # Not Started, Scheduled, Completed
    post_onboarding_status = Column(String(50), default="Not Started")  # Not Started, In Progress, Completed
    probation_status = Column(String(50), default="Under Review")  # Under Review, Confirmed
    feedback_probation_status = Column(String(50), default="Not Started")  # Not Started, In Progress, Completed

    # Pre-Onboarding Specific Checklist Fields
    pre_info_received = Column(Boolean, default=False)
    pre_connect_joiner = Column(Boolean, default=False)
    pre_it_tickets_status = Column(String(50), default="Not Raised")  # Not Raised, Raised
    pre_notify_stakeholders = Column(Boolean, default=False)
    pre_prepare_schedule = Column(Boolean, default=False)
    pre_share_schedule = Column(Boolean, default=False)

    # Onboarding Day Specific Checklist Fields
    day1_mandatory_forms = Column(Boolean, default=False)
    day1_employment_docs = Column(Boolean, default=False)
    day1_hr_induction = Column(Boolean, default=False)
    day1_announce_joiner = Column(Boolean, default=False)

    # Post-Onboarding Specific Checklist Fields
    post_id_card_status = Column(String(50), default="Not Raised")  # Not Raised, Raised
    post_hrms_doc_status = Column(String(50), default="Pending Approval")  # Pending Approval, Approved
    post_feedback_1week = Column(Boolean, default=False)
    post_insurance_pf = Column(Boolean, default=False)
    post_feedback_30days = Column(Boolean, default=False)
    post_feedback_60days = Column(Boolean, default=False)
    post_feedback_90days = Column(Boolean, default=False)
    post_probation_completed = Column(Boolean, default=False)

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    associate = relationship("Associate", back_populates="onboarding_record")


class ActivityLog(Base):
    """
    Audit log for tracking system actions, stage updates, and candidate profile modifications.
    """
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    associate_id = Column(Integer, ForeignKey("associates.id", ondelete="CASCADE"), nullable=True)
    action = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    performed_by = Column(String(100), default="Onboarding Admin")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    associate = relationship("Associate", back_populates="activity_logs")


class User(Base):
    """
    Represents an application user (HR Admin / Manager).
    Password is saved in password_token form as an encrypted/signed JWT token.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_token = Column(Text, nullable=False)  # JWT Encoded Password Token
    role = Column(String(50), nullable=False, default="HR Admin")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

