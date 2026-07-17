"""
Verifica que las funciones clave de database.py tengan la lógica correcta
para los nuevos campos.
"""
import sys
sys.path.insert(0, '.')

# 1. Check that create_invoice has the right signature
import inspect
import database as db

sig = inspect.signature(db.create_invoice)
params = list(sig.parameters.keys())
print("=== create_invoice params ===")
print(params)
expected = ['amount_paid', 'balance_due', 'due_date']
for p in expected:
    if p in params:
        print(f"  [OK] {p}")
    else:
        print(f"  [MISSING] {p}")

# 2. Check get_patient returns vital_status fields
print("\n=== get_patient returns (check source) ===")
src = inspect.getsource(db.get_patient)
for field in ['vital_status', 'death_date', 'death_certificate_url', 'death_notes']:
    if field in src:
        print(f"  [OK] {field} in get_patient")
    else:
        print(f"  [MISSING] {field} in get_patient")

# 3. Check mark_patient_deceased exists
print("\n=== mark_patient_deceased ===")
if hasattr(db, 'mark_patient_deceased'):
    sig2 = inspect.signature(db.mark_patient_deceased)
    print(f"  [OK] exists, params: {list(sig2.parameters.keys())}")
else:
    print("  [MISSING] mark_patient_deceased not found")

# 4. Check get_patient_account_statement exists
print("\n=== get_patient_account_statement ===")
if hasattr(db, 'get_patient_account_statement'):
    sig3 = inspect.signature(db.get_patient_account_statement)
    print(f"  [OK] exists, params: {list(sig3.parameters.keys())}")
else:
    print("  [MISSING] get_patient_account_statement not found")

# 5. Check list_invoices returns amount_paid/balance_due/due_date in SELECT
print("\n=== list_invoices SELECT ===")
src_li = inspect.getsource(db.list_invoices)
for field in ['amount_paid', 'balance_due', 'due_date']:
    if field in src_li:
        print(f"  [OK] {field} in list_invoices")
    else:
        print(f"  [MISSING] {field} in list_invoices")

# 6. Check get_invoice_by_id includes new fields
print("\n=== get_invoice_by_id return ===")
src_gi = inspect.getsource(db.get_invoice_by_id)
for field in ['amount_paid', 'balance_due', 'due_date']:
    if field in src_gi:
        print(f"  [OK] {field} in get_invoice_by_id")
    else:
        print(f"  [MISSING] {field} in get_invoice_by_id")

print("\n=== ALL CHECKS DONE ===")
