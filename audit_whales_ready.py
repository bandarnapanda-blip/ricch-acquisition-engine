from database import db
whales = db.fetch_leads({'opportunity_score': 'gte.75'})
needs_shadow = [w for w in whales if not w.get('demo_link')]
print(f"Total Whales: {len(whales)}")
print(f"Needs Shadow Site: {len(needs_shadow)}")
if needs_shadow:
    print("Example Lead IDs needing shadow sites:")
    for w in needs_shadow[:5]:
        print(f" - {w['id']} ({w.get('business_name', 'Unknown')})")
