import sys
import codecs
import random

# Force UTF-8 stdout
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from database import get_connection

def fill_data():
    conn = get_connection()
    cursor = conn.cursor()

    print("=== RELLENANDO DATOS FALTANTES EN LA BASE DE DATOS ===")

    # 1. Pacientes
    print("\n1. Verificando y rellenando datos de Pacientes (patients)...")
    cursor.execute("SELECT id, name, cedula, phone, blood_type FROM dbo.patients")
    patients = cursor.fetchall()
    
    blood_types = ["O+", "O-", "A+", "A-", "B+", "AB+"]
    patient_updated_count = 0

    for p in patients:
        pid, name, cedula, phone, btype = p
        updates = []
        params = []
        
        # Cédula faltante o vacía (generar 11 dígitos aleatorios que no existan)
        if not cedula or not cedula.strip() or len(cedula.strip()) < 11:
            dummy_ced = f"402{random.randint(1000000, 9999999)}"
            updates.append("cedula = ?")
            params.append(dummy_ced)
            print(f"   - Paciente '{name}' (ID {pid}): Rellenando Cédula con '{dummy_ced}'")

        # Teléfono faltante
        if not phone or not phone.strip():
            dummy_phone = f"809-555-{random.randint(1000, 9999)}"
            updates.append("phone = ?")
            params.append(dummy_phone)
            print(f"   - Paciente '{name}' (ID {pid}): Rellenando Teléfono con '{dummy_phone}'")

        # Tipo de sangre faltante
        if not btype or not btype.strip():
            dummy_btype = random.choice(blood_types)
            updates.append("blood_type = ?")
            params.append(dummy_btype)
            print(f"   - Paciente '{name}' (ID {pid}): Rellenando Tipo de Sangre con '{dummy_btype}'")

        if updates:
            params.append(pid)
            cursor.execute(f"UPDATE dbo.patients SET {', '.join(updates)} WHERE id = ?", *params)
            patient_updated_count += 1

    print(f"✅ Se actualizaron datos faltantes de {patient_updated_count} pacientes.")

    # 2. Doctores
    print("\n2. Verificando y rellenando datos de Doctores (doctors)...")
    cursor.execute("""
        SELECT d.id, u.username, d.matricula, d.especialidad, d.telefono, d.hospital 
        FROM dbo.doctors d
        INNER JOIN dbo.users u ON d.user_id = u.id
    """)
    doctors = cursor.fetchall()
    
    especialidades = ["Cardiología", "Neurología", "Medicina Interna", "Pediatría", "Ginecología", "Medicina General"]
    hospitales = ["Clínica Corominas", "Hospital Metropolitano de Santiago (HOMS)", "Centro Médico UCE", "Hospital Plaza de la Salud"]
    doctor_updated_count = 0

    for doc in doctors:
        did, username, matricula, especialidad, phone, hospital = doc
        updates = []
        params = []

        if not matricula or not matricula.strip():
            dummy_mat = f"DR-{random.randint(10000, 99999)}"
            updates.append("matricula = ?")
            params.append(dummy_mat)
            print(f"   - Doctor '{username}' (ID {did}): Rellenando Matrícula con '{dummy_mat}'")

        if not especialidad or not especialidad.strip():
            dummy_esp = random.choice(especialidades)
            updates.append("especialidad = ?")
            params.append(dummy_esp)
            print(f"   - Doctor '{username}' (ID {did}): Rellenando Especialidad con '{dummy_esp}'")

        if not phone or not phone.strip():
            dummy_phone = f"809-555-{random.randint(1000, 9999)}"
            updates.append("telefono = ?")
            params.append(dummy_phone)
            print(f"   - Doctor '{username}' (ID {did}): Rellenando Teléfono con '{dummy_phone}'")

        if not hospital or not hospital.strip():
            dummy_hosp = random.choice(hospitales)
            updates.append("hospital = ?")
            params.append(dummy_hosp)
            print(f"   - Doctor '{username}' (ID {did}): Rellenando Hospital con '{dummy_hosp}'")

        if updates:
            params.append(did)
            cursor.execute(f"UPDATE dbo.doctors SET {', '.join(updates)} WHERE id = ?", *params)
            doctor_updated_count += 1

    print(f"✅ Se actualizaron datos faltantes de {doctor_updated_count} doctores.")

    cursor.close()
    conn.close()
    print("\n🏁 Proceso de autorelleno completado con éxito.")

if __name__ == "__main__":
    fill_data()
