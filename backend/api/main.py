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

#AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
#AIRFLOW_ADMIN_USERNAME = os.getenv("AIRFLOW_ADMIN_USERNAME")
#AIRFLOW_ADMIN_PASSWORD = os.getenv("AIRFLOW_ADMIN_PASSWORD")
#
#API_AUTH = auth = (AIRFLOW_ADMIN_USERNAME, AIRFLOW_ADMIN_PASSWORD)



origins = FRONTEND_URL

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)





        