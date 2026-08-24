"""
Reporting and Analytics Service
Generates dashboard metrics, department breakdowns, and onboarding milestone analytics.
"""

import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Associate, OnboardingRecord
from utils.constants import STATUS_COMPLETED, STATUS_IN_PROGRESS, STATUS_NOT_STARTED

class ReportService:
    @staticmethod
    def get_dashboard_metrics(db: Session) -> Dict[str, Any]:
        """Calculates executive dashboard KPI metrics."""
        total_associates = db.query(Associate).count()
        active_onboarding = db.query(OnboardingRecord).filter(OnboardingRecord.overall_status == STATUS_IN_PROGRESS).count()
        completed_onboarding = db.query(OnboardingRecord).filter(OnboardingRecord.overall_status == STATUS_COMPLETED).count()
        not_started = db.query(OnboardingRecord).filter(OnboardingRecord.overall_status == STATUS_NOT_STARTED).count()

        records = db.query(OnboardingRecord).all()
        avg_progress = round(sum(r.overall_progress for r in records) / len(records), 1) if records else 0.0

        # Upcoming joiners in the next 14 days
        today = datetime.date.today()
        upcoming_count = db.query(Associate).filter(
            Associate.date_of_joining >= today,
            Associate.date_of_joining <= today + datetime.timedelta(days=14)
        ).count()

        return {
            "total_associates": total_associates,
            "active_onboarding": active_onboarding,
            "completed_onboarding": completed_onboarding,
            "not_started": not_started,
            "upcoming_joiners": upcoming_count,
            "avg_progress": avg_progress
        }

    @staticmethod
    def get_department_breakdown(db: Session) -> Dict[str, int]:
        """Returns candidate distribution by department."""
        results = db.query(Associate.department, func.count(Associate.id)).group_by(Associate.department).all()
        return {dept: count for dept, count in results if dept}

    @staticmethod
    def get_status_breakdown(db: Session) -> Dict[str, int]:
        """Returns candidate distribution by onboarding status."""
        results = db.query(OnboardingRecord.overall_status, func.count(OnboardingRecord.id)).group_by(OnboardingRecord.overall_status).all()
        return {status: count for status, count in results if status}

    @staticmethod
    def get_stage_breakdown(db: Session) -> Dict[str, int]:
        """Returns associate count by current stage."""
        results = db.query(OnboardingRecord.current_stage, func.count(OnboardingRecord.id)).group_by(OnboardingRecord.current_stage).all()
        return {stage: count for stage, count in results if stage}
