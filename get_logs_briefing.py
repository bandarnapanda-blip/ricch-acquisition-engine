from database import db
import json

logs = db.fetch_logs(limit=10)
for l in logs:
    ts = l.get("created_at", "?")[11:19]
    svc = l.get("service_name", "System")
    msg = l.get("message", "")
    print(f"[{ts}] {svc}: {msg}")
