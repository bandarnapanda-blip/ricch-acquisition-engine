import os
import requests
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def test_conn():
    endpoint = f"{SUPABASE_URL}/rest/v1/leads?select=*&limit=1"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    print(f"Testing connection to {endpoint}...")
    try:
        resp = requests.get(endpoint, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    test_conn()
