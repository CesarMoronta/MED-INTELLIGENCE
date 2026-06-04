import os
import sys
import pyodbc

# Forzar la codificación estándar (necesario en Windows)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from database import get_connection

def apply_updates():
    print(f"🔗 Conectando a la base de datos...")
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("1. Modificando tabla dbo.diagnoses...")
        try:
            cursor.execute("""
                ALTER TABLE dbo.diagnoses 
                ADD is_refuted BIT NOT NULL DEFAULT 0,
                    refutation_reason NVARCHAR(MAX) NULL,
                    doctor_override_diagnosis NVARCHAR(200) NULL;
            """)
            print("✅ Columnas agregadas a dbo.diagnoses.")
        except pyodbc.ProgrammingError as e:
            if "already exists" in str(e) or "42S21" in str(e):
                print("⚠️ Las columnas en dbo.diagnoses ya existen.")
            else:
                print(f"❌ Error al alterar dbo.diagnoses: {e}")

        print("2. Modificando tabla dbo.appointments...")
        try:
            cursor.execute("""
                ALTER TABLE dbo.appointments
                ADD parent_appointment_id INT NULL 
                CONSTRAINT FK_appointments_parent FOREIGN KEY REFERENCES dbo.appointments(id);
            """)
            print("✅ Columna parent_appointment_id agregada a dbo.appointments.")
        except pyodbc.ProgrammingError as e:
            if "already exists" in str(e) or "42S21" in str(e):
                print("⚠️ La columna parent_appointment_id ya existe en dbo.appointments.")
            else:
                print(f"❌ Error al alterar dbo.appointments: {e}")

        print("3. Modificando procedimiento sp_save_diagnosis...")
        cursor.execute("""
            ALTER PROCEDURE dbo.sp_save_diagnosis
                @visit_id INT,
                @phase NVARCHAR(20),
                @diagnosis_primary NVARCHAR(200),
                @probability FLOAT,
                @alert_level NVARCHAR(20),
                @alert_color NVARCHAR(10),
                @specialist NVARCHAR(200),
                @differentials_json NVARCHAR(MAX) = NULL,
                @clinical_report NVARCHAR(MAX) = NULL,
                @is_refuted BIT = 0,
                @refutation_reason NVARCHAR(MAX) = NULL,
                @doctor_override_diagnosis NVARCHAR(200) = NULL
            AS
            BEGIN
                SET NOCOUNT ON;

                -- Insertar nuevo diagnóstico
                INSERT INTO dbo.diagnoses (
                    visit_id, phase, diagnosis_primary, probability, alert_level, 
                    alert_color, specialist, differentials_json, clinical_report,
                    is_refuted, refutation_reason, doctor_override_diagnosis
                )
                VALUES (
                    @visit_id, @phase, @diagnosis_primary, @probability, @alert_level, 
                    @alert_color, @specialist, @differentials_json, @clinical_report,
                    @is_refuted, @refutation_reason, @doctor_override_diagnosis
                );

                -- Retornar el ID insertado
                SELECT SCOPE_IDENTITY() AS new_diag_id;
            END;
        """)
        print("✅ Procedimiento sp_save_diagnosis actualizado exitosamente.")

        print("4. Actualizando vw_appointments...")
        cursor.execute("""
            ALTER VIEW dbo.vw_appointments AS
            SELECT 
                a.id, a.patient_id, a.doctor_id, a.scheduled_date, a.scheduled_time,
                a.status, a.notes, a.confirmed, a.parent_appointment_id,
                p.name AS patient_name, p.cedula AS patient_cedula, p.gender AS patient_gender,
                u.full_name AS doctor_fullname, u.username AS doctor_username
            FROM dbo.appointments a
            JOIN dbo.patients p ON a.patient_id = p.id
            JOIN dbo.users u ON a.doctor_id = u.id;
        """)
        print("✅ Vista vw_appointments actualizada exitosamente.")


        cursor.close()
        conn.close()
        print("\n🚀 ¡Base de datos actualizada a la versión 3.1!")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_updates()
