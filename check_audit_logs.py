from database import db
logs = db.fetch_logs(limit=20)
for l in logs:
    if "Audit" in str(l.get("service_name")):
        print(f"[{l.get('created_at')}] {l.get('service_name')}: {l.get('message')}")
