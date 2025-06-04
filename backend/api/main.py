import os

from fastapi import FastAPI, UploadFile, File

from routes import workflows, auth, organizations

from database import SupabaseClient 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(workflows.router)
app.include_router(auth.router)
app.include_router(organizations.router)
supabase = SupabaseClient()

AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")

API_AUTH = auth = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)



origins = [
    "https://localhost:3000",
    "https://127.0.0.1:3000",
    "http://localhost:3000",  # Development fallback
    "http://127.0.0.1:3000",  # Development fallback
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)





        