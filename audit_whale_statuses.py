from database import db
leads = db.fetch_leads()
whales = [l for l in leads if l.get('opportunity_score', 0) >= 75]
status_counts = {}
for w in whales:
    s = w.get('status', 'Unknown')
    status_counts[s] = status_counts.get(s, 0) + 1
print(f"Total Whales: {len(whales)}")
print(f"Status Counts: {status_counts}")
print("Example Whales with 'Contacted' status:")
for w in whales:
    if w.get('status') == 'Contacted':
        print(f" - {w['id']} ({w.get('business_name')}) | Demo: {w.get('demo_link')}")
