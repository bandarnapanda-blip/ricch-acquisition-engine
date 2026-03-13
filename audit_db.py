import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def audit_leads():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    endpoint = f"{SUPABASE_URL}/rest/v1/leads?select=*"
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        leads = response.json()
        
        print(f"Auditing {len(leads)} leads...")
        for lead in leads:
            for key, value in lead.items():
                if isinstance(value, str) and ("ingine" in value.lower() or "there v" in value.lower()):
                    print(f"\n[CORRUPTION FOUND] Lead ID: {lead['id']}")
                    print(f"Key: {key}")
                    print(f"Value: {value}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_leads()
