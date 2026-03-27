import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_ROLE_KEY = os.getenv("SERVICE_ROLE_KEY")

headers = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def clean():
    print("Fetching ALL leads with candidate_emails...")
    all_leads = []
    offset = 0
    limit = 1000
    while True:
        resp = requests.get(f"{SUPABASE_URL}/rest/v1/leads?select=id,candidate_emails&candidate_emails=neq.null&limit={limit}&offset={offset}", headers=headers)
        if resp.status_code != 200:
            print(f"Failed to fetch leads: {resp.status_code} {resp.text}")
            break
        chunk = resp.json()
        all_leads.extend(chunk)
        if len(chunk) < limit:
            break
        offset += limit

    print(f"Total leads with candidate_emails: {len(all_leads)}")

    count = 0
    for l in all_leads:
        emails = l.get("candidate_emails")
        if emails and isinstance(emails, list):
            data_str = json.dumps(emails).lower()
            if "valued" in data_str or "vclient" in data_str:
                new_emails = [e for e in emails if "valued" not in e.lower() and "vclient" not in e.lower()]
                patch_resp = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/leads?id=eq.{l['id']}", 
                    json={"candidate_emails": new_emails}, 
                    headers=headers
                )
                if patch_resp.status_code >= 400:
                    print(f"Failed to update {l['id']}: {patch_resp.text}")
                else:
                    count += 1
                    print(f"Cleaned {l['id']}: {emails} -> {new_emails}")

    print(f"Cleaned {count} leads.")

if __name__ == "__main__":
    clean()
