import os
import requests
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def check_table(table_name):
    endpoint = f"{SUPABASE_URL}/rest/v1/{table_name}?select=count"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    try:
        resp = requests.get(endpoint, headers=headers)
        if resp.status_code == 200:
            print(f"Table '{table_name}' EXISTS.")
            return True
        elif resp.status_code == 404:
            print(f"Table '{table_name}' NOT FOUND (404).")
            return False
        else:
            print(f"Error checking table '{table_name}': {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"Exception checking table '{table_name}': {e}")
        return False

if __name__ == "__main__":
    check_table("follow_up_queue")
    check_table("leads")
