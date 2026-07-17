import pyodbc
import os

conn_str = os.environ.get('SQLSERVER_CONN', r'DRIVER={ODBC Driver 18 for SQL Server};SERVER=.\SQLEXPRESS;DATABASE=MedIntelligence;Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes')
conn = pyodbc.connect(conn_str, autocommit=True)
cursor = conn.cursor()

stmts = [
    "ALTER TABLE dbo.patients ADD vital_status NVARCHAR(20) NOT NULL DEFAULT 'Vivo'",
    "ALTER TABLE dbo.patients ADD death_date DATE NULL",
    "ALTER TABLE dbo.patients ADD death_certificate_url NVARCHAR(MAX) NULL",
    "ALTER TABLE dbo.patients ADD death_notes NVARCHAR(MAX) NULL",
    "ALTER TABLE dbo.patients ADD CONSTRAINT CK_patients_vital_status CHECK (vital_status IN ('Vivo', 'Fallecido'))",
    "ALTER TABLE dbo.invoices ADD amount_paid DECIMAL(10,2) NOT NULL DEFAULT 0",
    "ALTER TABLE dbo.invoices ADD balance_due DECIMAL(10,2) NOT NULL DEFAULT 0",
    "ALTER TABLE dbo.invoices ADD due_date DATE NULL",
    "UPDATE dbo.invoices SET amount_paid = total, balance_due = 0 WHERE invoice_type != 'nota_credito'"
]

for s in stmts:
    try:
        cursor.execute(s)
        print('Executed:', s)
    except Exception as e:
        print('Skipped (already exists or error):', e)

# Now recreate the views and SPs:
views_and_sps = """
DROP VIEW IF EXISTS dbo.vw_patients;
GO
CREATE VIEW dbo.vw_patients AS
SELECT
    p.id, p.cedula, p.name, p.dob, p.gender, p.phone, p.blood_type, p.registered_by, p.created_at, p.updated_at, p.photo_url,
    p.vital_status, p.death_date, p.death_certificate_url, p.death_notes,
    DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END AS age,
    (SELECT pa.antecedent, pa.value FROM dbo.patient_antecedents pa WHERE pa.patient_id = p.id FOR JSON PATH) AS antecedentes
FROM dbo.patients p;
GO
IF OBJECT_ID(N'dbo.sp_create_patient', N'P') IS NOT NULL DROP PROCEDURE dbo.sp_create_patient;
GO
CREATE PROCEDURE dbo.sp_create_patient
    @cedula NVARCHAR(50), @name NVARCHAR(200), @dob DATE, @gender NVARCHAR(20), @phone NVARCHAR(30) = NULL,
    @blood_type NVARCHAR(5) = NULL, @registered_by INT = NULL, @photo_url NVARCHAR(MAX) = NULL,
    @vital_status NVARCHAR(20) = 'Vivo', @death_date DATE = NULL, @death_certificate_url NVARCHAR(MAX) = NULL, @death_notes NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.patients (cedula, name, dob, gender, phone, blood_type, registered_by, photo_url, vital_status, death_date, death_certificate_url, death_notes)
    VALUES (@cedula, @name, @dob, @gender, @phone, @blood_type, @registered_by, @photo_url, @vital_status, @death_date, @death_certificate_url, @death_notes);
    SELECT SCOPE_IDENTITY() AS patient_id;
END
GO
IF OBJECT_ID(N'dbo.sp_update_patient', N'P') IS NOT NULL DROP PROCEDURE dbo.sp_update_patient;
GO
CREATE PROCEDURE dbo.sp_update_patient
    @patient_id INT, @cedula NVARCHAR(50) = NULL, @name NVARCHAR(200) = NULL, @dob DATE = NULL, @gender NVARCHAR(20) = NULL,
    @phone NVARCHAR(30) = NULL, @blood_type NVARCHAR(5) = NULL, @photo_url NVARCHAR(MAX) = NULL,
    @vital_status NVARCHAR(20) = NULL, @death_date DATE = NULL, @death_certificate_url NVARCHAR(MAX) = NULL, @death_notes NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE dbo.patients
    SET cedula = COALESCE(@cedula, cedula), name = COALESCE(@name, name), dob = COALESCE(@dob, dob), gender = COALESCE(@gender, gender),
        phone = COALESCE(@phone, phone), blood_type = COALESCE(@blood_type, blood_type), photo_url = COALESCE(@photo_url, photo_url),
        vital_status = COALESCE(@vital_status, vital_status), death_date = COALESCE(@death_date, death_date),
        death_certificate_url = COALESCE(@death_certificate_url, death_certificate_url), death_notes = COALESCE(@death_notes, death_notes),
        updated_at = SYSUTCDATETIME()
    WHERE id = @patient_id;
    SELECT @@ROWCOUNT AS rows_affected;
END
"""

import re
batches = re.split(r'\nGO\b', views_and_sps, flags=re.IGNORECASE)
for b in batches:
    if b.strip():
        cursor.execute(b.strip())
print("Vistas y SPs actualizados.")
