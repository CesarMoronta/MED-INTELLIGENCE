import sys
import codecs

# Force UTF-8 stdout
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from database import get_connection

def inspect():
    conn = get_connection()
    cursor = conn.cursor()

    print("=== VISITAS DE TIPO 'CONSULTA' EN LA BASE DE DATOS ===")
    cursor.execute("""
        SELECT 
            ev.id AS visit_id,
            ev.visit_date,
            ev.status AS visit_status,
            p.name AS patient_name,
            ev.appointment_id,
            app.parent_appointment_id,
            (SELECT COUNT(1) FROM dbo.diagnoses d WHERE d.visit_id = ev.id AND d.phase = 'final') AS has_final_diag,
            (SELECT COUNT(1) FROM dbo.invoices i WHERE i.visit_id = ev.id) AS has_invoice
        FROM dbo.emergency_visits ev
        INNER JOIN dbo.patients p ON ev.patient_id = p.id
        LEFT JOIN dbo.appointments app ON ev.appointment_id = app.id
        WHERE ev.visit_type = 'consulta'
        ORDER BY ev.visit_date DESC
    """)
    
    rows = cursor.fetchall()
    
    if not rows:
        print("No se encontraron consultas en la base de datos.")
        cursor.close()
        conn.close()
        return

    print(f"{'ID':<5} | {'Fecha':<20} | {'Paciente':<25} | {'Estado':<8} | {'Cita ID':<8} | {'Seguimiento':<12} | {'Diag. Final':<11} | {'Facturado':<9}")
    print("-" * 115)
    
    pending_to_close = []
    
    for r in rows:
        vid, vdate, vstatus, pname, app_id, parent_id, has_final, has_inv = r
        is_followup = "Sí" if parent_id is not None else "No"
        has_final_str = "Sí" if has_final > 0 else "No"
        has_inv_str = "Sí" if has_inv > 0 else "No"
        
        # Guardar para auto-cerrar si tiene diagnóstico final pero sigue abierta
        if vstatus == 'abierta' and has_final > 0:
            pending_to_close.append(vid)

        print(f"{vid:<5} | {str(vdate)[:19]:<20} | {pname[:25]:<25} | {vstatus:<8} | {str(app_id) if app_id else 'Ninguna':<8} | {is_followup:<12} | {has_final_str:<11} | {has_inv_str:<9}")

    if pending_to_close:
        print(f"\n⚠️ Se encontraron {len(pending_to_close)} consultas abiertas con diagnóstico final guardado. Corrigiendo estado a 'cerrada'...")
        for vid in pending_to_close:
            cursor.execute("UPDATE dbo.emergency_visits SET status = 'cerrada' WHERE id = ?", vid)
        print("✅ Estado corregido exitosamente.")
    else:
        print("\n✅ Todas las consultas con diagnóstico final están correctamente marcadas como 'cerrada'.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    inspect()
