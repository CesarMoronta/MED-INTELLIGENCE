import os
import re
import pyodbc

# Target connection details
server = "35.223.196.136"
user = "sa"
password = "Admin123"

conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},1433;DATABASE=master;UID={user};PWD={password};Encrypt=no"
print("Connecting to master database at:", server)

try:
    conn = pyodbc.connect(conn_str, autocommit=True)
    print("[SUCCESS] Connected successfully!")
except Exception as e:
    print("[ERROR] Failed to connect:", e)
    print("Please double check the firewall rule and if the password is correct.")
    exit(1)

cursor = conn.cursor()

# Read the database_schema.txt file
schema_path = "database_schema.txt"
with open(schema_path, "r", encoding="utf-8") as f:
    schema_sql = f.read()

# Since database_schema.txt starts with DB creation, let's split the commands by GO batches
# GO must be on its own line
batches = re.split(r"^\s*GO\s*$", schema_sql, flags=re.MULTILINE | re.IGNORECASE)

print(f"Executing {len(batches)} SQL batches to initialize database schema...")

for idx, batch in enumerate(batches):
    batch = batch.strip()
    if not batch:
        continue
    
    # Print a tiny preview
    preview = batch[:60].replace("\n", " ") + "..."
    print(f"[{idx+1}/{len(batches)}] Executing: {preview}")
    
    try:
        cursor.execute(batch)
    except Exception as e:
        # Ignore database creation errors if database already exists, or print warnings
        if "already exists" in str(e) or "database context to 'MedIntelligence'" in str(e):
            print(f"  (Notice): {e}")
        else:
            print(f"  [ERROR] Error in batch {idx+1}: {e}")

print("[OK] Schema initialization complete!")
cursor.close()
conn.close()
