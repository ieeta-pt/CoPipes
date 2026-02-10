#!/bin/bash
set -e

echo "🔁 Waiting for Postgres to be available..."
while ! pg_isready -h supabase-db -p 5432 > /dev/null 2>&1; do
  sleep 1
done
echo "✅ Postgres is ready."

echo "📦 Migrating Airflow DB..."
airflow db migrate

# Check if admin user exists
echo "👤 Creating admin user (if needed)..."
airflow users list | grep -q "$AIRFLOW_ADMIN_USERNAME" || airflow users create \
  --username "$AIRFLOW_ADMIN_USERNAME" \
  --password "$AIRFLOW_ADMIN_PASSWORD" \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email "$AIRFLOW_ADMIN_EMAIL"

echo "✅ Initialization complete."
