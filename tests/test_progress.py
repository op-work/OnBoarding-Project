import unittest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Associate, OnboardingRecord, OnboardingTask
from database import recalculate_associate_progress
from services.task_service import TaskService
from services.progress_service import ProgressService

class TestProgress(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()

    def tearDown(self):
        self.db.close()

    def test_progress_calculation(self):
        assoc = Associate(
            first_name="Test",
            last_name="User",
            personal_email="test@user.com",
            phone="+91 9999999999",
            designation="Tester",
            department="Engineering",
            date_of_joining=datetime.date.today(),
            location="Remote",
            reporting_manager="Manager",
            employee_id="EMP-TEST-001",
            work_mode="Online",
            status="Not Started"
        )
        self.db.add(assoc)
        self.db.commit()

        rec = OnboardingRecord(associate_id=assoc.id, overall_status="Not Started", overall_progress=0.0)
        self.db.add(rec)
        self.db.commit()

        # Add 4 tasks (3 applicable, 1 non-applicable)
        t1 = OnboardingTask(associate_id=assoc.id, stage="Pre-Onboarding", section="Sec 1", title="Task 1", is_applicable=True, status="Not Started")
        t2 = OnboardingTask(associate_id=assoc.id, stage="Pre-Onboarding", section="Sec 1", title="Task 2", is_applicable=True, status="Not Started")
        t3 = OnboardingTask(associate_id=assoc.id, stage="Onboarding Day", section="Sec 1", title="Task 3", is_applicable=True, status="Not Started")
        t4 = OnboardingTask(associate_id=assoc.id, stage="Pre-Onboarding", section="Sec 1", title="Non-Applicable Task", is_applicable=False, status="Not Started")

        self.db.add_all([t1, t2, t3, t4])
        self.db.commit()

        # Recalculate - 0/3 = 0%
        pct, status = recalculate_associate_progress(self.db, assoc.id)
        self.assertEqual(pct, 0.0)
        self.assertEqual(status, "Not Started")

        # Mark 1 task completed -> 1/3 = 33.3%
        TaskService.toggle_task_completion(self.db, t1.id, True)
        pct, status = recalculate_associate_progress(self.db, assoc.id)
        self.assertEqual(pct, 33.3)
        self.assertEqual(status, "In Progress")

        # Mark all 3 applicable completed -> 3/3 = 100%
        TaskService.toggle_task_completion(self.db, t2.id, True)
        TaskService.toggle_task_completion(self.db, t3.id, True)
        pct, status = recalculate_associate_progress(self.db, assoc.id)
        self.assertEqual(pct, 100.0)
        self.assertEqual(status, "Completed")

if __name__ == "__main__":
    unittest.main()
