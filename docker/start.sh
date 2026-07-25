#!/bin/sh
set -eu

python -c "from database import initialize_database; initialize_database()" || echo "⚠️ Advertencia: No se pudo inicializar la base de datos (se omitira por ahora)."

exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers "${GUNICORN_WORKERS:-2}" --threads "${GUNICORN_THREADS:-4}" --timeout "${GUNICORN_TIMEOUT:-120}" app:app
