"""
Progress Metrics Service
Calculates stage progress and overall onboarding milestone metrics for associates.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from models import OnboardingRecord
from utils.constants import STAGE_PRE_ONBOARDING, STAGE_ONBOARDING_DAY, STAGE_POST_ONBOARDING, STATUS_COMPLETED, STATUS_IN_PROGRESS, STATUS_NOT_STARTED

class ProgressService:
    @staticmethod
    def get_stage_progress(db: Session, associate_id: int, stage: str) -> Dict[str, Any]:
        """Calculates status and completion percentage for a specific onboarding stage."""
        record = db.query(OnboardingRecord).filter(OnboardingRecord.associate_id == associate_id).first()
        if not record:
            return {
                "stage": stage,
                "status": STATUS_NOT_STARTED,
                "progress_pct": 0.0,
                "detail": "No record found"
            }

        if stage == STAGE_PRE_ONBOARDING:
            status = record.pre_onboarding_status
            pct = 100.0 if status == STATUS_COMPLETED else (50.0 if status == STATUS_IN_PROGRESS else 0.0)
            detail = f"IT Status: {record.it_equipment_status} | BGV: {record.bgv_status}"
        elif stage == STAGE_ONBOARDING_DAY:
            status = record.day1_orientation_status
            pct = 100.0 if status == STATUS_COMPLETED else (50.0 if status == "Scheduled" else 0.0)
            detail = f"Orientation: {record.day1_orientation_status}"
        else:
            status = record.post_onboarding_status
            pct = 100.0 if status == STATUS_COMPLETED else (50.0 if status == STATUS_IN_PROGRESS else 0.0)
            detail = f"Probation: {record.probation_status}"

        return {
            "stage": stage,
            "status": status,
            "progress_pct": pct,
            "detail": detail
        }

    @staticmethod
    def get_overall_progress(db: Session, associate_id: int) -> Dict[str, Any]:
        """Returns overall progress percentage and stage metrics for an associate."""
        record = db.query(OnboardingRecord).filter(OnboardingRecord.associate_id == associate_id).first()
        if not record:
            return {
                "associate_id": associate_id,
                "progress_pct": 0.0,
                "overall_status": STATUS_NOT_STARTED,
                "current_stage": STAGE_PRE_ONBOARDING,
                "stages": {}
            }

        stage_metrics = {
            STAGE_PRE_ONBOARDING: ProgressService.get_stage_progress(db, associate_id, STAGE_PRE_ONBOARDING),
            STAGE_ONBOARDING_DAY: ProgressService.get_stage_progress(db, associate_id, STAGE_ONBOARDING_DAY),
            STAGE_POST_ONBOARDING: ProgressService.get_stage_progress(db, associate_id, STAGE_POST_ONBOARDING),
        }

        return {
            "associate_id": associate_id,
            "progress_pct": record.overall_progress,
            "overall_status": record.overall_status,
            "current_stage": record.current_stage,
            "stages": stage_metrics
        }
