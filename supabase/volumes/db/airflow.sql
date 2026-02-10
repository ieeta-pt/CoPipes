-- Create airflow database and user for Airflow integration
-- This script runs during Supabase Postgres initialization

-- Create the airflow user
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'airflow') THEN
        CREATE ROLE airflow WITH LOGIN PASSWORD 'airflow';
    END IF;
END
$$;

-- Create the airflow database
SELECT 'CREATE DATABASE airflow OWNER airflow'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
