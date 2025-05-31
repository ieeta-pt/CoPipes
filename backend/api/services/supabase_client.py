from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY

# Standard client with anon key for regular operations
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Service role client with admin privileges for operations requiring bypassing RLS
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)