import os
import sys
import pyodbc
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv(override=True)

conn_str = os.environ.get("SQLSERVER_CONN")
conn = pyodbc.connect(conn_str, autocommit=True)
cursor = conn.cursor()

try:
    cursor.execute("SELECT VIEW_DEFINITION FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_NAME = 'vw_reports_waiting_time'")
    row = cursor.fetchone()
    if row and row[0]:
        print("--- VIEW DEFINITION ---")
        print(row[0])
    else:
        # Try sp_helptext
        cursor.execute("EXEC sp_helptext 'dbo.vw_reports_waiting_time'")
        lines = [r[0] for r in cursor.fetchall()]
        print("--- VIEW DEFINITION ---")
        print("".join(lines))
except Exception as e:
    print("Error:", e)

cursor.close()
conn.close()
