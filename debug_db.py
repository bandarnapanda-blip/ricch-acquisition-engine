import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def test_connection():
    print(f"URL: {SUPABASE_URL}")
    print(f"Key exists: {'Yes' if SUPABASE_KEY else 'No'}")
    
    # Test Leads
    print("\n[Testing Leads Table]")
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/leads?select=count", headers=headers)
        print(f"Leads Status: {r.status_code}")
        if r.status_code != 200:
            print(f"Leads Error: {r.text}")
    except Exception as e:
        print(f"Leads Exception: {e}")

    # Test Tasks
    print("\n[Testing Tasks Table]")
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/tasks?select=count", headers=headers)
        print(f"Tasks Status: {r.status_code}")
        if r.status_code != 200:
            print(f"Tasks Error: {r.text}")
    except Exception as e:
        print(f"Tasks Exception: {e}")

if __name__ == "__main__":
    test_connection()
