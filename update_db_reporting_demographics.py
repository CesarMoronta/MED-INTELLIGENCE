# -*- coding: utf-8 -*-
from database import get_connection

def apply_migration():
    print("Starting demographics and reporting fields database migration...")
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Agregar columnas a dbo.patients si no existen
    alter_table_sql = """
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.patients') AND name = 'birth_country')
    BEGIN
        ALTER TABLE dbo.patients ADD
            birth_country    NVARCHAR(100) NULL,
            birth_city       NVARCHAR(100) NULL,
            residence_country NVARCHAR(100) NULL,
            residence_city    NVARCHAR(100) NULL,
            ethnicity        NVARCHAR(100) NULL,
            past_surgeries   NVARCHAR(MAX) NULL,
            education_level  NVARCHAR(100) NULL,
            occupation       NVARCHAR(100) NULL,
            marital_status   NVARCHAR(50)  NULL;
    END
    """
    try:
        cursor.execute(alter_table_sql)
        conn.commit()
        print("Columns added or already exist in dbo.patients.")
    except Exception as e:
        print(f"Error altering table patients: {e}")
        cursor.close()
        conn.close()
        return

    # 2. Recrear Vista vw_patients
    recreate_view_sql = """
    ALTER VIEW dbo.vw_patients AS
    SELECT
        p.id,
        p.cedula,
        p.name,
        p.dob,
        p.gender,
        p.phone,
        p.blood_type,
        p.registered_by,
        p.created_at,
        p.updated_at,
        p.photo_url,
        p.vital_status,
        p.death_date,
        p.death_certificate_url,
        p.death_notes,
        p.birth_country,
        p.birth_city,
        p.residence_country,
        p.residence_city,
        p.ethnicity,
        p.past_surgeries,
        p.education_level,
        p.occupation,
        p.marital_status,
        DATEDIFF(YEAR, p.dob, GETDATE())
            - CASE WHEN MONTH(p.dob) > MONTH(GETDATE())
                    OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE()))
                   THEN 1 ELSE 0 END AS age,
        (
            SELECT pa.antecedent, pa.value
            FROM dbo.patient_antecedents pa
            WHERE pa.patient_id = p.id
            FOR JSON PATH
        ) AS antecedentes
    FROM dbo.patients p;
    """
    try:
        cursor.execute(recreate_view_sql)
        conn.commit()
        print("View dbo.vw_patients recreated successfully.")
    except Exception as e:
        print(f"Error altering view vw_patients: {e}")
        cursor.close()
        conn.close()
        return

    # 3. Recrear SP sp_create_patient
    recreate_sp_create = """
    ALTER PROCEDURE dbo.sp_create_patient
        @cedula         NVARCHAR(50),
        @name           NVARCHAR(200),
        @dob            DATE,
        @gender         NVARCHAR(20),
        @phone          NVARCHAR(30)  = NULL,
        @blood_type     NVARCHAR(5)   = NULL,
        @registered_by  INT           = NULL,
        @photo_url      NVARCHAR(MAX) = NULL,
        @vital_status   NVARCHAR(20)  = 'Vivo',
        @death_date     DATE          = NULL,
        @death_certificate_url NVARCHAR(MAX) = NULL,
        @death_notes    NVARCHAR(MAX) = NULL,
        @birth_country   NVARCHAR(100) = NULL,
        @birth_city      NVARCHAR(100) = NULL,
        @residence_country NVARCHAR(100) = NULL,
        @residence_city  NVARCHAR(100) = NULL,
        @ethnicity       NVARCHAR(100) = NULL,
        @past_surgeries  NVARCHAR(MAX) = NULL,
        @education_level NVARCHAR(100) = NULL,
        @occupation      NVARCHAR(100) = NULL,
        @marital_status  NVARCHAR(50)  = NULL
    AS
    BEGIN
        SET NOCOUNT ON;
        INSERT INTO dbo.patients (
            cedula, name, dob, gender, phone, blood_type, registered_by, photo_url, vital_status, death_date, death_certificate_url, death_notes,
            birth_country, birth_city, residence_country, residence_city, ethnicity, past_surgeries, education_level, occupation, marital_status
        )
        VALUES (
            @cedula, @name, @dob, @gender, @phone, @blood_type, @registered_by, @photo_url, @vital_status, @death_date, @death_certificate_url, @death_notes,
            @birth_country, @birth_city, @residence_country, @residence_city, @ethnicity, @past_surgeries, @education_level, @occupation, @marital_status
        );
        SELECT SCOPE_IDENTITY() AS patient_id;
    END
    """
    try:
        cursor.execute(recreate_sp_create)
        conn.commit()
        print("SP dbo.sp_create_patient altered successfully.")
    except Exception as e:
        print(f"Error altering SP sp_create_patient: {e}")
        cursor.close()
        conn.close()
        return

    # 4. Recrear SP sp_update_patient
    recreate_sp_update = """
    ALTER PROCEDURE dbo.sp_update_patient
        @patient_id     INT,
        @cedula         NVARCHAR(50)  = NULL,
        @name           NVARCHAR(200) = NULL,
        @dob            DATE          = NULL,
        @gender         NVARCHAR(20)  = NULL,
        @phone          NVARCHAR(30)  = NULL,
        @blood_type     NVARCHAR(5)   = NULL,
        @photo_url      NVARCHAR(MAX) = NULL,
        @birth_country   NVARCHAR(100) = NULL,
        @birth_city      NVARCHAR(100) = NULL,
        @residence_country NVARCHAR(100) = NULL,
        @residence_city  NVARCHAR(100) = NULL,
        @ethnicity       NVARCHAR(100) = NULL,
        @past_surgeries  NVARCHAR(MAX) = NULL,
        @education_level NVARCHAR(100) = NULL,
        @occupation      NVARCHAR(100) = NULL,
        @marital_status  NVARCHAR(50)  = NULL
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE dbo.patients
        SET cedula            = COALESCE(@cedula, cedula),
            name              = COALESCE(@name, name),
            dob               = COALESCE(@dob, dob),
            gender            = COALESCE(@gender, gender),
            phone             = COALESCE(@phone, phone),
            blood_type        = COALESCE(@blood_type, blood_type),
            photo_url         = COALESCE(@photo_url, photo_url),
            birth_country     = COALESCE(@birth_country, birth_country),
            birth_city        = COALESCE(@birth_city, birth_city),
            residence_country = COALESCE(@residence_country, residence_country),
            residence_city    = COALESCE(@residence_city, residence_city),
            ethnicity         = COALESCE(@ethnicity, ethnicity),
            past_surgeries    = COALESCE(@past_surgeries, past_surgeries),
            education_level   = COALESCE(@education_level, education_level),
            occupation        = COALESCE(@occupation, occupation),
            marital_status    = COALESCE(@marital_status, marital_status),
            updated_at        = SYSUTCDATETIME()
        WHERE id = @patient_id;
        SELECT @@ROWCOUNT AS rows_affected;
    END
    """
    try:
        cursor.execute(recreate_sp_update)
        conn.commit()
        print("SP dbo.sp_update_patient altered successfully.")
    except Exception as e:
        print(f"Error altering SP sp_update_patient: {e}")
        cursor.close()
        conn.close()
        return

    cursor.close()
    conn.close()
    print("Demographics and reporting fields database migration completed successfully.")
