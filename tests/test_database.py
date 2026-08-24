import unittest
import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Associate, OnboardingRecord, OnboardingTask, Document
from database import seed_demo_data, recalculate_associate_progress

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # In-memory SQLite DB for testing
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()

    def tearDown(self):
        self.db.close()

    def test_seed_data_creation(self):
        seed_demo_data(self.db)
        assoc_count = self.db.query(Associate).count()
        self.assertEqual(assoc_count, 5)

        records = self.db.query(OnboardingRecord).all()
        self.assertEqual(len(records), 5)

        # Check online vs offline joiners exist
        online = self.db.query(Associate).filter(Associate.work_mode == "Online").all()
        offline = self.db.query(Associate).filter(Associate.work_mode == "Offline").all()
        self.assertGreater(len(online), 0)
        self.assertGreater(len(offline), 0)

    def test_task_applicability(self):
        seed_demo_data(self.db)
        offline_assoc = self.db.query(Associate).filter(Associate.work_mode == "Offline").first()
        offline_tasks = self.db.query(OnboardingTask).filter(OnboardingTask.associate_id == offline_assoc.id).all()

        non_applicable = [t for t in offline_tasks if not t.is_applicable]
        self.assertGreater(len(non_applicable), 0)

        # Shipment tasks should be non-applicable for offline joiners
        for t in non_applicable:
            self.assertTrue("shipment" in t.title.lower() or "address" in t.title.lower())

if __name__ == "__main__":
    unittest.main()
