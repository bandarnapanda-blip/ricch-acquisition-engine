import json
from database import db
from api import map_lead

print("Starting metrics test...")
raw_leads = db.fetch_leads()
print(f"Fetched {len(raw_leads)} raw leads.")

print("Mapping leads...")
leads = [map_lead(l) for l in raw_leads]
print(f"Mapped {len(leads)} leads.")

print("Calculating metrics...")
total_leads = len(leads)
whale_leads = len([l for l in leads if l["opportunityScore"] >= 75])
total_leakage = sum([l["revenueLoss"] for l in leads])
print(f"Calculated basic metrics. Whale count: {whale_leads}")

contacted = [l for l in leads if l["status"] == 'Contacted']
replies = [l for l in leads if l["status"] == 'Replied']
reply_rate = (len(replies) / len(contacted) * 100) if contacted else 0
print(f"Reply rate: {reply_rate}%")

print("Metrics test complete.")
