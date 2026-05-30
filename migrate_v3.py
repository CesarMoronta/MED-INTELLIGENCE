"""migrate_v3.py — Ejecuta las migraciones de base de datos para MED-INTELLIGENCE PRO v3.0"""
from database import get_connection

def run():
    conn = get_connection()
    cur  = conn.cursor()
    results = []

    # 1. Columnas confirmed/confirm_notes en appointments
    try:
        cur.execute("""
            IF NOT EXISTS (
                SELECT 1 FROM sys.columns
                WHERE object_id = OBJECT_ID('dbo.appointments') AND name = 'confirmed'
            )
            BEGIN
                ALTER TABLE dbo.appointments ADD
                    confirmed     BIT           NOT NULL DEFAULT 0,
                    confirm_notes NVARCHAR(500) NULL
            END
        """)
        results.append("appointments.confirmed: OK")
    except Exception as e:
        results.append(f"appointments error: {e}")

    # 2. Tabla patient_documents
    try:
        cur.execute("""
            IF OBJECT_ID(N'dbo.patient_documents', N'U') IS NULL
            BEGIN
                CREATE TABLE dbo.patient_documents (
                    id            INT IDENTITY(1,1) NOT NULL,
                    patient_id    INT               NOT NULL,
                    filename      NVARCHAR(300)     NOT NULL,
                    original_name NVARCHAR(300)     NOT NULL,
                    file_type     NVARCHAR(20)      NOT NULL,
                    file_size     INT               NOT NULL DEFAULT 0,
                    file_path     NVARCHAR(500)     NOT NULL,
                    uploaded_by   INT               NULL,
                    uploaded_at   DATETIME2         NOT NULL DEFAULT SYSUTCDATETIME(),
                    CONSTRAINT PK_patient_documents PRIMARY KEY (id),
                    CONSTRAINT FK_patdocs_patient FOREIGN KEY (patient_id)
                        REFERENCES dbo.patients(id) ON DELETE CASCADE,
                    CONSTRAINT FK_patdocs_user FOREIGN KEY (uploaded_by)
                        REFERENCES dbo.users(id) ON DELETE SET NULL
                )
                CREATE INDEX IX_patient_docs ON dbo.patient_documents (patient_id, uploaded_at DESC)
            END
        """)
        results.append("patient_documents: OK")
    except Exception as e:
        results.append(f"patient_documents error: {e}")

    # 3. Tabla notifications
    try:
        cur.execute("""
            IF OBJECT_ID(N'dbo.notifications', N'U') IS NULL
            BEGIN
                CREATE TABLE dbo.notifications (
                    id           INT IDENTITY(1,1) NOT NULL,
                    from_user_id INT               NOT NULL,
                    to_user_id   INT               NOT NULL,
                    message      NVARCHAR(MAX)     NOT NULL,
                    type         NVARCHAR(20)      NOT NULL DEFAULT 'message',
                    is_read      BIT               NOT NULL DEFAULT 0,
                    created_at   DATETIME2         NOT NULL DEFAULT SYSUTCDATETIME(),
                    CONSTRAINT PK_notifications     PRIMARY KEY (id),
                    CONSTRAINT CK_notif_type        CHECK (type IN ('message','alert','info')),
                    CONSTRAINT FK_notif_from        FOREIGN KEY (from_user_id) REFERENCES dbo.users(id),
                    CONSTRAINT FK_notif_to          FOREIGN KEY (to_user_id)   REFERENCES dbo.users(id)
                )
                CREATE INDEX IX_notif_to   ON dbo.notifications (to_user_id, created_at DESC)
                CREATE INDEX IX_notif_unrd ON dbo.notifications (to_user_id, is_read, created_at DESC)
            END
        """)
        results.append("notifications: OK")
    except Exception as e:
        results.append(f"notifications error: {e}")

    # 4. Settings adicionales del consultorio
    try:
        extra = [
            ('clinic_address', ''), ('clinic_phone', ''), ('clinic_rnc', ''),
            ('clinic_hours', ''),   ('clinic_email', '')
        ]
        for key, val in extra:
            cur.execute(
                "IF NOT EXISTS (SELECT 1 FROM dbo.system_config WHERE key_name=?) "
                "INSERT INTO dbo.system_config (key_name, key_value) VALUES (?,?)",
                key, key, val
            )
        results.append("settings keys: OK")
    except Exception as e:
        results.append(f"settings error: {e}")

    cur.close()
    conn.close()

    for r in results:
        print(r)
    print("Migraciones v3.0 completadas.")

if __name__ == "__main__":
    run()
