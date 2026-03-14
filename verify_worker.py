from database import db
import json

def verify_heartbeat():
    logs = db.fetch_logs(limit=5)
    print("Recent Logs:")
    for log in logs:
        print(f"[{log.get('created_at')}] {log.get('service_name')}: {log.get('message')}")

if __name__ == "__main__":
    verify_heartbeat()
