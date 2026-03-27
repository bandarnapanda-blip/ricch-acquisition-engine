from database import db
leads = db.fetch_leads()
whales = [l for l in leads if l.get('opportunity_score', 0) >= 75]
sorted_whales = sorted(whales, key=lambda x: x.get('opportunity_score', 0), reverse=True)
for l in sorted_whales[50:135]:
    print(f"{l.get('business_name')} - {l.get('status')} - {l.get('demo_link')}")
