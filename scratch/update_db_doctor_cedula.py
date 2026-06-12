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

        print("1. Modificando tabla dbo.users para añadir columna cedula...")
        try:
            cursor.execute("ALTER TABLE dbo.users ADD cedula NVARCHAR(50) NULL;")
            print("  ✅ Columna 'cedula' agregada a dbo.users.")
        except pyodbc.ProgrammingError as e:
            if "already exists" in str(e) or "42S21" in str(e):
                print("  ⚠️ La columna 'cedula' ya existe en dbo.users.")
            else:
                print(f"  ❌ Error al agregar 'cedula': {e}")
                raise e

        print("2. Actualizando la vista dbo.vw_users para incluir columna cedula...")
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

        print("3. Modificando procedimiento sp_create_user...")
        cursor.execute("""
            IF OBJECT_ID(N'dbo.sp_create_user', N'P') IS NOT NULL DROP PROCEDURE dbo.sp_create_user;
        """)
        cursor.execute("""
            CREATE PROCEDURE dbo.sp_create_user
                @username       NVARCHAR(100),
                @password_hash  NVARCHAR(255),
                @role           NVARCHAR(20),
                @full_name      NVARCHAR(200) = NULL,
                @email          NVARCHAR(200) = NULL,
                @matricula      NVARCHAR(50)  = NULL,
                @especialidad   NVARCHAR(150) = NULL,
                @telefono       NVARCHAR(30)  = NULL,
                @hospital       NVARCHAR(200) = NULL,
                @cedula         NVARCHAR(50)  = NULL,
                @photo_url      NVARCHAR(MAX) = NULL
            AS
            BEGIN
                SET NOCOUNT ON;
                SET XACT_ABORT ON;
                BEGIN TRANSACTION;

                INSERT INTO dbo.users (username, password_hash, role, full_name, email, cedula, photo_url)
                VALUES (@username, @password_hash, @role, @full_name, @email, @cedula, @photo_url);

                DECLARE @new_id INT = SCOPE_IDENTITY();

                IF @role = 'doctor'
                BEGIN
                    INSERT INTO dbo.doctors (user_id, matricula, especialidad, telefono, hospital)
                    VALUES (@new_id, @matricula, @especialidad, @telefono, @hospital);
                END

                COMMIT TRANSACTION;
                SELECT @new_id AS user_id;
            END;
        """)
        print("✅ Procedimiento sp_create_user actualizado.")

        print("4. Modificando procedimiento sp_update_user...")
        cursor.execute("""
            IF OBJECT_ID(N'dbo.sp_update_user', N'P') IS NOT NULL DROP PROCEDURE dbo.sp_update_user;
        """)
        cursor.execute("""
            CREATE PROCEDURE dbo.sp_update_user
                @user_id        INT,
                @username       NVARCHAR(100) = NULL,
                @password_hash  NVARCHAR(255) = NULL,
                @role           NVARCHAR(20)  = NULL,
                @full_name      NVARCHAR(200) = NULL,
                @email          NVARCHAR(200) = NULL,
                @is_active      BIT           = NULL,
                @matricula      NVARCHAR(50)  = NULL,
                @especialidad   NVARCHAR(150) = NULL,
                @telefono       NVARCHAR(30)  = NULL,
                @hospital       NVARCHAR(200) = NULL,
                @cedula         NVARCHAR(50)  = NULL,
                @photo_url      NVARCHAR(MAX) = NULL
            AS
            BEGIN
                SET NOCOUNT ON;
                UPDATE dbo.users
                SET username      = COALESCE(@username, username),
                    password_hash = COALESCE(@password_hash, password_hash),
                    role          = COALESCE(@role, role),
                    full_name     = COALESCE(@full_name, full_name),
                    email         = COALESCE(@email, email),
                    is_active     = COALESCE(@is_active, is_active),
                    cedula        = COALESCE(@cedula, cedula),
                    photo_url     = COALESCE(@photo_url, photo_url),
                    updated_at    = SYSUTCDATETIME()
                WHERE id = @user_id;

                -- Actualizar o crear datos de doctor
                IF (@matricula IS NOT NULL OR @especialidad IS NOT NULL OR @telefono IS NOT NULL OR @hospital IS NOT NULL)
                BEGIN
                    IF EXISTS (SELECT 1 FROM dbo.doctors WHERE user_id = @user_id)
                        UPDATE dbo.doctors
                        SET matricula   = COALESCE(@matricula, matricula),
                            especialidad = COALESCE(@especialidad, especialidad),
                            telefono    = COALESCE(@telefono, telefono),
                            hospital    = COALESCE(@hospital, hospital),
                            updated_at  = SYSUTCDATETIME()
                        WHERE user_id = @user_id;
                    ELSE
                        INSERT INTO dbo.doctors (user_id, matricula, especialidad, telefono, hospital)
                        VALUES (@user_id, @matricula, @especialidad, @telefono, @hospital);
                END

                SELECT @@ROWCOUNT AS rows_affected;
            END;
        """)
        print("✅ Procedimiento sp_update_user actualizado.")

        cursor.close()
        conn.commit()
        conn.close()
        print("\n🚀 ¡Base de datos actualizada con la cédula del doctor!")

    except Exception as e:
        print(f"❌ Error general: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_updates()
