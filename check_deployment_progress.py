from database import db

leads = db.fetch_leads()
with_demo = [l for l in leads if l.get('demo_link')]
print(f"Total Leads: {len(leads)}")
print(f"Leads with Demo Link: {len(with_demo)}")

for l in with_demo[-5:]:
    print(f"- {l.get('business_name')} | Demo: {l.get('demo_link')}")
