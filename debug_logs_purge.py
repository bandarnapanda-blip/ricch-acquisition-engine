from database import db
logs = db.fetch_logs(limit=300)
purge_logs = [l for l in logs if '2026-03-19' in str(l.get('created_at'))]
for l in purge_logs:
    print(f"[{l.get('created_at')}] {l.get('service_name')}: {l.get('message')}")
