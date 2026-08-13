import os
import pyodbc
import threading
from contextlib import contextmanager

# ─── Cadena de conexión ───────────────────────────────────────────────────────
SQLSERVER_CONN = os.environ.get(
    "SQLSERVER_CONN",
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER=ASUS_GAMING_CM;DATABASE=MedIntelligence;Trusted_Connection=yes;Encrypt=no"
)

MAX_LOGIN_ATTEMPTS = 5    # Intentos antes del bloqueo
LOCKOUT_MINUTES    = 15   # Minutos de bloqueo

_local_data = threading.local()

def get_connection() -> pyodbc.Connection:
    conn_str = os.environ.get("SQLSERVER_CONN", SQLSERVER_CONN)
    if "APP=" not in conn_str.upper() and "APPLICATION NAME=" not in conn_str.upper():
        conn_str += ";APP=MedIntelligenceApp"
    conn = pyodbc.connect(conn_str, autocommit=True)
    if not hasattr(_local_data, "connections"):
        _local_data.connections = []
    _local_data.connections.append(conn)
    return conn

@contextmanager
def get_db_cursor():
    """
    Context manager para operaciones de base de datos seguras.
    Garantiza el cierre del cursor y la conexión al finalizar.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

def close_all_thread_connections():
    """
    Cierra de forma segura todas las conexiones de base de datos creadas
    en el hilo actual. Se utiliza en el teardown de Flask para evitar fugas.
    """
    if hasattr(_local_data, "connections"):
        for conn in _local_data.connections:
            try:
                conn.close()
            except Exception:
                pass
        _local_data.connections.clear()

def rows_to_dicts(cursor: pyodbc.Cursor) -> list:
    if cursor.description is None:
        return []
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def _fmt_date(val) -> str | None:
    """Convierte objetos datetime/date a string ISO."""
    if val is None:
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return str(val)
