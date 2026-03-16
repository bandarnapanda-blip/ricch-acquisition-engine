from database import db

leads = db.fetch_leads()
no_demo = [l for l in leads if not l.get('demo_link')]
no_biz_name = [l for l in leads if not l.get('business_name')]

print(f"Total Leads: {len(leads)}")
print(f"Leads without Demo Link: {len(no_demo)}")
print(f"Leads without Business Name: {len(no_biz_name)}")

print("\nSample Leads without Demo Link:")
for l in no_demo[:10]:
    name = l.get('business_name') or "MISSING NAME"
    niche = l.get('niche') or "MISSING NICHE"
    city = l.get('city') or "MISSING CITY"
    score = l.get('opportunity_score') or 0
    print(f"- {name} ({niche}) in {city}, score: {score}")
