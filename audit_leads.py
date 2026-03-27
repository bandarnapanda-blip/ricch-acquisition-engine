import sys
import os
import json
from database import db

def audit():
    print("--- LEAD AUDIT ---")
    leads = db.fetch_leads()
    print(f"Total Leads: {len(leads)}")
    
    whales = [l for l in leads if l.get('opportunity_score', 0) >= 75]
    warm = [l for l in leads if 60 <= l.get('opportunity_score', 0) < 75]
    cold = [l for l in leads if l.get('opportunity_score', 0) < 60]
    
    print(f"Whales (75+):  {len(whales)}")
    print(f"Warm (60-74):  {len(warm)}")
    print(f"Cold (<60):    {len(cold)}")
    
    # Top 5 Whales
    print("\n--- TOP 5 WHALES ---")
    sorted_whales = sorted(whales, key=lambda x: x.get('opportunity_score', 0), reverse=True)
    for i, lead in enumerate(sorted_whales[:5]):
        print(f"{i+1}. {lead.get('business_name')} ({lead.get('city')}) - Score: {lead.get('opportunity_score')}")
        print(f"   Niche: {lead.get('niche')}")
        print(f"   Status: {lead.get('status')}")
        print(f"   URL: {lead.get('demo_link') or 'Pending...'}")

if __name__ == "__main__":
    audit()
