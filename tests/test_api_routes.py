import unittest
from unittest.mock import patch, MagicMock
import sys

# Patch pyodbc before app import so ODBC connection attempt never blocks/times out
mock_pyodbc = MagicMock()
sys.modules["pyodbc"] = mock_pyodbc

from app import app


class APIRouteAuthTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_patients_unauthorized(self):
        response = self.client.get("/api/patients")
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertFalse(data.get("success"))

    def test_appointments_unauthorized(self):
        response = self.client.get("/api/appointments")
        self.assertEqual(response.status_code, 401)

    def test_billing_invoices_unauthorized(self):
        response = self.client.get("/api/billing/invoices")
        self.assertEqual(response.status_code, 401)

    def test_reports_doctor_list_unauthorized(self):
        response = self.client.get("/api/reports/doctor-list")
        self.assertEqual(response.status_code, 401)

    def test_doctor_cannot_create_patient(self):
        with self.client.session_transaction() as sess:
            sess["user"] = {"id": 2, "role": "doctor", "username": "dr_smith"}
        
        response = self.client.post("/api/patients", json={
            "cedula": "001-1234567-8",
            "name": "Paciente Prueba"
        })
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("error"), "Permiso denegado.")

    @patch("routes.patients.list_patients")
    def test_authenticated_admin_gets_patients(self, mock_list_patients):
        mock_list_patients.return_value = [{"id": 1, "name": "JUAN PEREZ", "cedula": "001-1234567-8"}]
        with self.client.session_transaction() as sess:
            sess["user"] = {"id": 1, "role": "admin", "username": "admin"}

        response = self.client.get("/api/patients")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(len(data.get("patients")), 1)


if __name__ == "__main__":
    unittest.main()
