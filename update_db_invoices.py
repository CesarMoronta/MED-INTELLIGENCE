import os
import sys
import pyodbc

# Forzar la codificación estándar (necesario en Windows)
if getattr(sys.stdout, 'encoding', None) and sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from database import get_connection

def apply_migration():
    print("🔗 Conectando a la base de datos para crear la tabla de facturación...")
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("1. Creando tabla dbo.invoices...")
        cursor.execute("""
            IF OBJECT_ID(N'dbo.invoices', N'U') IS NULL
            BEGIN
                CREATE TABLE dbo.invoices (
                    id                  INT IDENTITY(1,1)   NOT NULL,
                    visit_id            INT                 NULL,
                    user_id             INT                 NULL,
                    invoice_type        NVARCHAR(20)        NOT NULL,
                    amount              DECIMAL(10,2)       NOT NULL,
                    itbis               DECIMAL(10,2)       NOT NULL,
                    total               DECIMAL(10,2)       NOT NULL,
                    payment_method      NVARCHAR(20)        NOT NULL,
                    ecf_id              NVARCHAR(100)       NULL,
                    encf                NVARCHAR(50)        NULL,
                    estado              NVARCHAR(50)        NOT NULL DEFAULT 'Pendiente',
                    track_id            NVARCHAR(100)       NULL,
                    codigo_seguridad    NVARCHAR(50)        NULL,
                    dgii_url            NVARCHAR(MAX)       NULL,
                    xml_url             NVARCHAR(MAX)       NULL,
                    created_at          DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
                    CONSTRAINT PK_invoices PRIMARY KEY (id),
                    CONSTRAINT FK_invoices_visit FOREIGN KEY (visit_id) REFERENCES dbo.emergency_visits(id),
                    CONSTRAINT FK_invoices_user FOREIGN KEY (user_id) REFERENCES dbo.users(id)
                );
                PRINT '✅ Tabla dbo.invoices creada con éxito.';
            END
            ELSE
            BEGIN
                PRINT '⚠️ La tabla dbo.invoices ya existe.';
            END
        """)
        
        # Guardar cambios
        conn.commit()
        cursor.close()
        conn.close()
        print("\n🚀 ¡Migración de facturación aplicada con éxito!")

    except Exception as e:
        print(f"❌ Error al ejecutar la migración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_migration()
