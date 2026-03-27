from database import db
import json

tasks = db.fetch_table('tasks', {'status': 'eq.failed'}, limit=100)
purge_tasks = [t for t in tasks if 'purge' in str(t.get('error_message', '')).lower()]

print(f"Found {len(purge_tasks)} purge-related entries.")
for t in purge_tasks:
    print(json.dumps(t, indent=2))
