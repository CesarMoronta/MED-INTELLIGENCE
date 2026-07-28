import re

def validate_cedula_and_name(raw_cedula: str, name: str):
    cedula_digits = re.sub(r"\D", "", raw_cedula)
    if len(cedula_digits) != 11:
        return False, "La cédula debe contener exactamente 11 dígitos numéricos."
    
    clean_name = (name or "").strip().upper()
    if not clean_name:
        return False, "El nombre completo del paciente es requerido."
    
    return True, {"cedula_digits": cedula_digits, "name": clean_name}

# Test cases
print("Test 1 (Valid 11 digits & lowercase name):", validate_cedula_and_name("001-1234567-8", "juan perez"))
print("Test 2 (Invalid 5 digits):", validate_cedula_and_name("12345", "maria gomez"))
print("Test 3 (Valid 11 digits without hyphens):", validate_cedula_and_name("03100012345", "pedro alcatara"))
