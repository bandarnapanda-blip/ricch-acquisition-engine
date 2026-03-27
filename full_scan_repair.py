import os
import time
import requests
import json
from urllib.parse import urlparse
from database import db

def get_domain(url):
    if not url: return None
    try:
        if not url.startswith('http'): url = 'https://' + url
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'): domain = domain[4:]
        return domain
    except:
        return None

def repair_name(website):
    domain = get_domain(website)
    if domain:
        name = domain.split('.')[0]
        return name.capitalize()
    return "Business Owner"

def run_full_repair():
    print("--- RI2CH FULL SCAN & REPAIR ENGINE ---")
    
    # 1. Fetch ALL leads
    leads = db.fetch_table('leads', limit=10000)
    print(f"[*] Analyzing {len(leads)} leads...")
    
    # 2. De-duplication Cache
    domain_map = {} # domain -> list of leads
    placeholders = ["", "none", "unknown", "unknown business"]
    
    for l in leads:
        d = get_domain(l.get('website'))
        if not d: continue
        if d not in domain_map: domain_map[d] = []
        domain_map[d].append(l)

    # 3. Process Duplicates & Repairs
    processed_ids = set()
    to_delete = []
    
    for domain, dupes in domain_map.items():
        if len(dupes) > 1:
            print(f" [!] Duplicate found for {domain} ({len(dupes)} entries)")
            # Sort by priority: Contacted > Replied > Shadow Site Ready > New
            status_priority = {'Replied': 10, 'Contacted': 9, 'Shadow Site Ready': 8, 'New': 1}
            sorted_dupes = sorted(dupes, key=lambda x: status_priority.get(x.get('status'), 0), reverse=True)
            
            primary = sorted_dupes[0]
            others = sorted_dupes[1:]
            
            # Keep primary, merge others
            updates = {}
            for other in others:
                # Merge missing link
                if not primary.get('demo_link') and other.get('demo_link'):
                    primary['demo_link'] = other['demo_link']
                    updates['demo_link'] = other['demo_link']
                # Merge missing name
                if (not primary.get('business_name') or primary.get('business_name').lower() in placeholders) and other.get('business_name') and other.get('business_name').lower() not in placeholders:
                    primary['business_name'] = other['business_name']
                    updates['business_name'] = other['business_name']
                
                to_delete.append(other['id'])
            
            if updates:
                db.update_lead(primary['id'], updates)
                print(f"    [MERGED] Unified data for {primary.get('business_name') or domain}")

        # Individual Repair logic for the primary or single lead
        target = dupes[0]
        id_ = target['id']
        updates = {}
        
        # Repair missing name
        if not target.get('business_name') or target.get('business_name').lower() in placeholders:
            new_name = repair_name(target.get('website'))
            updates['business_name'] = new_name
            print(f"    [NAME] Repaired {id_} -> {new_name}")
            
        # Backfill missing link if status suggests it should have one
        if (target.get('status') in ['Shadow Site Ready', 'Contacted', 'Replied']) and not target.get('demo_link'):
            base_url = "https://bandarnapanda-blip.github.io/ricch-acquisition-engine/demo/"
            site_name = get_domain(target.get('website'))
            if site_name:
                site_name = site_name.split('.')[0]
                city = target.get('city', '').lower().replace(' ', '-')
                reconstructed = f"{base_url}{site_name}-{city}.html"
                
                # Verify reachable
                try:
                    head = requests.head(reconstructed, timeout=3)
                    if head.status_code == 200:
                        updates['demo_link'] = reconstructed
                        print(f"    [LINK] Backfilled link for {id_}")
                except:
                    pass
        
        # Sync Reply Status
        if target.get('replied_at') and target.get('status') != 'Replied':
            updates['status'] = 'Replied'
            print(f"    [STATUS] Forced 'Replied' for {id_}")

        if updates:
            db.update_lead(id_, updates)

    # 4. Cleanup Duplicates
    if to_delete:
        print(f"[*] Purging {len(to_delete)} duplicate lead entries...")
        # Since our db doesn't have a bulk delete leads yet, we'll do it sequentially or just mark them
        # For safety in this script, we'll just print them and update status to 'Archived_Duplicate'
        for rid in to_delete:
            db.update_lead(rid, {"status": "Archived_Duplicate"})

    print("--- REPAIR COMPLETE ---")

if __name__ == "__main__":
    run_full_repair()
