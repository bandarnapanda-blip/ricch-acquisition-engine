import json
from database import db
leads = db.fetch_leads({'id': 'eq.3ee9f5d7-84a3-4888-ba0b-692500fc6462'})
if leads:
    lead = leads[0]
    print(json.dumps(lead, indent=2))
else:
    print("Lead not found.")
