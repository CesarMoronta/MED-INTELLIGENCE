import json
from datetime import datetime, date
from database.connection import get_connection, get_db_cursor, rows_to_dicts, _fmt_date, MAX_LOGIN_ATTEMPTS, LOCKOUT_MINUTES
import re
import os
import requests

def list_pending_bills() -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        WITH visit_billing AS (
            SELECT 
                ev.id AS visit_id,
                ev.visit_date,
                p.name AS patient_name,
                p.cedula AS patient_cedula,
                u.full_name AS doctor_fullname,
                p.id AS patient_id,
                inv.balance_due,
                inv.is_cancelled
            FROM dbo.emergency_visits ev
            INNER JOIN dbo.patients p ON ev.patient_id = p.id
            INNER JOIN dbo.users u ON ev.doctor_id = u.id
            LEFT JOIN dbo.appointments app ON ev.appointment_id = app.id
            OUTER APPLY (
                SELECT TOP 1 
                    i.balance_due,
                    CASE 
                        WHEN EXISTS (
                            SELECT 1 FROM dbo.invoices cn 
                            WHERE cn.visit_id = i.visit_id 
                              AND cn.invoice_type = 'nota_credito' 
                              AND cn.created_at > i.created_at
                        ) THEN 1 
                        ELSE 0 
                    END AS is_cancelled
                FROM dbo.invoices i
                WHERE i.visit_id = ev.id AND i.invoice_type = 'consulta'
                ORDER BY i.created_at DESC
            ) inv
            WHERE ev.status = 'cerrada' AND ev.visit_type = 'consulta'
              AND (app.parent_appointment_id IS NULL OR ev.appointment_id IS NULL)
        )
        SELECT 
            visit_id, visit_date, patient_name, patient_cedula, doctor_fullname, patient_id,
            CASE 
                WHEN balance_due IS NULL OR is_cancelled = 1 THEN 3000.00
                ELSE balance_due
            END AS pending_amount
        FROM visit_billing
        WHERE (balance_due IS NULL OR is_cancelled = 1 OR balance_due > 0)
        ORDER BY visit_date DESC
    """)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["visit_date"] = _fmt_date(r.get("visit_date"))
        r["pending_amount"] = float(r.get("pending_amount") or 3000.00)
    return rows

def get_patient_billing_info(patient_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT patient_id, rnc, razon_social, correo
        FROM dbo.patient_billing_info
        WHERE patient_id = ?
    """, patient_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    return {
        "patient_id": row[0],
        "rnc": row[1],
        "razon_social": row[2],
        "correo": row[3]
    }

def save_patient_billing_info(patient_id: int, rnc: str, razon_social: str, correo: str | None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            IF EXISTS (SELECT 1 FROM dbo.patient_billing_info WHERE patient_id = ?)
                UPDATE dbo.patient_billing_info
                SET rnc = ?, razon_social = ?, correo = ?, updated_at = SYSUTCDATETIME()
                WHERE patient_id = ?
            ELSE
                INSERT INTO dbo.patient_billing_info (patient_id, rnc, razon_social, correo)
                VALUES (?, ?, ?, ?)
        """, patient_id, rnc, razon_social, correo, patient_id,
             patient_id, rnc, razon_social, correo)
        return True
    except Exception as e:
        print(f"Error guardando informacion de facturacion del paciente: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_invoice(visit_id: int | None, user_id: int | None, invoice_type: str,
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
            
        cursor.execute("""
            SET NOCOUNT ON;
            DECLARE @inserted TABLE (id INT);
            INSERT INTO dbo.invoices (visit_id, user_id, invoice_type, amount, itbis, total,
                                      payment_method, ecf_id, encf, estado, track_id,
                                      codigo_seguridad, dgii_url, xml_url, tipo_ecf, amount_paid, balance_due, due_date)
            OUTPUT INSERTED.id INTO @inserted
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            SELECT id FROM @inserted;
        """, visit_id, user_id, invoice_type, amount, itbis, total,
             payment_method, ecf_id, encf, estado, track_id,
             codigo_seguridad, dgii_url, xml_url, tipo_ecf, amount_paid, balance_due, due_date)
        row = cursor.fetchone()
        invoice_id = int(row[0]) if row and row[0] is not None else None
        return invoice_id
    except Exception as e:
        print(f"Error insertando factura: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def list_invoices() -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.visit_id, i.user_id, i.invoice_type, i.amount, i.itbis, i.total,
               i.payment_method, i.ecf_id, i.encf, i.estado, i.track_id, i.codigo_seguridad,
               i.dgii_url, i.xml_url, i.created_at, i.tipo_ecf, i.amount_paid, i.balance_due, i.due_date,
               p.name AS patient_name, p.cedula AS patient_cedula, p.id AS patient_id,
               u.full_name AS doctor_fullname,
               CASE 
                   WHEN i.invoice_type <> 'nota_credito' AND EXISTS (
                       SELECT 1 FROM dbo.invoices cn 
                       WHERE cn.visit_id = i.visit_id 
                         AND cn.invoice_type = 'nota_credito' 
                         AND cn.created_at > i.created_at
                   ) THEN 1 
                   ELSE 0 
               END AS is_cancelled
        FROM dbo.invoices i
        LEFT JOIN dbo.emergency_visits ev ON i.visit_id = ev.id
        LEFT JOIN dbo.patients p ON ev.patient_id = p.id
        LEFT JOIN dbo.users u ON (ev.doctor_id = u.id OR i.user_id = u.id)
        ORDER BY i.created_at DESC
    """)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["created_at"] = _fmt_date(r.get("created_at"))
        r["amount"] = float(r["amount"])
        r["itbis"] = float(r["itbis"])
        r["total"] = float(r["total"])
        r["amount_paid"] = float(r["amount_paid"]) if r.get("amount_paid") is not None else 0.0
        r["balance_due"] = float(r["balance_due"]) if r.get("balance_due") is not None else 0.0
        r["due_date"] = _fmt_date(r.get("due_date"))
        r["is_cancelled"] = bool(r.get("is_cancelled", 0))
    return rows

