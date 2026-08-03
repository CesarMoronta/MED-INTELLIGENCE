import os
import sys
import pyodbc
from dotenv import load_dotenv
import re

if getattr(sys.stdout, 'encoding', None) and sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv(override=True)

conn_str = os.environ.get("SQLSERVER_CONN")
conn = pyodbc.connect(conn_str, autocommit=True)
cursor = conn.cursor()

# Get all columns from SQL Server database
cursor.execute("""
    SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'dbo'
    ORDER BY TABLE_NAME, ORDINAL_POSITION
""")
db_schema = {}
for row in cursor.fetchall():
    table, col, dtype, max_len, is_null = row
    t_lower = table.lower()
    if t_lower not in db_schema:
        db_schema[t_lower] = {}
    db_schema[t_lower][col.lower()] = (dtype.lower(), max_len, is_null)

# Read database_schema.txt
with open("database_schema.txt", "r", encoding="utf-8") as f:
    sql_content = f.read()

# We will normalize spacing in sql_content to help us find columns in CREATE TABLE blocks.
# Let's find CREATE TABLE blocks
create_blocks = re.findall(r"CREATE\s+TABLE\s+dbo\.(\w+)\s*\((.*?)\)\s*;", sql_content, re.DOTALL | re.IGNORECASE)
if not create_blocks:
    # Maybe without ending semicolon or wrapped in IF block?
    # Let's match: CREATE TABLE dbo.tablename ( ... ) ending with ); or ) and next GO
    create_blocks = re.findall(r"CREATE\s+TABLE\s+dbo\.(\w+)\s*\((.*?)\n\s*\)", sql_content, re.DOTALL | re.IGNORECASE)

sql_schema = {}
for table_name, body in create_blocks:
    t_lower = table_name.lower()
    sql_schema[t_lower] = set()
    # Extract words at start of line inside body
    lines = body.split("\n")
    for line in lines:
        line = line.strip()
        if not line or line.startswith("--") or line.startswith("CONSTRAINT") or line.startswith("PRIMARY KEY") or line.startswith("FOREIGN KEY"):
            continue
        m = re.match(r"^(\w+)\s+", line)
        if m:
            sql_schema[t_lower].add(m.group(1).lower())

print("Differences found:")
for db_table, db_cols in db_schema.items():
    if db_table in sql_schema:
        sql_cols = sql_schema[db_table]
        missing_in_sql = set(db_cols.keys()) - sql_cols
        if missing_in_sql:
            print(f"Table {db_table} has columns in DB but missing in SQL text: {list(missing_in_sql)}")
    else:
        print(f"Table {db_table} is in DB but not detected in SQL text (might be parsed incorrectly).")

cursor.close()
conn.close()
