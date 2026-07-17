import os
import pyodbc

SQLSERVER_CONN = os.environ.get(
    "SQLSERVER_CONN",
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-5JM3GSQ\\SQLEXPRESS;"
    "DATABASE=MedIntelligence;Trusted_Connection=yes;Encrypt=no"
)

def clean_database():
    conn = pyodbc.connect(SQLSERVER_CONN, autocommit=True)
    cursor = conn.cursor()
    
    tables_to_clean = [
        "dbo.invoices",
        "dbo.prescriptions",
        "dbo.diagnoses",
        "dbo.visit_tests",
        "dbo.visit_symptoms",
        "dbo.visit_vitals",
        "dbo.emergency_visits",
        "dbo.appointments",
        "dbo.patient_documents",
        "dbo.notifications",
        "dbo.audit_log"
    ]
    
    for table in tables_to_clean:
        print(f"Cleaning {table}...")
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"Cleaned {table}. Rows affected: {cursor.rowcount}")
        except Exception as e:
            print(f"Error cleaning {table}: {e}")
            
    cursor.close()
    conn.close()
    print("Database cleaned successfully!")

if __name__ == "__main__":
    clean_database()
