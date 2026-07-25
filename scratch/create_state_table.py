import pyodbc

conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=35.223.196.136,1433;DATABASE=MedIntelligence;UID=sa;PWD=Admin123;Encrypt=no"

try:
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT 1 FROM sys.tables WHERE name = 'telegram_bot_states'")
    exists = cursor.fetchone()
    
    if not exists:
        print("Creating table dbo.telegram_bot_states...")
        cursor.execute("""
            CREATE TABLE dbo.telegram_bot_states (
                chat_id BIGINT PRIMARY KEY,
                state NVARCHAR(50) NOT NULL,
                user_data NVARCHAR(MAX) NULL,
                updated_at DATETIME DEFAULT GETDATE()
            )
        """)
        print("[OK] Table created successfully.")
    else:
        print("[OK] Table already exists.")
        
    cursor.close()
    conn.close()
except Exception as e:
    print("[ERROR] Failed:", e)
