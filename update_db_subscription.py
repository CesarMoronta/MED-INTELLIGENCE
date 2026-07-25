import sys
import pyodbc

# Forzar la codificación estándar (necesario en Windows)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from database import get_connection

def apply_updates():
    print("🔗 Conectando a la base de datos...")
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("1. Modificando tabla dbo.users para añadir campos de perfil y suscripción...")
        columns_to_add = [
            ("photo_url", "NVARCHAR(MAX) NULL"),
            ("subscription_active", "BIT NOT NULL DEFAULT 0"),
            ("subscription_id", "NVARCHAR(100) NULL"),
            ("subscription_plan", "NVARCHAR(50) NULL"),
            ("subscription_expires_at", "DATETIME2 NULL"),
            ("cedula", "NVARCHAR(50) NULL")
        ]

        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE dbo.users ADD {col_name} {col_type};")
                print(f"  ✅ Columna '{col_name}' agregada.")
            except pyodbc.ProgrammingError as e:
                if "already exists" in str(e) or "42S21" in str(e):
                    print(f"  ⚠️ La columna '{col_name}' ya existe.")
                else:
                    print(f"  ❌ Error al agregar '{col_name}': {e}")
                    raise e

        print("2. Actualizando la vista dbo.vw_users para incluir nuevos campos...")
        cursor.execute("""
            ALTER VIEW dbo.vw_users AS
            SELECT
                u.id,
                u.username,
                u.role,
                u.full_name,
                u.email,
                u.is_active,
                u.failed_logins,
                u.locked_until,
                u.last_login,
                u.created_at,
                u.updated_at,
                u.photo_url,
                u.subscription_active,
                u.subscription_id,
                u.subscription_plan,
                u.subscription_expires_at,
                u.cedula,
                -- Datos de doctor (si existe)
                doc.id          AS doctor_id,
                doc.matricula,
                doc.especialidad,
                doc.telefono,
                doc.hospital
            FROM dbo.users u
            LEFT JOIN dbo.doctors doc ON doc.user_id = u.id;
        """)
        print("✅ Vista dbo.vw_users actualizada exitosamente.")

        cursor.close()
        conn.close()
        print("\n🚀 ¡Base de datos actualizada con campos de suscripción y perfil!")

    except Exception as e:
        print(f"❌ Error general: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_updates()
