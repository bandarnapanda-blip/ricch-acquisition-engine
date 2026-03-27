import os
import requests
import json
import time
from database import db
from dotenv import load_dotenv

load_dotenv()

GITHUB_BASE_URL = "https://bandarnapanda-blip.github.io/ricch-acquisition-engine/demo/"

def get_slug(name, city):
    safe_name = "".join(x for x in name if x.isalnum() or x == ' ').strip().replace(' ', '-')
    safe_city = "".join(x for x in city if x.isalnum() or x == ' ').strip().replace(' ', '-')
    return f"{safe_name.lower()}-{safe_city.lower()}"

def verify_url(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("--- SHADOW SITE RECOVERY ENGINE ---")
    
    # Target 1: Mismatched Status
    all_ready = db.fetch_table('leads', filters={'status': 'eq.Shadow Site Ready'}, limit=10000)
    mismatched = [l for l in all_ready if not l.get('demo_link')]
    
    # Target 2: Contacted Whales missing links (High Risk)
    all_contacted_whales = db.fetch_table('leads', filters={'status': 'eq.Contacted', 'opportunity_score': 'gte.75'}, limit=10000)
    contacted_missing = [l for l in all_contacted_whales if not l.get('demo_link')]
    
    if not mismatched: mismatched = []
    if not contacted_missing: contacted_missing = []
    
    combined = mismatched + contacted_missing
    # Remove duplicates by ID
    targets = {}
    for t in combined:
        targets[t['id']] = t
    
    targets = list(targets.values())
    
    print(f"Identified {len(targets)} leads needing link synchronization.")
    
    sync_count = 0
    for lead in targets:
        name = lead.get('business_name')
        city = lead.get('city')
        website = lead.get('website')
        
        if not name or name.lower() in ["", "none", "unknown", "unknown business"]:
            if website:
                name = website.split("//")[-1].split("/")[0].replace("www.", "").split(".")[0].capitalize()
            else:
                continue
                
        if not city:
            city = "Your City"

        slug = get_slug(name, city)
        potential_url = f"{GITHUB_BASE_URL}{slug}.html"
        
        print(f"Checking: {name} -> {potential_url}...")
        if verify_url(potential_url):
            print(f"  [FOUND] Link is live. Backfilling...")
            db.update_lead(lead['id'], {"demo_link": potential_url})
            sync_count += 1
        else:
            # Try a second fallback: niche based slug if the first one failed
            niche = lead.get('niche', 'General')
            safe_niche = "".join(x for x in niche if x.isalnum() or x == ' ').strip().replace(' ', '-')
            safe_city = "".join(x for x in city if x.isalnum() or x == ' ').strip().replace(' ', '-')
            alt_slug = f"{safe_niche.lower()}-{safe_city.lower()}"
            alt_url = f"{GITHUB_BASE_URL}{alt_slug}.html"
            
            if verify_url(alt_url):
                print(f"  [FOUND ALT] Link is live. Backfilling...")
                db.update_lead(lead['id'], {"demo_link": alt_url})
                sync_count += 1
            else:
                print(f"  [FAILED] No reachable site found for {name}.")
        
        time.sleep(0.5)

    print(f"\nSync Complete. Restored {sync_count} shadow site links.")

if __name__ == "__main__":
    main()
