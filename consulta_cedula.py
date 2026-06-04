import requests

BASE_URL = "https://ecf-platform-backend-50801509587.us-central1.run.app"
API_KEY  = "ecf_live_5ad0ef2626e32d8967e13f655cee0c45f54d8509b1ef793149b881cbb52f25fe"

def consultar_cedula(cedula: str):
    cedula = cedula.replace("-", "").strip()
    if len(cedula) != 11 or not cedula.isdigit():
        print("❌ La cédula debe tener exactamente 11 dígitos.")
        return

    url = f"{BASE_URL}/api/v1/dgii/jce?cedula={cedula}"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }

    print(f"\n🔍 Consultando cédula {cedula}...")
    try:
        res = requests.get(url, headers=headers)
        data = res.json()

        if not res.ok or not data.get("found"):
            print(f"❌ No encontrado: {data.get('message', 'Cédula no existe en la JCE.')}")
            return

        print("\n✅ Persona encontrada:")
        print(f"  Cédula:           {data.get('cedula')}")
        print(f"  Nombre completo:  {data.get('nombre')}")
        print(f"  Primer nombre:    {data.get('primerNombre')}")
        print(f"  Segundo nombre:   {data.get('segundoNombre')}")
        print(f"  Primer apellido:  {data.get('primerApellido')}")
        print(f"  Segundo apellido: {data.get('segundoApellido')}")
        print(f"  Sexo:             {data.get('sexo')}")
        print(f"  Fecha nacimiento: {data.get('fechaNacimiento', '')[:10]}")
        print(f"  Lugar nacimiento: {data.get('lugarNacimiento')}")
        print(f"  Foto URL:         {data.get('foto', 'N/A')}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    while True:
        cedula = input("\nIngresa la cédula (o 'salir'): ").strip()
        if cedula.lower() == "salir":
            break
        consultar_cedula(cedula)
