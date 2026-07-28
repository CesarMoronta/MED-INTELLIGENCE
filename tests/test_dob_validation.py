import unittest
import re
from datetime import datetime

def calculate_age(dob_dt: datetime) -> int:
    today = datetime.now()
    return today.year - dob_dt.year - ((today.month, today.day) < (dob_dt.month, dob_dt.day))

def is_valid_dob(dob_str: str, min_age: int = 16) -> bool:
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", dob_str):
        return False
    try:
        dob_dt = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.now()
        if dob_dt > today or dob_dt.year < 1900:
            return False
        return calculate_age(dob_dt) >= min_age
    except ValueError:
        return False

class DOBValidationTests(unittest.TestCase):
    def test_invalid_dates(self):
        self.assertFalse(is_valid_dob("1977-02-32"))
        self.assertFalse(is_valid_dob("2021-02-29"))  # 2021 is not leap year
        self.assertFalse(is_valid_dob("invalid-date"))
        self.assertFalse(is_valid_dob("1899-12-31"))

    def test_underage_patients(self):
        today = datetime.now()
        recent_year = today.year - 10
        underage_dob = f"{recent_year}-05-15"
        self.assertFalse(is_valid_dob(underage_dob, min_age=16))

    def test_valid_dates(self):
        self.assertTrue(is_valid_dob("1977-02-15"))
        self.assertTrue(is_valid_dob("2000-02-29"))  # 2000 is leap year
        self.assertTrue(is_valid_dob("1990-05-15"))

if __name__ == "__main__":
    unittest.main()
