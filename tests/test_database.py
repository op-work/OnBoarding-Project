import unittest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Associate, OnboardingRecord, ActivityLog
from database import seed_demo_data, recalculate_associate_progress
from services.associate_service import AssociateService

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # In-memory SQLite DB for isolated unit testing
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()

    def tearDown(self):
        self.db.close()

    def test_seed_demo_data(self):
        """Tests that demo data seeds 5 associates and onboarding records with valid states."""
        seed_demo_data(self.db)

        assoc_count = self.db.query(Associate).count()
        self.assertEqual(assoc_count, 5)

        records = self.db.query(OnboardingRecord).all()
        self.assertEqual(len(records), 5)

        # Verify Virtual vs In-person work mode distribution
        online = self.db.query(Associate).filter(Associate.work_mode.in_(["Virtual", "Online"])).all()
        offline = self.db.query(Associate).filter(Associate.work_mode.in_(["In-person", "Offline"])).all()
        self.assertGreater(len(online), 0)
        self.assertGreater(len(offline), 0)

        # Check Rahul Sharma (Completed 100%)
        rahul = self.db.query(Associate).filter(Associate.first_name == "Rahul").first()
        self.assertIsNotNone(rahul)
        self.assertEqual(rahul.onboarding_record.overall_progress, 100.0)
        self.assertEqual(rahul.onboarding_record.overall_status, "Completed")
        self.assertEqual(rahul.status, "Completed")

    def test_create_and_delete_associate(self):
        """Tests creating an associate and deleting with cascade deletion."""
        data = {
            "first_name": "Test",
            "last_name": "Joiner",
            "personal_email": "test.joiner@example.com",
            "phone": "+91 9999999999",
            "designation": "QA Engineer",
            "department": "Engineering",
            "date_of_joining": datetime.date.today(),
            "location": "Pune",
            "reporting_manager": "Manager Name",
            "work_mode": "Online",
            "asset_shipment_address": "Test Address, Pune"
        }

        assoc = AssociateService.create_associate(self.db, data)
        self.assertIsNotNone(assoc.id)
        self.assertEqual(assoc.status, "Not Started")
        self.assertIsNotNone(assoc.onboarding_record)
        self.assertEqual(assoc.onboarding_record.overall_progress, 0.0)

        # Test cascading deletion
        assoc_id = assoc.id
        deleted = AssociateService.delete_associate(self.db, assoc_id)
        self.assertTrue(deleted)

        rec = self.db.query(OnboardingRecord).filter(OnboardingRecord.associate_id == assoc_id).first()
        self.assertIsNone(rec)

if __name__ == "__main__":
    unittest.main()
