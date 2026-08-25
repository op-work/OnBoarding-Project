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
            pre_items = [
                bool(record.pre_info_received),
                bool(record.pre_connect_joiner),
                record.pre_it_tickets_status == "Raised",
                bool(record.pre_notify_stakeholders),
                bool(record.pre_prepare_schedule),
                bool(record.pre_share_schedule)
            ]
            completed_cnt = sum(1 for item in pre_items if item)
            total_cnt = 6
            pct = round((completed_cnt / total_cnt) * 100.0, 1)
            detail = f"{completed_cnt} / {total_cnt} Milestones Verified ({pct}%)"
            return {
                "stage": stage,
                "status": status,
                "progress_pct": pct,
                "completed": completed_cnt,
                "total": total_cnt,
                "detail": detail
            }
        elif stage == STAGE_ONBOARDING_DAY:
            status = record.day1_orientation_status
            day1_items = [
                bool(record.day1_mandatory_forms),
                bool(record.day1_employment_docs),
                bool(record.day1_hr_induction),
                bool(record.day1_announce_joiner)
            ]
            completed_cnt = sum(1 for item in day1_items if item)
            total_cnt = 4
            pct = round((completed_cnt / total_cnt) * 100.0, 1)
            detail = f"{completed_cnt} / {total_cnt} Milestones Verified ({pct}%)"
            return {
                "stage": stage,
                "status": status,
                "progress_pct": pct,
                "completed": completed_cnt,
                "total": total_cnt,
                "detail": detail
            }
        else:
            status = record.post_onboarding_status
            post_items = [
                record.post_id_card_status == "Raised",
                record.post_hrms_doc_status == "Approved",
                bool(record.post_feedback_1week),
                bool(record.post_insurance_pf),
                bool(record.post_feedback_30days),
                bool(record.post_feedback_60days),
                bool(record.post_feedback_90days)
            ]
            completed_cnt = sum(1 for item in post_items if item)
            total_cnt = 7
            pct = round((completed_cnt / total_cnt) * 100.0, 1)
            detail = f"{completed_cnt} / {total_cnt} Milestones Verified ({pct}%)"
            return {
                "stage": stage,
                "status": status,
                "progress_pct": pct,
                "completed": completed_cnt,
                "total": total_cnt,
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
