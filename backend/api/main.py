import os

from fastapi import FastAPI, UploadFile, File

from routes import workflows, auth, organizations

from database import SupabaseClient
from fastapi.middleware.cors import CORSMiddleware
from config import FRONTEND_URL

app = FastAPI()
app.include_router(workflows.router)
app.include_router(auth.router)
app.include_router(organizations.router)
supabase = SupabaseClient()

#AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
#AIRFLOW_ADMIN_USERNAME = os.getenv("AIRFLOW_ADMIN_USERNAME")
#AIRFLOW_ADMIN_PASSWORD = os.getenv("AIRFLOW_ADMIN_PASSWORD")
#
#API_AUTH = auth = (AIRFLOW_ADMIN_USERNAME, AIRFLOW_ADMIN_PASSWORD)



origins = [FRONTEND_URL] if FRONTEND_URL else ["*"]
print(f"Allowed CORS origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)





        