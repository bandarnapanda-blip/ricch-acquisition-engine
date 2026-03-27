from database import db
logs = db.fetch_logs(limit=20)
orchestrator_logs = [l for l in logs if l.get('service_name') == 'Orchestrator']

print(f"Total Orchestrator Logs Found: {len(orchestrator_logs)}")
for l in orchestrator_logs:
    print(f" - [{l.get('created_at')}] {l.get('message')}")
