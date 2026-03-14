import sys
import os
sys.path.append('.')
from find_leads import scrape_query

def test():
    print("Initiating Search Diagnostic (Integrated find_leads logic)...")
    niche = "Solar Energy Installers"
    city = "Austin"
    query = f"{niche} in {city}"
    
    # This calls the real logic in find_leads.py
    leads = scrape_query(query, niche, city)
    print(f"RESULTS: Found {len(leads)} leads.")
    
    for i, lead in enumerate(leads[:10]):
        print(f"[{i+1}] {lead.get('website', 'N/A')}")

if __name__ == "__main__":
    test()
