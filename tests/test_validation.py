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
            "name_as_per_aadhar": "Rohan Kulkarni",
            "personal_email": "rohan@example.com",
            "date_of_joining": datetime.date.today(),
            "is_fresher": False,
            "last_working_day": datetime.date.today(),
            "designation": "Software Engineer",
            "location": "Pune",
            "work_mode": "Virtual",
            "asset_shipment_address": "Pune Maharashtra 411001"
        }
        is_valid, errors = validate_associate_form(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Virtual mode missing shipment address
        invalid_virtual = valid_data.copy()
        invalid_virtual["asset_shipment_address"] = ""
        is_valid, errors = validate_associate_form(invalid_virtual)
        self.assertFalse(is_valid)
        self.assertIn("asset_shipment_address", errors)

        # In-person mode without shipment address should be valid
        valid_inperson = valid_data.copy()
        valid_inperson["work_mode"] = "In-person"
        valid_inperson["asset_shipment_address"] = ""
        is_valid, errors = validate_associate_form(valid_inperson)
        self.assertTrue(is_valid)

        # Non-fresher missing last working day should be invalid
        invalid_experienced = valid_data.copy()
        invalid_experienced["is_fresher"] = False
        invalid_experienced["last_working_day"] = None
        is_valid, errors = validate_associate_form(invalid_experienced)
        self.assertFalse(is_valid)
        self.assertIn("last_working_day", errors)

        # Fresher missing last working day should be valid
        valid_fresher = valid_data.copy()
        valid_fresher["is_fresher"] = True
        valid_fresher["last_working_day"] = None
        is_valid, errors = validate_associate_form(valid_fresher)
        self.assertTrue(is_valid)

if __name__ == "__main__":
    unittest.main()
