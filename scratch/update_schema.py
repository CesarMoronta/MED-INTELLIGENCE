import re

with open('database_schema.txt', 'r', encoding='utf-8') as f:
    schema = f.read()

# Modify patients
patients_old = """        photo_url       NVARCHAR(MAX)       NULL,
        created_at      DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at      DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT PK_patients          PRIMARY KEY (id),"""
patients_new = """        photo_url       NVARCHAR(MAX)       NULL,
        vital_status    NVARCHAR(20)        NOT NULL DEFAULT 'Vivo',
        death_date      DATE                NULL,
        death_certificate_url NVARCHAR(MAX) NULL,
        death_notes     NVARCHAR(MAX)       NULL,
        created_at      DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at      DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT PK_patients          PRIMARY KEY (id),"""
schema = schema.replace(patients_old, patients_new)

patients_chk_old = """CONSTRAINT CK_patients_gender   CHECK (gender IN ('Masculino','Femenino','Otro')),"""
patients_chk_new = """CONSTRAINT CK_patients_gender   CHECK (gender IN ('Masculino','Femenino','Otro')),
        CONSTRAINT CK_patients_vital_status CHECK (vital_status IN ('Vivo', 'Fallecido')),"""
schema = schema.replace(patients_chk_old, patients_chk_new)

# Modify invoices
invoices_old = """        payment_method      NVARCHAR(20)        NOT NULL,
        ecf_id              NVARCHAR(100)       NULL,"""
invoices_new = """        payment_method      NVARCHAR(20)        NOT NULL,
        amount_paid         DECIMAL(10,2)       NOT NULL DEFAULT 0,
        balance_due         DECIMAL(10,2)       NOT NULL DEFAULT 0,
        due_date            DATE                NULL,
        ecf_id              NVARCHAR(100)       NULL,"""
schema = schema.replace(invoices_old, invoices_new)

# Modify vw_patients
vw_patients_old = """    p.photo_url,
    DATEDIFF"""
vw_patients_new = """    p.photo_url,
    p.vital_status,
    p.death_date,
    p.death_certificate_url,
    p.death_notes,
    DATEDIFF"""
schema = schema.replace(vw_patients_old, vw_patients_new)

# Modify sp_create_patient
sp_create_old = """    @photo_url      NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.patients (cedula, name, dob, gender, phone, blood_type, registered_by, photo_url)
    VALUES (@cedula, @name, @dob, @gender, @phone, @blood_type, @registered_by, @photo_url);"""
sp_create_new = """    @photo_url      NVARCHAR(MAX) = NULL,
    @vital_status   NVARCHAR(20)  = 'Vivo',
    @death_date     DATE          = NULL,
    @death_certificate_url NVARCHAR(MAX) = NULL,
    @death_notes    NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.patients (cedula, name, dob, gender, phone, blood_type, registered_by, photo_url, vital_status, death_date, death_certificate_url, death_notes)
    VALUES (@cedula, @name, @dob, @gender, @phone, @blood_type, @registered_by, @photo_url, @vital_status, @death_date, @death_certificate_url, @death_notes);"""
schema = schema.replace(sp_create_old, sp_create_new)

# Modify sp_update_patient
sp_update_old1 = """    @photo_url  NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE dbo.patients
    SET cedula        = COALESCE(@cedula, cedula),
        name          = COALESCE(@name, name),
        dob           = COALESCE(@dob, dob),
        gender        = COALESCE(@gender, gender),
        phone         = COALESCE(@phone, phone),
        blood_type    = COALESCE(@blood_type, blood_type),
        photo_url     = COALESCE(@photo_url, photo_url),
        updated_at    = SYSUTCDATETIME()
    WHERE id = @patient_id;"""
sp_update_new1 = """    @photo_url  NVARCHAR(MAX) = NULL,
    @vital_status           NVARCHAR(20)  = NULL,
    @death_date             DATE          = NULL,
    @death_certificate_url  NVARCHAR(MAX) = NULL,
    @death_notes            NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE dbo.patients
    SET cedula        = COALESCE(@cedula, cedula),
        name          = COALESCE(@name, name),
        dob           = COALESCE(@dob, dob),
        gender        = COALESCE(@gender, gender),
        phone         = COALESCE(@phone, phone),
        blood_type    = COALESCE(@blood_type, blood_type),
        photo_url     = COALESCE(@photo_url, photo_url),
        vital_status  = COALESCE(@vital_status, vital_status),
        death_date    = COALESCE(@death_date, death_date),
        death_certificate_url = COALESCE(@death_certificate_url, death_certificate_url),
        death_notes   = COALESCE(@death_notes, death_notes),
        updated_at    = SYSUTCDATETIME()
    WHERE id = @patient_id;"""
schema = schema.replace(sp_update_old1, sp_update_new1)

with open('database_schema.txt', 'w', encoding='utf-8') as f:
    f.write(schema)
print("database_schema.txt updated.")
