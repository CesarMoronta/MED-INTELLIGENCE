import os
import pyodbc
from dotenv import load_dotenv

load_dotenv(override=True)

# Connection configurations
local_conn_str = os.environ.get("SQLSERVER_CONN")
remote_conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=35.223.196.136,1433;DATABASE=MedIntelligence;UID=sa;PWD=Admin123;Encrypt=no"

print("Connecting to local database...")
try:
    local_conn = pyodbc.connect(local_conn_str, autocommit=True)
    print("[OK] Connected to local database.")
except Exception as e:
    print("[ERROR] Failed to connect to local database:", e)
    exit(1)

print("Connecting to remote database at 35.223.196.136...")
try:
    remote_conn = pyodbc.connect(remote_conn_str, autocommit=True)
    print("[OK] Connected to remote database.")
except Exception as e:
    print("[ERROR] Failed to connect to remote database:", e)
    local_conn.close()
    exit(1)

local_cursor = local_conn.cursor()
remote_cursor = remote_conn.cursor()

# Order of tables to migrate (dependencies first to avoid issues, though we can disable constraints too)
# Let's list tables in order
tables = [
    "users",
    "doctors",
    "patients",
    "patient_antecedents",
    "appointments",
    "emergency_visits",
    "visit_symptoms",
    "visit_tests",
    "visit_vitals",
    "diagnoses",
    "invoices",
    "patient_billing_info",
    "prescriptions",
    "system_config",
    "login_attempts",
    "model_conditionals",
    "model_priors",
    "notifications",
    "patient_documents"
]

# Step 1: Temporarily disable constraints on the remote DB
print("\n[STEP 1] Disabling foreign key constraints on remote database...")
try:
    remote_cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'")
    print("[OK] Constraints disabled.")
except Exception as e:
    print("[WARNING] Could not disable all constraints via sp_MSforeachtable, continuing anyway:", e)

# Step 2: Migrate data for each table
print("\n[STEP 2] Migrating table records...")
for table in tables:
    print(f"Migrating table: {table}...")
    
    # Check if table has identity column
    remote_cursor.execute(f"SELECT OBJECTPROPERTY(OBJECT_ID('dbo.{table}'), 'TableHasIdentity')")
    row = remote_cursor.fetchone()
    has_identity = row and row[0] == 1
    
    # Get columns
    local_cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}' ORDER BY ORDINAL_POSITION")
    columns = [r[0] for r in local_cursor.fetchall()]
    
    if not columns:
        print(f"  (Notice): No columns found for table {table}. Skipping.")
        continue
    
    col_list = ", ".join(columns)
    val_placeholders = ", ".join(["?"] * len(columns))
    
    # Get rows from local
    local_cursor.execute(f"SELECT {col_list} FROM dbo.{table}")
    rows = local_cursor.fetchall()
    
    print(f"  Found {len(rows)} records locally.")
    if not rows:
        continue
    
    # Truncate remote table first to avoid duplicate primary keys
    try:
        remote_cursor.execute(f"DELETE FROM dbo.{table}")
    except Exception as e:
        print(f"  [ERROR] Failed to clear remote table {table}: {e}")
        continue
        
    # Enable identity insert if table has identity column
    if has_identity:
        try:
            remote_cursor.execute(f"SET IDENTITY_INSERT dbo.{table} ON")
        except Exception as e:
            print(f"  [WARNING] Failed to enable IDENTITY_INSERT for {table}: {e}")
            has_identity = False  # Reset flag if command failed
            
    # Insert rows into remote
    insert_query = f"INSERT INTO dbo.{table} ({col_list}) VALUES ({val_placeholders})"
    success_count = 0
    for r in rows:
        try:
            # Convert row values to list
            vals = list(r)
            remote_cursor.execute(insert_query, *vals)
            success_count += 1
        except Exception as e:
            print(f"  [ERROR] Failed to insert row into {table}: {e}")
            
    print(f"  Successfully migrated {success_count}/{len(rows)} records.")
    
    # Disable identity insert
    if has_identity:
        try:
            remote_cursor.execute(f"SET IDENTITY_INSERT dbo.{table} OFF")
        except Exception as e:
            print(f"  [WARNING] Failed to disable IDENTITY_INSERT for {table}: {e}")

# Step 3: Re-enable foreign key constraints on the remote DB
print("\n[STEP 3] Re-enabling foreign key constraints on remote database...")
try:
    remote_cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL'")
    print("[OK] Constraints re-enabled.")
except Exception as e:
    print("[WARNING] Could not re-enable all constraints via sp_MSforeachtable:", e)

print("\n🎉 Migration complete!")
local_cursor.close()
local_conn.close()
remote_cursor.close()
remote_conn.close()
