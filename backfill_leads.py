import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def backfill():
    print("🚀 Starting Idempotent Backfill for Lead Analytics...")
    
    # Fetch all leads
    endpoint = f"{SUPABASE_URL}/rest/v1/leads?select=*"
    try:
        response = requests.get(endpoint, headers=get_headers())
        response.raise_for_status()
        leads = response.json()
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return

    print(f"Found {len(leads)} leads to process.")
    
    success = 0
    for lead in leads:
        patch = {}
        
        # 1. Set default last_stage if missing
        if not lead.get('last_stage'):
            if lead.get('status') == 'Closed': patch['last_stage'] = 'closed'
            elif lead.get('demo_link'): patch['last_stage'] = 'demo_sent'
            elif lead.get('replied_at'): patch['last_stage'] = 'replied'
            elif lead.get('email_sent_at'): patch['last_stage'] = 'emailed'
            else: patch['last_stage'] = 'scraped'

        # 2. Set default monthly_value based on niche if 0
        if not lead.get('monthly_value') or lead['monthly_value'] == 0:
            niche = lead.get('niche', '')
            if niche == "Solar Energy": patch["monthly_value"] = 500
            elif niche == "Personal Injury Law": patch["monthly_value"] = 800
            else: patch["monthly_value"] = 499

        if patch:
            update_url = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead['id']}"
            try:
                requests.patch(update_url, headers=get_headers(), json=patch)
                success += 1
            except Exception as e:
                print(f"Error updating lead {lead['id']}: {e}")

    print(f"✅ Backfill complete. {success} leads updated.")

if __name__ == "__main__":
    backfill()
