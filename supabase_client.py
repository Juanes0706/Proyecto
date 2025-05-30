from supabase import create_client
from supabase_config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

# Use service role key for backend operations to bypass RLS
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
