from database import db
logs = db.fetch_logs(limit=50)
print(f"Total Logs Fetched: {len(logs)}")
for i, l in enumerate(logs):
    print(f"[{i+1}] [{l.get('created_at')}] {l.get('service_name')}: {l.get('message')}")
