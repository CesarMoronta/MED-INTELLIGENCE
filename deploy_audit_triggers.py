import os
import sys
import pyodbc
from dotenv import load_dotenv

# Forzar la codificación estándar (necesario en Windows)
if getattr(sys.stdout, 'encoding', None) and sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Cargar dotenv desde la carpeta raíz
project_root = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(project_root, '.env'), override=True)

from database import get_connection

def deploy_triggers():
    print("🔗 Conectando a la base de datos para instalar triggers de auditoría...")
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Lista de tablas y sus respectivos SQLs de trigger (Drop y luego Create)
        triggers = {
            "users": {
                "drop": "IF OBJECT_ID('dbo.trg_users_audit', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_users_audit;",
                "create": """
                    CREATE TRIGGER trg_users_audit ON dbo.users AFTER INSERT, UPDATE, DELETE AS
                    BEGIN
                        SET NOCOUNT ON;
                        IF APP_NAME() = 'MedIntelligenceApp' RETURN;
                        DECLARE @action NVARCHAR(50);
                        IF EXISTS(SELECT 1 FROM inserted) AND EXISTS(SELECT 1 FROM deleted) SET @action = 'UPDATE';
                        ELSE IF EXISTS(SELECT 1 FROM inserted) SET @action = 'CREATE';
                        ELSE IF EXISTS(SELECT 1 FROM deleted) SET @action = 'DELETE';
                        ELSE RETURN;
                        IF @action = 'CREATE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_CREATE', 'User', CAST(id AS NVARCHAR(100)), 'Usuario creado directamente: ' + username + ' (Rol: ' + role + ') via ' + APP_NAME() FROM inserted;
                        END
                        ELSE IF @action = 'DELETE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_DELETE', 'User', CAST(id AS NVARCHAR(100)), 'Usuario eliminado directamente: ' + username + ' (Rol: ' + role + ') via ' + APP_NAME() FROM deleted;
                        END
                        ELSE IF @action = 'UPDATE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_UPDATE', 'User', CAST(i.id AS NVARCHAR(100)), 'Usuario modificado directamente: ' + i.username + ' (Rol: ' + i.role + ') via ' + APP_NAME() FROM inserted i;
                        END
                    END;
                """
            },
            "patients": {
                "drop": "IF OBJECT_ID('dbo.trg_patients_audit', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_patients_audit;",
                "create": """
                    CREATE TRIGGER trg_patients_audit ON dbo.patients AFTER INSERT, UPDATE, DELETE AS
                    BEGIN
                        SET NOCOUNT ON;
                        IF APP_NAME() = 'MedIntelligenceApp' RETURN;
                        DECLARE @action NVARCHAR(50);
                        IF EXISTS(SELECT 1 FROM inserted) AND EXISTS(SELECT 1 FROM deleted) SET @action = 'UPDATE';
                        ELSE IF EXISTS(SELECT 1 FROM inserted) SET @action = 'CREATE';
                        ELSE IF EXISTS(SELECT 1 FROM deleted) SET @action = 'DELETE';
                        ELSE RETURN;
                        IF @action = 'CREATE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_CREATE', 'Patient', CAST(id AS NVARCHAR(100)), 'Paciente creado directamente: ' + name + ' (Cédula: ' + cedula + ') via ' + APP_NAME() FROM inserted;
                        END
                        ELSE IF @action = 'DELETE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_DELETE', 'Patient', CAST(id AS NVARCHAR(100)), 'Paciente eliminado directamente: ' + name + ' (Cédula: ' + cedula + ') via ' + APP_NAME() FROM deleted;
                        END
                        ELSE IF @action = 'UPDATE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_UPDATE', 'Patient', CAST(i.id AS NVARCHAR(100)), 'Paciente modificado directamente: ' + i.name + ' (Cédula: ' + i.cedula + ') via ' + APP_NAME() FROM inserted i;
                        END
                    END;
                """
            },
            "emergency_visits": {
                "drop": "IF OBJECT_ID('dbo.trg_visits_audit', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_visits_audit;",
                "create": """
                    CREATE TRIGGER trg_visits_audit ON dbo.emergency_visits AFTER INSERT, UPDATE, DELETE AS
                    BEGIN
                        SET NOCOUNT ON;
                        IF APP_NAME() = 'MedIntelligenceApp' RETURN;
                        DECLARE @action NVARCHAR(50);
                        IF EXISTS(SELECT 1 FROM inserted) AND EXISTS(SELECT 1 FROM deleted) SET @action = 'UPDATE';
                        ELSE IF EXISTS(SELECT 1 FROM inserted) SET @action = 'CREATE';
                        ELSE IF EXISTS(SELECT 1 FROM deleted) SET @action = 'DELETE';
                        ELSE RETURN;
                        IF @action = 'CREATE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_CREATE', 'EmergencyVisit', CAST(id AS NVARCHAR(100)), 'Visita médica creada directamente (Tipo: ' + visit_type + ') via ' + APP_NAME() FROM inserted;
                        END
                        ELSE IF @action = 'DELETE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_DELETE', 'EmergencyVisit', CAST(id AS NVARCHAR(100)), 'Visita médica eliminada directamente (Tipo: ' + visit_type + ') via ' + APP_NAME() FROM deleted;
                        END
                        ELSE IF @action = 'UPDATE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_UPDATE', 'EmergencyVisit', CAST(i.id AS NVARCHAR(100)), 'Visita médica modificada directamente (Tipo: ' + i.visit_type + ', Estado: ' + i.status + ') via ' + APP_NAME() FROM inserted i;
                        END
                    END;
                """
            },
            "appointments": {
                "drop": "IF OBJECT_ID('dbo.trg_appointments_audit', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_appointments_audit;",
                "create": """
                    CREATE TRIGGER trg_appointments_audit ON dbo.appointments AFTER INSERT, UPDATE, DELETE AS
                    BEGIN
                        SET NOCOUNT ON;
                        IF APP_NAME() = 'MedIntelligenceApp' RETURN;
                        DECLARE @action NVARCHAR(50);
                        IF EXISTS(SELECT 1 FROM inserted) AND EXISTS(SELECT 1 FROM deleted) SET @action = 'UPDATE';
                        ELSE IF EXISTS(SELECT 1 FROM inserted) SET @action = 'CREATE';
                        ELSE IF EXISTS(SELECT 1 FROM deleted) SET @action = 'DELETE';
                        ELSE RETURN;
                        IF @action = 'CREATE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_CREATE', 'Appointment', CAST(id AS NVARCHAR(100)), 'Cita médica creada directamente (Fecha: ' + CAST(scheduled_date AS NVARCHAR(20)) + ') via ' + APP_NAME() FROM inserted;
                        END
                        ELSE IF @action = 'DELETE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_DELETE', 'Appointment', CAST(id AS NVARCHAR(100)), 'Cita médica eliminada directamente (Fecha: ' + CAST(scheduled_date AS NVARCHAR(20)) + ') via ' + APP_NAME() FROM deleted;
                        END
                        ELSE IF @action = 'UPDATE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_UPDATE', 'Appointment', CAST(i.id AS NVARCHAR(100)), 'Cita médica modificada directamente (Fecha: ' + CAST(i.scheduled_date AS NVARCHAR(20)) + ', Estado: ' + i.status + ') via ' + APP_NAME() FROM inserted i;
                        END
                    END;
                """
            },
            "invoices": {
                "drop": "IF OBJECT_ID('dbo.trg_invoices_audit', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_invoices_audit;",
                "create": """
                    CREATE TRIGGER trg_invoices_audit ON dbo.invoices AFTER INSERT, UPDATE, DELETE AS
                    BEGIN
                        SET NOCOUNT ON;
                        IF APP_NAME() = 'MedIntelligenceApp' RETURN;
                        DECLARE @action NVARCHAR(50);
                        IF EXISTS(SELECT 1 FROM inserted) AND EXISTS(SELECT 1 FROM deleted) SET @action = 'UPDATE';
                        ELSE IF EXISTS(SELECT 1 FROM inserted) SET @action = 'CREATE';
                        ELSE IF EXISTS(SELECT 1 FROM deleted) SET @action = 'DELETE';
                        ELSE RETURN;
                        IF @action = 'CREATE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_CREATE', 'Billing', CAST(id AS NVARCHAR(100)), 'Factura creada directamente (Total: ' + CAST(total AS NVARCHAR(20)) + ', eNCF: ' + COALESCE(encf, '—') + ') via ' + APP_NAME() FROM inserted;
                        END
                        ELSE IF @action = 'DELETE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_DELETE', 'Billing', CAST(id AS NVARCHAR(100)), 'Factura eliminada directamente (eNCF: ' + COALESCE(encf, '—') + ') via ' + APP_NAME() FROM deleted;
                        END
                        ELSE IF @action = 'UPDATE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_UPDATE', 'Billing', CAST(i.id AS NVARCHAR(100)), 'Factura modificada directamente (Monto: ' + CAST(i.total AS NVARCHAR(20)) + ', eNCF: ' + COALESCE(i.encf, '—') + ') via ' + APP_NAME() FROM inserted i;
                        END
                    END;
                """
            },
            "diagnoses": {
                "drop": "IF OBJECT_ID('dbo.trg_diagnoses_audit', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_diagnoses_audit;",
                "create": """
                    CREATE TRIGGER trg_diagnoses_audit ON dbo.diagnoses AFTER INSERT, UPDATE, DELETE AS
                    BEGIN
                        SET NOCOUNT ON;
                        IF APP_NAME() = 'MedIntelligenceApp' RETURN;
                        DECLARE @action NVARCHAR(50);
                        IF EXISTS(SELECT 1 FROM inserted) AND EXISTS(SELECT 1 FROM deleted) SET @action = 'UPDATE';
                        ELSE IF EXISTS(SELECT 1 FROM inserted) SET @action = 'CREATE';
                        ELSE IF EXISTS(SELECT 1 FROM deleted) SET @action = 'DELETE';
                        ELSE RETURN;
                        IF @action = 'CREATE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_CREATE', 'Diagnosis', CAST(id AS NVARCHAR(100)), 'Diagnóstico creado directamente: ' + diagnosis_primary + ' via ' + APP_NAME() FROM inserted;
                        END
                        ELSE IF @action = 'DELETE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_DELETE', 'Diagnosis', CAST(id AS NVARCHAR(100)), 'Diagnóstico eliminado directamente: ' + diagnosis_primary + ' via ' + APP_NAME() FROM deleted;
                        END
                        ELSE IF @action = 'UPDATE' BEGIN
                            INSERT INTO dbo.audit_log (username, action, entity, entity_id, details)
                            SELECT COALESCE(SYSTEM_USER, 'DB_DIRECT'), 'DB_DIRECT_UPDATE', 'Diagnosis', CAST(i.id AS NVARCHAR(100)), 'Diagnóstico modificado directamente: ' + i.diagnosis_primary + ' via ' + APP_NAME() FROM inserted i;
                        END
                    END;
                """
            }
        }

        # Desplegar triggers
        for table, sqls in triggers.items():
            print(f"Instalando trigger de auditoría para la tabla 'dbo.{table}'...")
            try:
                # 1. Eliminar si existe
                cursor.execute(sqls["drop"])
                # 2. Crear trigger
                cursor.execute(sqls["create"])
                print(f"✅ Trigger para 'dbo.{table}' instalado con éxito.")
            except Exception as trigger_err:
                print(f"❌ Error al crear trigger para 'dbo.{table}': {trigger_err}")
                conn.rollback()
                raise trigger_err

        conn.commit()
        cursor.close()
        conn.close()
        print("\n🚀 ¡Todos los triggers de auditoría se instalaron y configuraron con éxito!")

    except Exception as e:
        print(f"❌ Error general en la migración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    deploy_triggers()
