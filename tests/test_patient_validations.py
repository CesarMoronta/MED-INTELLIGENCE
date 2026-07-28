import unittest
import re
from utils import format_cedula

def validate_cedula_and_name(raw_cedula: str, name: str):
    cedula_digits = re.sub(r"\D", "", raw_cedula or "")
    if len(cedula_digits) != 11:
        return False, "La cédula debe contener exactamente 11 dígitos numéricos."
    
    clean_name = (name or "").strip().upper()
    if not clean_name:
        return False, "El nombre completo del paciente es requerido."
    
    formatted_cedula = format_cedula(cedula_digits)
    return True, {"cedula": formatted_cedula, "cedula_digits": cedula_digits, "name": clean_name}


class PatientValidationTests(unittest.TestCase):
    def test_valid_cedula_formatting(self):
        valid, result = validate_cedula_and_name("001-1234567-8", "juan perez")
        self.assertTrue(valid)
        self.assertEqual(result["cedula_digits"], "00112345678")
        self.assertEqual(result["name"], "JUAN PEREZ")
        self.assertEqual(result["cedula"], "001-1234567-8")

    def test_valid_cedula_raw_digits(self):
        valid, result = validate_cedula_and_name("03100012345", "pedro alcantara")
        self.assertTrue(valid)
        self.assertEqual(result["cedula_digits"], "03100012345")
        self.assertEqual(result["cedula"], "031-0001234-5")

    def test_invalid_cedula_length(self):
        valid, err = validate_cedula_and_name("12345", "maria gomez")
        self.assertFalse(valid)
        self.assertIn("11 dígitos", err)

    def test_empty_patient_name(self):
        valid, err = validate_cedula_and_name("001-1234567-8", "   ")
        self.assertFalse(valid)
        self.assertIn("requerido", err)


if __name__ == "__main__":
    unittest.main()
