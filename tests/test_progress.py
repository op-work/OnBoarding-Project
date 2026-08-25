import unittest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Associate, OnboardingRecord
from database import recalculate_associate_progress
from services.progress_service import ProgressService
from services.associate_service import AssociateService

class TestProgress(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()

    def tearDown(self):
        self.db.close()

    def test_progress_calculation_all_combinations(self):
        """Tests progress and status calculations across all stage combinations and completion thresholds."""
        assoc = Associate(
            first_name="Jane",
            last_name="Doe",
            personal_email="jane.doe@example.com",
            phone="+91 9876543210",
            designation="Full Stack Developer",
            department="Engineering",
            date_of_joining=datetime.date.today(),
            location="Pune",
            reporting_manager="Tech Lead",
            employee_id="EMP-TEST-101",
            work_mode="Online",
            status="Not Started"
        )
        self.db.add(assoc)
        self.db.commit()

        rec = OnboardingRecord(associate_id=assoc.id, overall_status="Not Started", overall_progress=0.0)
        self.db.add(rec)
        self.db.commit()

        # 1. Initial State: 0 / 17 items verified
        pct, status = recalculate_associate_progress(self.db, assoc.id)
        self.assertEqual(pct, 0.0)
        self.assertEqual(status, "Not Started")
        self.assertEqual(rec.current_stage, "Pre-Onboarding")
        self.assertIsNone(rec.completed_at)

        # 2. Partial Pre-Onboarding: 3 / 6 items verified (3/17 total = 17.6%)
        rec.pre_info_received = True
        rec.pre_connect_joiner = True
        rec.pre_it_tickets_status = "Raised"
        pct, status = recalculate_associate_progress(self.db, assoc.id)
        self.assertEqual(pct, 17.6)
        self.assertEqual(status, "In Progress")
        self.assertEqual(rec.pre_onboarding_status, "In Progress")
        self.assertEqual(rec.current_stage, "Pre-Onboarding")

        # 3. Complete Pre-Onboarding: 6 / 6 items verified (6/17 total = 35.3%)
        rec.pre_notify_stakeholders = True
        rec.pre_prepare_schedule = True
        rec.pre_share_schedule = True
        pct, status = recalculate_associate_progress(self.db, assoc.id)
        self.assertEqual(pct, 35.3)
        self.assertEqual(status, "In Progress")
        self.assertEqual(rec.pre_onboarding_status, "Completed")
        self.assertEqual(rec.current_stage, "Onboarding Day")

        # 4. Complete Onboarding Day: 4 / 4 items verified (10/17 total = 58.8%)
        rec.day1_mandatory_forms = True
        rec.day1_employment_docs = True
        rec.day1_hr_induction = True
        rec.day1_announce_joiner = True
        pct, status = recalculate_associate_progress(self.db, assoc.id)
        self.assertEqual(pct, 58.8)
        self.assertEqual(status, "In Progress")
        self.assertEqual(rec.day1_orientation_status, "Completed")
        self.assertEqual(rec.current_stage, "Post-Onboarding")

        # 5. Partial Post-Onboarding: 4 / 7 items verified (14/17 total = 82.4%)
        rec.post_id_card_status = "Raised"
        rec.post_hrms_doc_status = "Approved"
        rec.post_feedback_1week = True
        rec.post_insurance_pf = True
        pct, status = recalculate_associate_progress(self.db, assoc.id)
        self.assertEqual(pct, 82.4)
        self.assertEqual(status, "In Progress")
        self.assertEqual(rec.post_onboarding_status, "In Progress")
        self.assertEqual(rec.current_stage, "Post-Onboarding")

        # 6. Complete ALL Stages & Checklists: 17 / 17 items verified (100.0%)
        rec.post_feedback_30days = True
        rec.post_feedback_60days = True
        rec.post_feedback_90days = True
        pct, status = recalculate_associate_progress(self.db, assoc.id)

        # MUST BE 100% COMPLETE AND STATUS "Completed"
        self.assertEqual(pct, 100.0)
        self.assertEqual(status, "Completed")
        self.assertEqual(rec.overall_status, "Completed")
        self.assertEqual(assoc.status, "Completed")
        self.assertEqual(rec.post_onboarding_status, "Completed")
        self.assertEqual(rec.current_stage, "Post-Onboarding")
        self.assertIsNotNone(rec.completed_at)
        self.assertEqual(rec.it_equipment_status, "Delivered")
        self.assertEqual(rec.bgv_status, "Verified")
        self.assertEqual(rec.probation_status, "Confirmed")

        # 7. Test ProgressService overall progress helper
        overall = ProgressService.get_overall_progress(self.db, assoc.id)
        self.assertEqual(overall["progress_pct"], 100.0)
        self.assertEqual(overall["overall_status"], "Completed")
        self.assertEqual(overall["stages"]["Pre-Onboarding"]["progress_pct"], 100.0)
        self.assertEqual(overall["stages"]["Onboarding Day"]["progress_pct"], 100.0)
        self.assertEqual(overall["stages"]["Post-Onboarding"]["progress_pct"], 100.0)

    def test_out_of_order_and_toggling_items(self):
        """Tests toggling items off and performing out-of-order stage updates."""
        data = {
            "first_name": "Out",
            "last_name": "OfOrder",
            "personal_email": "ooo@example.com",
            "phone": "+91 9111111111",
            "designation": "Data Scientist",
            "department": "Data",
            "date_of_joining": datetime.date.today(),
            "location": "Bengaluru",
            "reporting_manager": "Data Lead",
            "work_mode": "Offline"
        }
        assoc = AssociateService.create_associate(self.db, data)
        rec = assoc.onboarding_record

        # Check all 7 Post-Onboarding items without checking Pre-Onboarding (7/17 items = 41.2%)
        rec.post_id_card_status = "Raised"
        rec.post_hrms_doc_status = "Approved"
        rec.post_feedback_1week = True
        rec.post_insurance_pf = True
        rec.post_feedback_30days = True
        rec.post_feedback_60days = True
        rec.post_feedback_90days = True

        pct, status = recalculate_associate_progress(self.db, assoc.id)
        self.assertEqual(pct, 41.2)
        self.assertEqual(status, "In Progress")
        self.assertEqual(rec.post_onboarding_status, "Completed")
        self.assertEqual(rec.current_stage, "Pre-Onboarding") # Pre-Onboarding still needs completion

        # Uncheck items
        rec.post_feedback_90days = False
        pct, status = recalculate_associate_progress(self.db, assoc.id)
        self.assertEqual(pct, 35.3) # 6/17 items
        self.assertEqual(rec.post_onboarding_status, "In Progress")

    def test_draft_associate_progress(self):
        """Tests draft associate creation and status behavior."""
        data = {
            "first_name": "Draft",
            "last_name": "Candidate",
            "personal_email": "draft@example.com",
            "phone": "+91 9222222222",
            "designation": "Intern",
            "department": "Human Resources",
            "date_of_joining": datetime.date.today(),
            "location": "Mumbai",
            "reporting_manager": "HR Lead",
            "work_mode": "Online"
        }
        assoc = AssociateService.create_associate(self.db, data, is_draft=True)
        self.assertEqual(assoc.status, "Draft")
        self.assertEqual(assoc.onboarding_record.overall_progress, 0.0)

if __name__ == "__main__":
    unittest.main()
