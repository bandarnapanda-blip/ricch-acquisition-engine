from database import db
import json

try:
    print("Testing DB connection...")
    leads = db.fetch_leads()
    print(f"Fetched {len(leads)} leads.")
    if leads:
        print(f"Sample lead: {leads[0].get('business_name')}")
    
    logs = db.fetch_logs(limit=5)
    print(f"Fetched {len(logs)} logs.")
    
    count = db.get_count("leads")
    print(f"Total leads count: {count}")
    
except Exception as e:
    print(f"Connection failed: {e}")
