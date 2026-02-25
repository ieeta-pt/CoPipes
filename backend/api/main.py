import os
import re

from fastapi import FastAPI, UploadFile, File

from database import SupabaseClient
from fastapi.middleware.cors import CORSMiddleware
from config import FRONTEND_URL

app = FastAPI()

# Add CORS middleware FIRST before including routers
# Build allowed origins - filter out None values
allowed_origins = []
if FRONTEND_URL:
    allowed_origins.append(FRONTEND_URL)
allowed_origins.extend([
    "http://localhost:3000",
])

# Allow GitHub Codespaces URLs with regex pattern
allow_origin_regex = r"https://.*\.app\.github\.dev"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers AFTER middleware setup
from routes import workflows, auth, organizations

app.include_router(workflows.router)
app.include_router(auth.router)
app.include_router(organizations.router)
supabase = SupabaseClient()

#AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
#AIRFLOW_ADMIN_USERNAME = os.getenv("AIRFLOW_ADMIN_USERNAME")
#AIRFLOW_ADMIN_PASSWORD = os.getenv("AIRFLOW_ADMIN_PASSWORD")
#
#API_AUTH = auth = (AIRFLOW_ADMIN_USERNAME, AIRFLOW_ADMIN_PASSWORD)


        