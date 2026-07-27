"""
Supabase client initialization module.
Loads environment variables and exposes a configured Supabase client instance.
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your_anon_key")


def get_supabase_client() -> Client:
    """Creates and returns a Supabase Client instance."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase: Client = get_supabase_client()
