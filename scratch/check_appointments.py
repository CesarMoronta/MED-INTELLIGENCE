import pyodbc

conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=35.223.196.136,1433;DATABASE=MedIntelligence;UID=sa;PWD=Admin123;Encrypt=no"
conn = pyodbc.connect(conn_str, autocommit=True)
cursor = conn.cursor()

cursor.execute("""
    SELECT a.id, p.name, a.scheduled_date, a.scheduled_time, a.status 
    FROM dbo.appointments a
    JOIN dbo.patients p ON a.patient_id = p.id
""")
for r in cursor.fetchall():
    print(f"ID: {r[0]} | Patient: {r[1]} | Date: {r[2]} | Time: {r[3]} | Status: '{r[4]}'")

cursor.close()
conn.close()
