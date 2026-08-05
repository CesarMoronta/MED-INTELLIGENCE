from database.connection import (
    get_connection,
    get_db_cursor,
    close_all_thread_connections,
    rows_to_dicts,
    _fmt_date,
    SQLSERVER_CONN,
    MAX_LOGIN_ATTEMPTS,
    LOCKOUT_MINUTES
)

from database.users import (
    create_user,
    verify_user,
    update_user,
    update_user_photo,
    update_user_subscription,
    list_users,
    get_user_by_id,
    get_user_by_username,
    is_account_locked
)

from database.patients import (
    add_patient,
    update_patient,
    delete_patient,
    get_patient,
    list_patients,
    mark_patient_deceased,
    get_patient_vitals_history,
    get_patient_red_alerts,
    add_patient_document,
    delete_patient_document,
    get_patient_document,
    list_patient_documents
)

from database.appointments import (
    create_appointment,
    update_appointment,
    update_appointment_status,
    reschedule_appointment,
    list_appointments,
    get_appointment,
    check_appointment_clash,
    confirm_appointment,
    mark_patient_arrived
)

from database.visits import (
    create_visit,
    get_visit,
    list_visits,
    get_visit_with_details,
    save_visit_tests,
    get_visit_tests,
    get_medical_tests,
    add_prescription,
    get_prescriptions,
    get_prescriptions_for_visit,
    get_active_medications,
    add_record,
    list_records,
    list_clinical_history,
    get_clinical_report,
    save_diagnosis,
    get_waiting_room
)

from database.billing import (
    create_invoice,
    list_pending_bills,
    list_invoices,
    get_invoice_by_id,
    save_patient_billing_info,
    get_patient_billing_info,
    get_patient_account_statement
)

from database.reports import (
    get_dashboard_stats,
    get_doctor_dashboard_stats,
    get_dashboard_charts,
    get_report_visits,
    get_report_waiting_time,
    get_report_diagnoses_summary,
    get_report_doctor_activity,
    get_report_billing,
    get_report_recurrent_patients,
    get_report_prescriptions,
    get_report_model_performance,
    get_report_ai_comparison,
    get_report_patient,
    get_report_audit,
    get_audit_logs,
    log_audit_action,
    get_epidemiology_report
)

from database.settings import (
    get_all_clinic_settings,
    set_clinic_settings,
    get_clinic_name,
    set_clinic_name,
    create_notification,
    get_notifications,
    get_unread_count,
    mark_notification_read,
    mark_all_notifications_read,
    get_parameters,
    save_parameters,
    reset_parameters,
    initialize_database,
    ensure_reports_views,
    get_clinic_working_hours,
    save_clinic_working_hours,
    get_doctor_blocked_slots,
    add_doctor_blocked_slot,
    delete_doctor_blocked_slot
)
