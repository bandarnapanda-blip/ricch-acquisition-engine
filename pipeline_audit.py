from database import db
leads = db.fetch_leads()
print(f"Total Leads Synced: {len(leads)}")

audited = [l for l in leads if l.get('status') == 'Audited']
whales = [l for l in leads if l.get('opportunity_score', 0) >= 75]
warm = [l for l in leads if 51 <= l.get('opportunity_score', 0) <= 74]

print(f"Audited Leads (Pending $47 pitch): {len(audited)}")
print(f"Whale Leads (Targeting $1,500): {len(whales)}")
print(f"Warm Leads (Score 51-74): {len(warm)}")

# Check God View Pulse
print("\nGod View Pulse (Latest 10 Events):")
logs = db.fetch_logs(limit=10)
for l in logs:
    print(f" - [{l.get('created_at')}] {l.get('service_name')}: {l.get('message')}")
