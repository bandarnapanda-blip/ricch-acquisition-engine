from database import db
print("Fetching leads...")
leads = db.fetch_leads(limit=5)
print(f"Fetched {len(leads)} leads.")
for l in leads:
    print(f" - {l.get('id')} | Score: {l.get('opportunity_score')}")
