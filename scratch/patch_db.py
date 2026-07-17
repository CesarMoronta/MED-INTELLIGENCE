import re

with open('database.py', 'r', encoding='utf-8') as f:
    db_code = f.read()

# 1. Update get_patient
get_patient_old = """    cursor.execute(
        "SELECT id, cedula, name, dob, gender, phone, blood_type, age, antecedentes, created_at, updated_at, photo_url "
        "FROM dbo.vw_patients WHERE id = ?",
        patient_id
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    patient = {
        "id": row[0], "cedula": row[1], "name": row[2],
        "dob": _fmt_date(row[3]), "gender": row[4],
        "phone": row[5], "blood_type": row[6], "age": row[7],
        "antecedentes": {}, "created_at": _fmt_date(row[9]),
        "updated_at": _fmt_date(row[10]), "photo_url": row[11]
    }"""
get_patient_new = """    cursor.execute(
        "SELECT id, cedula, name, dob, gender, phone, blood_type, age, antecedentes, created_at, updated_at, photo_url, vital_status, death_date, death_certificate_url, death_notes "
        "FROM dbo.vw_patients WHERE id = ?",
        patient_id
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    patient = {
        "id": row[0], "cedula": row[1], "name": row[2],
        "dob": _fmt_date(row[3]), "gender": row[4],
        "phone": row[5], "blood_type": row[6], "age": row[7],
        "antecedentes": {}, "created_at": _fmt_date(row[9]),
        "updated_at": _fmt_date(row[10]), "photo_url": row[11],
        "vital_status": row[12], "death_date": _fmt_date(row[13]),
        "death_certificate_url": row[14], "death_notes": row[15]
    }"""
db_code = db_code.replace(get_patient_old, get_patient_new)

# 2. Update list_patients
list_patients_old = """    base_query = "SELECT p.id, p.cedula, p.name, p.dob, p.gender, p.phone, p.blood_type, p.age, p.antecedentes, p.photo_url FROM dbo.vw_patients p" """
list_patients_new = """    base_query = "SELECT p.id, p.cedula, p.name, p.dob, p.gender, p.phone, p.blood_type, p.age, p.antecedentes, p.photo_url, p.vital_status FROM dbo.vw_patients p" """
db_code = db_code.replace(list_patients_old, list_patients_new)

# 3. Add mark_patient_deceased
add_mark_patient_deceased = """
def mark_patient_deceased(patient_id: int, death_date: str, cert_path: str, notes: str, doctor_id: int, doctor_username: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE dbo.patients SET vital_status = 'Fallecido', death_date = ?, death_certificate_url = ?, death_notes = ?, updated_at = SYSUTCDATETIME() WHERE id = ?",
            death_date, cert_path, notes, patient_id
        )
        if cursor.rowcount > 0:
            cursor.execute(
                "INSERT INTO dbo.audit_log (username, action, entity, entity_id, details, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                doctor_username, 'MARCAR_FALLECIDO', 'Patient', str(patient_id), f"Fallecimiento registrado: {death_date}", doctor_id
            )
            return True
        return False
    except Exception as e:
        print(f"Error marking patient deceased: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
"""
if "mark_patient_deceased" not in db_code:
    db_code += add_mark_patient_deceased

# 4. Update create_invoice
create_invoice_old = """def create_invoice(visit_id: int | None, user_id: int | None, invoice_type: str,
                   amount: float, itbis: float, total: float, payment_method: str,
                   ecf_id: str | None, encf: str | None, estado: str, track_id: str | None,
                   codigo_seguridad: str | None, dgii_url: str | None, xml_url: str | None,
                   tipo_ecf: str | None = None) -> int | None:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(\"\"\"
            INSERT INTO dbo.invoices (visit_id, user_id, invoice_type, amount, itbis, total,
                                      payment_method, ecf_id, encf, estado, track_id,
                                      codigo_seguridad, dgii_url, xml_url, tipo_ecf)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", visit_id, user_id, invoice_type, amount, itbis, total,
             payment_method, ecf_id, encf, estado, track_id,
             codigo_seguridad, dgii_url, xml_url, tipo_ecf)"""
create_invoice_new = """def create_invoice(visit_id: int | None, user_id: int | None, invoice_type: str,
                   amount: float, itbis: float, total: float, payment_method: str,
                   ecf_id: str | None, encf: str | None, estado: str, track_id: str | None,
                   codigo_seguridad: str | None, dgii_url: str | None, xml_url: str | None,
                   tipo_ecf: str | None = None, amount_paid: float = None, balance_due: float = None, due_date: str = None) -> int | None:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if amount_paid is None:
            amount_paid = total
        if balance_due is None:
            balance_due = 0.0
            
        cursor.execute(\"\"\"
            INSERT INTO dbo.invoices (visit_id, user_id, invoice_type, amount, itbis, total,
                                      payment_method, ecf_id, encf, estado, track_id,
                                      codigo_seguridad, dgii_url, xml_url, tipo_ecf, amount_paid, balance_due, due_date)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", visit_id, user_id, invoice_type, amount, itbis, total,
             payment_method, ecf_id, encf, estado, track_id,
             codigo_seguridad, dgii_url, xml_url, tipo_ecf, amount_paid, balance_due, due_date)"""
db_code = db_code.replace(create_invoice_old, create_invoice_new)

