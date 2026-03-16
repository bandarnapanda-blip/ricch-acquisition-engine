import database
leads = database.db.fetch_leads()
print("--START--")
for l in leads:
    if l.get('opportunity_score', 0) >= 60:
        print(f"{l.get('business_name')}|{l.get('demo_link')}")
print("--END--")
