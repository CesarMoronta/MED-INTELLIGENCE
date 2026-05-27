import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=ASUS_GAMING_CM;DATABASE=MedIntelligence;Trusted_Connection=yes;Encrypt=no', autocommit=True)
cursor = conn.cursor()
cursor.execute("SELECT is_identity FROM sys.columns WHERE object_id = OBJECT_ID('appointments') AND name = 'id'")
rows = cursor.fetchall()
for r in rows:
    print("is_identity:", r)

