import os
import time
from database import db
from dotenv import load_dotenv

load_dotenv()

def find_candidate_emails(website, business_name=None):
    """Generate typical email candidates for a domain."""
    if not website or '.' not in website:
        return []
    domain = website.split('//')[-1].split('/')[0].replace('www.', '')
    
    # Strat A: Common generic aliases (Lower Priority)
    generic_prefixes = ['info', 'contact', 'office', 'support', 'sales', 'hello']
    candidates = [f"{p}@{domain}" for p in generic_prefixes]
    
    # Strat B: Personnel Construction (Higher Priority)
    # If business name is 'John Doe Law', we try 'john@', 'jd@' etc.
    if business_name:
        clean_name = str(business_name).replace('None', '').strip().lower()
        # Remove common business suffixes
        for suffix in ["law", "llc", "inc", "corp", "group", "firm", "dentistry", "dental", "solar", "office", "center", "expert"]:
            clean_name = clean_name.replace(suffix, "").strip()
            
        parts = clean_name.split()
        if len(parts) >= 2:
            first, last = parts[0], parts[1]
            candidates.insert(0, f"{first}@{domain}")
            candidates.insert(1, f"{first[0]}{last}@{domain}")
            candidates.insert(2, f"{first}.{last}@{domain}")
        elif len(parts) == 1 and len(parts[0]) > 2:
            candidates.insert(0, f"{parts[0]}@{domain}")
            
    return candidates

def enrich_whales(limit=20):
    print("--- VEX ENRICHMENT: HIGH-AUTHORITY DATA SYNC ---")
    print(f"--- ANALYZING TOP {limit} WHALES FOR ESCALATED DATA ---")
    print("---------------------------------------------------------")
    
    # PULSE Check: Fetching leads with score >= 75 only to avoid 3000+ lead data dump
    leads = db.fetch_leads({"opportunity_score": "gte.75"})
    
    # Target leads missing valid candidate lists
    whales = [
        l for l in leads 
        if (not l.get('candidate_emails') or len(l.get('candidate_emails', [])) == 0)
    ]
    
    targets = whales[:limit]
    print(f"Targeting {len(targets)} Whales for enrichment.")
    
    success = 0
    for lead in targets:
        lid = lead.get('id')
        website = lead.get('website', '')
        biz = lead.get('business_name')
        
        # SKIP if biz is generic or missing (prevents 'valued@' bounces)
        if not biz or biz.lower() in ["valued client", "none", "", "lead", "client"]:
            print(f"[SKIP] Lead {lid} has no real business name. Skipping construction.")
            continue
            
        candidates = find_candidate_emails(website, biz)
        if not candidates:
            continue
            
        print(f"[*] Processing {biz} ({website})...")
        print(f"    [CANDIDATES] {', '.join(candidates[:3])}...")
        
        # Update the DB with the candidates list
        db.update_lead(lid, {
            "candidate_emails": candidates,
            "status": "Shadow Site Ready"
        })
        
        db.push_log("Vex Enrichment", f"Enriched lead {biz} with {len(candidates)} candidates.")
        success += 1

    print(f"\nENRICHMENT COMPLETE: {success} Whales enriched with personnel candidates.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Enrich elite whales with personnel email candidates")
    parser.add_argument("--limit", type=int, default=20, help="Number of leads to enrich")
    args = parser.parse_args()
    
    enrich_whales(limit=args.limit)
