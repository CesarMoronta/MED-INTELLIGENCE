import sys
import pyodbc

# Forzar la codificación estándar (necesario en Windows)
if getattr(sys.stdout, 'encoding', None) and sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from database import get_connection

def apply_updates():
    print("🔗 Conectando a la base de datos...")
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("1. Creando tabla dbo.patient_billing_info...")
        cursor.execute("""
            IF OBJECT_ID(N'dbo.patient_billing_info', N'U') IS NULL
            BEGIN
                CREATE TABLE dbo.patient_billing_info (
                    patient_id   INT                 NOT NULL,
                    rnc          NVARCHAR(50)        NOT NULL,
                    razon_social NVARCHAR(200)       NOT NULL,
                    correo       NVARCHAR(200)       NULL,
                    updated_at   DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
                    CONSTRAINT PK_patient_billing_info PRIMARY KEY (patient_id),
                    CONSTRAINT FK_patient_billing_info_patient FOREIGN KEY (patient_id)
                        REFERENCES dbo.patients(id) ON DELETE CASCADE
                );
                PRINT '✅ Tabla dbo.patient_billing_info creada.';
            END
            ELSE
            BEGIN
                PRINT '⚠️ La tabla dbo.patient_billing_info ya existe.';
            END
        """)

        print("2. Modificando tabla dbo.invoices...")
        try:
            cursor.execute("""
                ALTER TABLE dbo.invoices
                ADD tipo_ecf NVARCHAR(10) NULL;
            """)
            print("✅ Columna tipo_ecf agregada a dbo.invoices.")
        except pyodbc.ProgrammingError as e:
            if "already exists" in str(e) or "42S21" in str(e):
                print("⚠️ La columna tipo_ecf ya existe en dbo.invoices.")
            else:
                print(f"❌ Error al alterar dbo.invoices: {e}")

        cursor.close()
        conn.close()
        print("\n🚀 ¡Base de datos actualizada con las tablas de facturación!")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_updates()
