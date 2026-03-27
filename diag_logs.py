from database import db
count = db.get_count("activity_logs")
print(f"Total activity_logs in DB: {count}")

latest_logs = db.fetch_logs(limit=10)
print("\nLatest 10 logs:")
for l in latest_logs:
    print(f" - [{l.get('created_at')}] {l.get('service_name')}: {l.get('message')}")
