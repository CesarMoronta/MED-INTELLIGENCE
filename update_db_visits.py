import os
import sys
import pyodbc

# Forzar la codificación estándar (necesario en Windows)
if getattr(sys.stdout, 'encoding', None) and sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from database import get_connection

def apply_migration():
    print("🔗 Conectando a la base de datos para vincular consultas con citas...")
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("1. Modificando tabla dbo.emergency_visits...")
        try:
            cursor.execute("""
                ALTER TABLE dbo.emergency_visits 
                ADD appointment_id INT NULL;
            """)
            print("✅ Columna appointment_id agregada.")
        except pyodbc.ProgrammingError as e:
            if "already exists" in str(e) or "42S21" in str(e):
                print("⚠️ La columna appointment_id ya existe.")
            else:
                print(f"❌ Error al alterar la tabla: {e}")

        try:
            cursor.execute("""
                ALTER TABLE dbo.emergency_visits
                ADD CONSTRAINT FK_emergency_visits_appointment 
                FOREIGN KEY (appointment_id) REFERENCES dbo.appointments(id);
            """)
            print("✅ Restricción de llave foránea FK_emergency_visits_appointment agregada.")
        except pyodbc.ProgrammingError as e:
            if "already exists" in str(e) or "already a FOREIGN KEY" in str(e) or "42000" in str(e):
                print("⚠️ La restricción de llave foránea ya existe.")
            else:
                print(f"❌ Error al agregar restricción: {e}")

        print("2. Modificando procedimiento sp_create_visit...")
        cursor.execute("""
            ALTER PROCEDURE dbo.sp_create_visit
                @patient_id         INT,
                @doctor_id          INT,
                @visit_type         NVARCHAR(20),
                @motivo_consulta    NVARCHAR(MAX) = NULL,
                @motivo_emergencia  NVARCHAR(MAX) = NULL,
                @doctor_notes       NVARCHAR(MAX) = NULL,
                @appointment_id     INT = NULL
            AS
            BEGIN
                SET NOCOUNT ON;
                INSERT INTO dbo.emergency_visits (patient_id, doctor_id, visit_type, motivo_consulta, motivo_emergencia, doctor_notes, appointment_id)
                VALUES (@patient_id, @doctor_id, @visit_type, @motivo_consulta, @motivo_emergencia, @doctor_notes, @appointment_id);
                SELECT SCOPE_IDENTITY() AS visit_id;
            END;
        """)
        print("✅ Procedimiento sp_create_visit actualizado.")

        conn.commit()
        cursor.close()
        conn.close()
        print("\n🚀 ¡Migración aplicada con éxito!")

    except Exception as e:
        print(f"❌ Error general en la migración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_migration()