def get_invoice_by_id(invoice_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.visit_id, i.user_id, i.invoice_type, i.amount, i.itbis, i.total,
               i.payment_method, i.ecf_id, i.encf, i.estado, i.track_id, i.codigo_seguridad,
               i.dgii_url, i.xml_url, i.created_at, i.tipo_ecf, i.amount_paid, i.balance_due, i.due_date,
               p.name AS patient_name, p.cedula AS patient_cedula, p.id AS patient_id,
               u.full_name AS doctor_fullname
        FROM dbo.invoices i
        LEFT JOIN dbo.emergency_visits ev ON i.visit_id = ev.id
        LEFT JOIN dbo.patients p ON ev.patient_id = p.id
        LEFT JOIN dbo.users u ON (ev.doctor_id = u.id OR i.user_id = u.id)
        WHERE i.id = ?
    """, invoice_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0], "visit_id": row[1], "user_id": row[2], "invoice_type": row[3],
        "amount": float(row[4]) if row[4] is not None else 0.0,
        "itbis": float(row[5]) if row[5] is not None else 0.0,
        "total": float(row[6]) if row[6] is not None else 0.0,
        "payment_method": row[7], "ecf_id": row[8], "encf": row[9], "estado": row[10],
        "track_id": row[11], "codigo_seguridad": row[12], "dgii_url": row[13],
        "xml_url": row[14], "created_at": _fmt_date(row[15]), "tipo_ecf": row[16],
        "amount_paid": float(row[17]) if row[17] is not None else 0.0,
        "balance_due": float(row[18]) if row[18] is not None else 0.0,
        "due_date": _fmt_date(row[19]),
        "patient_name": row[20], "patient_cedula": row[21], "patient_id": row[22],
        "doctor_fullname": row[23]
    }

def get_patient_account_statement(patient_id: int, doctor_id: int) -> dict | None:
    # Validate access
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM dbo.appointments a WHERE a.patient_id = ? AND a.doctor_id = ?
        UNION
        SELECT 1 FROM dbo.emergency_visits ev WHERE ev.patient_id = ? AND ev.doctor_id = ?
    """, patient_id, doctor_id, patient_id, doctor_id)
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return None # Access denied or no records

    # Access granted, fetch invoices
    cursor.execute("""
        SELECT i.id, i.created_at, i.invoice_type, i.total, i.amount_paid, i.balance_due, i.estado, i.due_date
        FROM dbo.invoices i
        JOIN dbo.emergency_visits ev ON ev.id = i.visit_id
        WHERE ev.patient_id = ?
        ORDER BY i.created_at DESC
    """, patient_id)
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