# 5. Update list_invoices
list_invoices_old = """        SELECT i.id, i.visit_id, i.user_id, i.invoice_type, i.amount, i.itbis, i.total,
               i.payment_method, i.ecf_id, i.encf, i.estado, i.track_id, i.codigo_seguridad,
               i.dgii_url, i.xml_url, i.created_at, i.tipo_ecf,
               p.name AS patient_name, p.cedula AS patient_cedula, p.id AS patient_id,"""
list_invoices_new = """        SELECT i.id, i.visit_id, i.user_id, i.invoice_type, i.amount, i.itbis, i.total,
               i.payment_method, i.ecf_id, i.encf, i.estado, i.track_id, i.codigo_seguridad,
               i.dgii_url, i.xml_url, i.created_at, i.tipo_ecf, i.amount_paid, i.balance_due, i.due_date,
               p.name AS patient_name, p.cedula AS patient_cedula, p.id AS patient_id,"""
db_code = db_code.replace(list_invoices_old, list_invoices_new)

list_invoices_old2 = """    for r in rows:
        r["created_at"] = _fmt_date(r.get("created_at"))
        r["amount"] = float(r["amount"])
        r["itbis"] = float(r["itbis"])
        r["total"] = float(r["total"])
        r["is_cancelled"] = bool(r.get("is_cancelled", 0))"""
list_invoices_new2 = """    for r in rows:
        r["created_at"] = _fmt_date(r.get("created_at"))
        r["amount"] = float(r["amount"])
        r["itbis"] = float(r["itbis"])
        r["total"] = float(r["total"])
        r["amount_paid"] = float(r["amount_paid"]) if r.get("amount_paid") is not None else 0.0
        r["balance_due"] = float(r["balance_due"]) if r.get("balance_due") is not None else 0.0
        r["due_date"] = _fmt_date(r.get("due_date"))
        r["is_cancelled"] = bool(r.get("is_cancelled", 0))"""
db_code = db_code.replace(list_invoices_old2, list_invoices_new2)

# 6. Update get_invoice_by_id
get_invoice_old = """        SELECT i.id, i.visit_id, i.user_id, i.invoice_type, i.amount, i.itbis, i.total,
               i.payment_method, i.ecf_id, i.encf, i.estado, i.track_id, i.codigo_seguridad,
               i.dgii_url, i.xml_url, i.created_at, i.tipo_ecf,
               p.name AS patient_name, p.cedula AS patient_cedula, p.id AS patient_id,"""
get_invoice_new = """        SELECT i.id, i.visit_id, i.user_id, i.invoice_type, i.amount, i.itbis, i.total,
               i.payment_method, i.ecf_id, i.encf, i.estado, i.track_id, i.codigo_seguridad,
               i.dgii_url, i.xml_url, i.created_at, i.tipo_ecf, i.amount_paid, i.balance_due, i.due_date,
               p.name AS patient_name, p.cedula AS patient_cedula, p.id AS patient_id,"""
db_code = db_code.replace(get_invoice_old, get_invoice_new)

get_invoice_old2 = """        "xml_url": row[14], "created_at": _fmt_date(row[15]), "tipo_ecf": row[16],
        "patient_name": row[17], "patient_cedula": row[18], "patient_id": row[19],
        "doctor_fullname": row[20]
    }"""
get_invoice_new2 = """        "xml_url": row[14], "created_at": _fmt_date(row[15]), "tipo_ecf": row[16],
        "amount_paid": float(row[17]) if row[17] is not None else 0.0,
        "balance_due": float(row[18]) if row[18] is not None else 0.0,
        "due_date": _fmt_date(row[19]),
        "patient_name": row[20], "patient_cedula": row[21], "patient_id": row[22],
        "doctor_fullname": row[23]
    }"""
db_code = db_code.replace(get_invoice_old2, get_invoice_new2)

# 7. Add get_patient_account_statement
add_get_patient_account = """
def get_patient_account_statement(patient_id: int, doctor_id: int) -> dict | None:
    # Validate access
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(\"\"\"
        SELECT 1 FROM dbo.appointments a WHERE a.patient_id = ? AND a.doctor_id = ?
        UNION
        SELECT 1 FROM dbo.emergency_visits ev WHERE ev.patient_id = ? AND ev.doctor_id = ?
    \"\"\", patient_id, doctor_id, patient_id, doctor_id)
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return None # Access denied or no records

    # Access granted, fetch invoices
    cursor.execute(\"\"\"
        SELECT i.id, i.created_at, i.invoice_type, i.total, i.amount_paid, i.balance_due, i.estado, i.due_date
        FROM dbo.invoices i
        JOIN dbo.emergency_visits ev ON ev.id = i.visit_id
        WHERE ev.patient_id = ?
        ORDER BY i.created_at DESC
    \"\"\", patient_id)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    
    total_balance = 0.0
    for r in rows:
        r["created_at"] = _fmt_date(r.get("created_at"))
        r["due_date"] = _fmt_date(r.get("due_date"))
        r["total"] = float(r["total"])
        r["amount_paid"] = float(r["amount_paid"])
        r["balance_due"] = float(r["balance_due"])
        if r["invoice_type"] != 'nota_credito' and r["estado"] != 'Cancelada':
            total_balance += r["balance_due"]
            
    return {
        "total_balance": total_balance,
        "invoices": rows
    }
"""
if "get_patient_account_statement" not in db_code:
    db_code += add_get_patient_account

with open('database.py', 'w', encoding='utf-8') as f:
    f.write(db_code)
print("database.py patched.")
