import os
import sys

# Agregar el directorio raíz al path para poder importar database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from database import get_connection
    print("Conectando a la base de datos...")
    conn = get_connection()
    cursor = conn.cursor()
    
    print("Iniciando eliminación de consultas y datos relacionados...")
    
    # 1. Eliminar facturas
    print("- Eliminando facturas (dbo.invoices)...")
    cursor.execute("DELETE FROM dbo.invoices;")
    
    # 2. Eliminar recetas
    print("- Eliminando recetas (dbo.prescriptions)...")
    cursor.execute("DELETE FROM dbo.prescriptions;")
    
    # 3. Eliminar diagnósticos
    print("- Eliminando diagnósticos (dbo.diagnoses)...")
    cursor.execute("DELETE FROM dbo.diagnoses;")
    
    # 4. Eliminar detalles de visitas
    print("- Eliminando síntomas de visitas (dbo.visit_symptoms)...")
    cursor.execute("DELETE FROM dbo.visit_symptoms;")
    
    print("- Eliminando signos vitales de visitas (dbo.visit_vitals)...")
    cursor.execute("DELETE FROM dbo.visit_vitals;")
    
    print("- Eliminando pruebas de visitas (dbo.visit_tests)...")
    cursor.execute("DELETE FROM dbo.visit_tests;")
    
    # 5. Eliminar visitas de emergencia / consultas
    print("- Eliminando consultas (dbo.emergency_visits)...")
    cursor.execute("DELETE FROM dbo.emergency_visits;")
    
    conn.commit()
    print("¡Base de datos limpiada con éxito! Se conservaron los pacientes, doctores y usuarios.")
    
except Exception as e:
    print(f"Error al limpiar la base de datos: {e}")
    sys.exit(1)
finally:
    try:
        cursor.close()
        conn.close()
    except NameError:
        pass
