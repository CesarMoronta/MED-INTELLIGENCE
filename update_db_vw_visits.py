import os
import sys
import pyodbc

# Forzar la codificación estándar (necesario en Windows)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from database import get_connection

def apply_migration():
    print("🔗 Conectando a la base de datos para actualizar la vista vw_visits...")
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("1. Modificando vista dbo.vw_visits...")
        cursor.execute("""
            ALTER VIEW dbo.vw_visits AS
            SELECT
                ev.id,
                ev.visit_type,
                ev.motivo_consulta,
                ev.motivo_emergencia,
                ev.doctor_notes,
                ev.visit_date,
                ev.status,
                ev.created_at,
                -- Paciente
                p.id            AS patient_id,
                p.cedula        AS patient_cedula,
                p.name          AS patient_name,
                p.dob           AS patient_dob,
                p.gender        AS patient_gender,
                -- Doctor
                u.id            AS doctor_id,
                u.username      AS doctor_username,
                u.full_name     AS doctor_fullname,
                -- Diagnóstico más reciente de la visita
                d.id            AS diagnosis_id,
                d.phase         AS diagnosis_phase,
                d.diagnosis_primary,
                d.probability   AS diagnosis_probability,
                d.alert_level,
                d.alert_color,
                d.specialist,
                -- Cita y Seguimiento
                ev.appointment_id,
                a.parent_appointment_id
            FROM dbo.emergency_visits ev
            INNER JOIN dbo.patients p ON ev.patient_id = p.id
            INNER JOIN dbo.users    u ON ev.doctor_id  = u.id
            LEFT JOIN dbo.appointments a ON ev.appointment_id = a.id
            LEFT JOIN (
                SELECT visit_id, id, phase, diagnosis_primary, probability, alert_level, alert_color, specialist,
                       ROW_NUMBER() OVER (PARTITION BY visit_id ORDER BY id DESC) AS rn
                FROM dbo.diagnoses
            ) d ON d.visit_id = ev.id AND d.rn = 1;
        """)
        print("✅ Vista dbo.vw_visits actualizada exitosamente.")

        conn.commit()
        cursor.close()
        conn.close()
        print("\n🚀 ¡Migración de vista aplicada con éxito!")

    except Exception as e:
        print(f"❌ Error al ejecutar la migración de la vista: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_migration()
