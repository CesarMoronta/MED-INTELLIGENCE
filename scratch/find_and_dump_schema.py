import pyodbc
import sys

servers = [
    "LATRD-PF4PV5FT\\SQLEXPRESS",
    "LATRD-PF4PV5FT",
    "localhost\\SQLEXPRESS",
    "localhost",
    "127.0.0.1\\SQLEXPRESS",
    "127.0.0.1"
]

conn = None
connected_server = None

for server in servers:
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=MedIntelligence;Trusted_Connection=yes;Encrypt=no"
    print(f"Trying connection to {server}...")
    try:
        conn = pyodbc.connect(conn_str, timeout=3, autocommit=True)
        connected_server = server
        print(f"🎉 Connected successfully to {server}!")
        break
    except Exception as e:
        print(f"  Failed: {e}")

if not conn:
    print("❌ Could not connect to any SQL Server instance.")
    sys.exit(1)

cursor = conn.cursor()

# Get all tables
cursor.execute("""
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = 'dbo'
    ORDER BY TABLE_NAME
""")
tables = [row[0] for row in cursor.fetchall()]

# We'll build the updated database_schema.txt contents dynamically based on the current tables in their database.
# But wait! SQL Server can generate the exact DDL if we query sys tables.
# Let's write a simple generator for the table definitions to match database_schema.txt format.

# For this request, let's write out all table columns so we can compare and replace database_schema.txt
print("\n--- SCHEMA DUMP ---")
for table in tables:
    print(f"Table: {table}")
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
