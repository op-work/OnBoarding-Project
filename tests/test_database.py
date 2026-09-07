import unittest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Associate, OnboardingRecord, ActivityLog
from database import engine, recalculate_associate_progress
from services.associate_service import AssociateService

class TestDatabase(unittest.TestCase):
    def setUp(self):
        try:
            with engine.connect() as conn:
                pass
        except Exception as e:
            self.skipTest(f"Azure PostgreSQL database is not reachable ({e}). Configure valid DB credentials in .env.")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        self.db = Session()

    def tearDown(self):
        if hasattr(self, "db"):
            self.db.rollback()
            self.db.close()

    def test_associate_creation_and_recalculation(self):
        """Tests that creating an associate and onboarding record correctly calculates progress."""
        data = {
            "first_name": "Dynamic",
            "last_name": "Employee",
            "personal_email": "dynamic.emp@example.com",
            "phone": "+91 9876543210",
            "designation": "Software Engineer",
            "department": "Engineering",
            "date_of_joining": datetime.date.today(),
            "location": "Pune",
            "reporting_manager": "Tech Lead",
            "work_mode": "Virtual",
            "employee_id": "EMP-TEST-DYN-01"
        }
        assoc = AssociateService.create_associate(self.db, data)
        self.assertIsNotNone(assoc)
        self.assertEqual(assoc.first_name, "Dynamic")
        self.assertEqual(assoc.onboarding_record.overall_progress, 0.0)

        # Cleanup
        AssociateService.delete_associate(self.db, assoc.id)

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
