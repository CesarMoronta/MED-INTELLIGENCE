import pyodbc
import os

conn_str = os.environ.get('SQLSERVER_CONN', r'DRIVER={ODBC Driver 18 for SQL Server};SERVER=.\SQLEXPRESS;DATABASE=MedIntelligence;Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes')
conn = pyodbc.connect(conn_str, autocommit=True)
cursor = conn.cursor()

print("=== COLUMNAS EN dbo.patients ===")
cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, COLUMN_DEFAULT, IS_NULLABLE 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'patients' 
    AND COLUMN_NAME IN ('vital_status','death_date','death_certificate_url','death_notes')
    ORDER BY COLUMN_NAME
""")
for r in cursor.fetchall():
    print(r)

print("\n=== COLUMNAS EN dbo.invoices ===")
cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, COLUMN_DEFAULT, IS_NULLABLE 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'invoices' 
    AND COLUMN_NAME IN ('amount_paid','balance_due','due_date')
    ORDER BY COLUMN_NAME
""")
for r in cursor.fetchall():
    print(r)

print("\n=== CONSTRAINT CHECK EN patients ===")
cursor.execute("""
    SELECT cc.CONSTRAINT_NAME, cc.CHECK_CLAUSE
    FROM INFORMATION_SCHEMA.CHECK_CONSTRAINTS cc
    JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE cu ON cc.CONSTRAINT_NAME = cu.CONSTRAINT_NAME
    WHERE cu.TABLE_NAME = 'patients' AND cu.COLUMN_NAME = 'vital_status'
""")
for r in cursor.fetchall():
    print(r)

print("\n=== VISTA vw_patients - COLUMNAS ===")
cursor.execute("""
    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'vw_patients'
    ORDER BY ORDINAL_POSITION
""")
for r in cursor.fetchall():
    print(r[0], end="  ")
print()

print("\n=== STORED PROC sp_update_patient - parametros ===")
cursor.execute("""
    SELECT PARAMETER_NAME, DATA_TYPE, PARAMETER_MODE
    FROM INFORMATION_SCHEMA.PARAMETERS
    WHERE SPECIFIC_NAME = 'sp_update_patient'
    ORDER BY ORDINAL_POSITION
""")
for r in cursor.fetchall():
    print(r)

conn.close()
print("\n=== OK ===")
