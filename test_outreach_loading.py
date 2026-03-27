import asyncio
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def test_fetch():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    print("--- OUTREACH QUEUE AUDIT ---")
    
    # 1. Diamond
    diamond_endpoint = f"{SUPABASE_URL}/rest/v1/leads?status=eq.Diamond%20Audit%20Ready&select=id,business_name"
    res = requests.get(diamond_endpoint, headers=headers)
    diamond_leads = res.json()
    print(f"Diamond Audit Ready: {len(diamond_leads)}")
    
    # 2. Shadow Site
    shadow_endpoint = f"{SUPABASE_URL}/rest/v1/leads?status=eq.Shadow%20Site%20Ready&select=id,business_name"
    res = requests.get(shadow_endpoint, headers=headers)
    shadow_leads = res.json()
    print(f"Shadow Site Ready (The 763): {len(shadow_leads)}")
    
    # 3. Fresh New
    new_endpoint = f"{SUPABASE_URL}/rest/v1/leads?status=eq.New&select=id,business_name"
    res = requests.get(new_endpoint, headers=headers)
    new_leads = res.json()
    print(f"Fresh New leads: {len(new_leads)}")
    
    total = len(diamond_leads) + len(shadow_leads) + len(new_leads)
    print(f"\nTOTAL PENDING REACH: {total}")
    
    if total > 0:
        print("\nTOP PRIORITY SAMPLES:")
        all_leads = diamond_leads + shadow_leads
        for l in all_leads[:5]:
            print(f"- {l.get('business_name')}")

if __name__ == "__main__":
    asyncio.run(test_fetch())
