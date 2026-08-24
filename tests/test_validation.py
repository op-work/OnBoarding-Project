import unittest
import datetime
from utils.validation import validate_email, validate_phone, validate_associate_form

class TestValidation(unittest.TestCase):
    def test_email_validation(self):
        self.assertTrue(validate_email("john.doe@company.com"))
        self.assertTrue(validate_email("user.name+tag@domain.co.in"))
        self.assertFalse(validate_email("invalid_email"))
        self.assertFalse(validate_email(""))
        self.assertFalse(validate_email(None))

    def test_phone_validation(self):
        self.assertTrue(validate_phone("+91 9876543210"))
        self.assertTrue(validate_phone("9876543210"))
        self.assertTrue(validate_phone("+1 (555) 019-2834"))
        self.assertFalse(validate_phone("123"))
        self.assertFalse(validate_phone(""))

    def test_associate_form_validation(self):
        valid_data = {
            "first_name": "Rohan",
            "last_name": "Kulkarni",
            "personal_email": "rohan@example.com",
            "phone": "+91 9123456789",
            "designation": "Software Engineer",
            "department": "Engineering",
            "location": "Pune",
            "reporting_manager": "Manager Name",
            "date_of_joining": datetime.date.today(),
            "work_mode": "Online",
            "asset_shipment_address": "Pune Maharashtra 411001"
        }
        is_valid, errors = validate_associate_form(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Online mode missing shipment address
        invalid_online = valid_data.copy()
        invalid_online["asset_shipment_address"] = ""
        is_valid, errors = validate_associate_form(invalid_online)
        self.assertFalse(is_valid)
        self.assertIn("asset_shipment_address", errors)

        # Offline mode without shipment address should be valid
        valid_offline = valid_data.copy()
        valid_offline["work_mode"] = "Offline"
        valid_offline["asset_shipment_address"] = ""
        is_valid, errors = validate_associate_form(valid_offline)
        self.assertTrue(is_valid)

if __name__ == "__main__":
    unittest.main()
