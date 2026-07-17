import sys
sys.path.append('.')
import pyodbc
from database import SQLSERVER_CONN

conn = pyodbc.connect(SQLSERVER_CONN)
cursor = conn.cursor()
cursor.execute("SELECT key_name, key_value FROM dbo.system_config WHERE key_name LIKE 'sidebar_order%'")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")
cursor.close()
conn.close()
