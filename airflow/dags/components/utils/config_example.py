# Example configuration file for Supabase Storage
# Copy this to config.py and fill in your actual credentials

import os

# Supabase Configuration
# You can set these as environment variables or directly here
SUPABASE_URL = os.getenv('SUPABASE_URL', 'your-supabase-url-here')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'your-service-role-key-here')

# Storage Configuration
STORAGE_BUCKET = 'ml-pipeline-storage'

# Example environment variables you can set:
# export SUPABASE_URL="https://your-project.supabase.co"
# export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"