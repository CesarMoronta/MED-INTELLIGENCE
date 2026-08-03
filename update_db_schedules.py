from database import get_connection

def apply_migration():
    print("Starting schedules and availability database migration...")
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Crear tabla dbo.clinic_working_hours
    cursor.execute("""
    IF OBJECT_ID(N'dbo.clinic_working_hours', N'U') IS NULL
    BEGIN
        CREATE TABLE dbo.clinic_working_hours (
            day_of_week INT NOT NULL, -- 1=Monday, ..., 7=Sunday
            start_time  TIME NOT NULL,
            end_time    TIME NOT NULL,
            is_active   BIT NOT NULL DEFAULT 1,
            CONSTRAINT PK_clinic_working_hours PRIMARY KEY (day_of_week),
            CONSTRAINT CK_clinic_working_hours_day CHECK (day_of_week BETWEEN 1 AND 7)
        );
    END
    """)
    conn.commit()

    # 2. Poblar valores por defecto para la clínica si está vacía
    cursor.execute("SELECT COUNT(1) FROM dbo.clinic_working_hours")
    count = cursor.fetchone()[0]
    if count == 0:
        defaults = [
            (1, '08:00:00', '18:00:00', 1), # Lunes
            (2, '08:00:00', '18:00:00', 1), # Martes
            (3, '08:00:00', '18:00:00', 1), # Miércoles
            (4, '08:00:00', '18:00:00', 1), # Jueves
            (5, '08:00:00', '18:00:00', 1), # Viernes
            (6, '08:00:00', '12:00:00', 1), # Sábado
            (7, '08:00:00', '18:00:00', 0), # Domingo (Inactivo)
        ]
        for row in defaults:
            cursor.execute(
                "INSERT INTO dbo.clinic_working_hours (day_of_week, start_time, end_time, is_active) VALUES (?, ?, ?, ?)",
                row[0], row[1], row[2], row[3]
            )
        conn.commit()

    # 3. Crear tabla dbo.doctor_blocked_slots
    cursor.execute("""
    IF OBJECT_ID(N'dbo.doctor_blocked_slots', N'U') IS NULL
    BEGIN
        CREATE TABLE dbo.doctor_blocked_slots (
            id           INT IDENTITY(1,1) NOT NULL,
            doctor_id    INT NOT NULL,
            blocked_date DATE NOT NULL,
            start_time   TIME NOT NULL,
            end_time     TIME NOT NULL,
            reason       NVARCHAR(255) NULL,
            created_at   DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
            CONSTRAINT PK_doctor_blocked_slots PRIMARY KEY (id),
            CONSTRAINT FK_doctor_blocked_slots_users FOREIGN KEY (doctor_id)
                REFERENCES dbo.users(id) ON DELETE CASCADE
        );
    END
    """)
    conn.commit()
    
    cursor.close()
    conn.close()
    print("Database schedules migration completed successfully.")
