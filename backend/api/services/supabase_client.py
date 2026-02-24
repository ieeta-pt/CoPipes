from supabase import create_client, Client
from config import SUPABASE_PUBLIC_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY

# Use service role key for all operations (including auth) since anon key has restricted permissions
supabase: Client = create_client(SUPABASE_PUBLIC_URL, SUPABASE_SERVICE_ROLE_KEY)

# Service role client with admin privileges for operations requiring bypassing RLS
supabase_admin: Client = create_client(SUPABASE_PUBLIC_URL, SUPABASE_SERVICE_ROLE_KEY)