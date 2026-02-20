import os

from dotenv import load_dotenv


IS_CODESPACES = os.getenv("CODESPACES", "false").lower() == "true"

# In Codespaces, use environment variables (e.g., GitHub Codespaces secrets).
# Locally, allow values from .env as a fallback without overriding existing env vars.
if not IS_CODESPACES:
    load_dotenv(override=False)

# Supabase Configuration
SUPABASE_PUBLIC_URL = os.getenv("SUPABASE_PUBLIC_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_KEY)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_HOURS = 24

# Frontend URL for redirects
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Airflow Configuration
AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_ADMIN_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_ADMIN_PASSWORD")