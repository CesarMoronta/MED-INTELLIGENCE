import os
import pyodbc
from dotenv import load_dotenv

load_dotenv(override=True)

conn_str = os.environ.get("SQLSERVER_CONN")
print("Connecting to:", conn_str)
conn = pyodbc.connect(conn_str, autocommit=True)
cursor = conn.cursor()

# Query to list all user tables
cursor.execute("""
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = 'dbo'
    ORDER BY TABLE_NAME
""")
tables = [row[0] for row in cursor.fetchall()]

for table in tables:
    print(f"\nTable: {table}")
    cursor.execute(f"""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
    """, table)
    for col in cursor.fetchall():
        name, dtype, max_len, is_nullable, default = col
        char_len = f"({max_len})" if max_len else ""
        if max_len == -1:
            char_len = "(MAX)"
        null_str = "NULL" if is_nullable == "YES" else "NOT NULL"
        def_str = f" DEFAULT {default}" if default else ""
        print(f"  - {name} {dtype}{char_len} {null_str}{def_str}")

cursor.close()
conn.close()
