import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

filename = "fresh_render_test.html"
bucket = "landing-pages"

# Generate a signed URL with a long expiration (1 year = 31536000 seconds)
# Or even longer if allowed
try:
    res = supabase.storage.from_(bucket).create_signed_url(filename, 31536000)
    print(f"SIGNED_URL: {res.get('signedURL')}")
except Exception as e:
    print(f"ERROR: {e}")
