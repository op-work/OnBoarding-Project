"""
Activity Audit Trail Service
Logs and fetches system audit events and onboarding milestone activity logs.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from models import ActivityLog

class ActivityService:
    @staticmethod
    def get_activity_history(db: Session, associate_id: Optional[int] = None, limit: int = 50) -> List[ActivityLog]:
        """Fetches activity history filtered by associate ID or global system history."""
        query = db.query(ActivityLog)
        if associate_id:
            query = query.filter(ActivityLog.associate_id == associate_id)
        return query.order_by(ActivityLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def log_activity(
        db: Session,
        action: str,
        description: str,
        associate_id: Optional[int] = None,
        performed_by: str = "Onboarding Admin"
    ) -> ActivityLog:
        """Records a new audit log entry in the database."""
        log = ActivityLog(
            associate_id=associate_id,
            action=action,
            description=description,
            performed_by=performed_by
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
