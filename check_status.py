from database import db
import json

def check_scraping_status():
    print("[Checking Task Queue]")
    tasks = db.fetch_pending_tasks(limit=10)
    processing_tasks = db.fetch_leads(filters={"status": "eq.processing"}) # Assuming I can fetch from tasks table or similar
    
    # Let's try to fetch all tasks to see what's going on
    endpoint = f"{db.url}/rest/v1/tasks?select=*"
    try:
        r = db._session.get(endpoint, headers=db.headers)
        all_tasks = r.json()
        print(f"Total Tasks: {len(all_tasks)}")
        for t in all_tasks:
            print(f"- Task {t.get('id')} ({t.get('task_type')}): {t.get('status')}")
    except:
        print("Could not fetch tasks table directly.")

    print("\n[Recent Activity Logs]")
    logs = db.fetch_logs(limit=10)
    for log in logs:
        print(f"[{log.get('created_at')}] {log.get('service_name')}: {log.get('message')}")

if __name__ == "__main__":
    check_scraping_status()
