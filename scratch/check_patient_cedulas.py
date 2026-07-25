import os
import pyodbc
from dotenv import load_dotenv

load_dotenv(override=True)

conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=35.223.196.136,1433;DATABASE=MedIntelligence;UID=sa;PWD=Admin123;Encrypt=no"
conn = pyodbc.connect(conn_str, autocommit=True)
cursor = conn.cursor()

cursor.execute("SELECT id, name, cedula FROM dbo.patients")
for r in cursor.fetchall():
    print(f"ID: {r[0]} | Name: {r[1]} | Cedula in DB: '{r[2]}'")

cursor.close()
conn.close()
