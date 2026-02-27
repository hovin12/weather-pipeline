#!/bin/bash
set -e

# ─────────────────────────────────────────────
# 1. Install Python dependencies
# ─────────────────────────────────────────────
if [ -f /requirements.txt ]; then
  echo ">>> Installing requirements..."
  pip install --no-cache-dir -r /requirements.txt
fi

# ─────────────────────────────────────────────
# 2. Wait for Postgres to be ready
# ─────────────────────────────────────────────
echo ">>> Waiting for Postgres..."
until airflow db check 2>/dev/null; do
  sleep 2
done
echo ">>> Postgres is ready."

# ─────────────────────────────────────────────
# 3. Run DB migrations (idempotent)
# ─────────────────────────────────────────────
echo ">>> Running airflow db migrate..."
airflow db migrate

# ─────────────────────────────────────────────
# 4. Create admin user (idempotent)
# ─────────────────────────────────────────────
# Required .env vars: AIRFLOW_ADMIN_USER, AIRFLOW_ADMIN_PASSWORD,
#                     AIRFLOW_ADMIN_FIRSTNAME, AIRFLOW_ADMIN_LASTNAME,
#                     AIRFLOW_ADMIN_EMAIL
if [ -n "${AIRFLOW_ADMIN_USER}" ]; then
  echo ">>> Creating/verifying admin user..."
  airflow users create \
    --username  "${AIRFLOW_ADMIN_USER}" \
    --password  "${AIRFLOW_ADMIN_PASSWORD}" \
    --firstname "${AIRFLOW_ADMIN_FIRSTNAME:-Admin}" \
    --lastname  "${AIRFLOW_ADMIN_LASTNAME:-User}" \
    --role      Admin \
    --email     "${AIRFLOW_ADMIN_EMAIL:-admin@example.com}" \
    2>&1 | grep -v "already exists" || true
fi

# ─────────────────────────────────────────────
# 5. Create connections (idempotent)
# ─────────────────────────────────────────────
# POSTGRES_CONN example – reads individual vars from .env so the URI
# is never stored as plain text in the image.
echo ">>> Setting up connections..."

airflow connections add 'POSTGRES_CONN' \
  --conn-type    postgres \
  --conn-host    "${POSTGRES_HOST:-postgres}" \
  --conn-schema  "${POSTGRES_DB:-airflow}" \
  --conn-login   "${POSTGRES_USER:-airflow}" \
  --conn-password "${POSTGRES_PASSWORD:-airflow}" \
  --conn-port    "${POSTGRES_PORT:-5432}" \
  2>&1 | grep -v "already exist" || true

airflow connections add 'CURRENT_WEATHER_API' \
  --conn-type    HTTP \
  --conn-host    "${API_HOST:-api.openweathermap.org/data/2.5}" \
  --conn-schema  "${POSTGRES_DB:-https}" \
  --conn-password "${API_KEY}" \
  2>&1 | grep -v "already exist" || true

# ─────────────────────────────────────────────
# 7. Hand off to the requested Airflow component
# ─────────────────────────────────────────────
echo ">>> Starting: $@"
exec airflow "$@"
