import sys
sys.path.append('.')
from database import db

def check_followups():
    print("--- FOLLOW-UP AUDIT (RI2CH) ---")
    
    # 1. Total Contacted
    contacted = db.get_count("leads", filters={"status": "Contacted"})
    print(f"Total Contacted: {contacted}")
    
    # 2. Check for Replies in Leads Table
    replied_leads = db.fetch_table("leads", filters={"status": "eq.Replied"})
    print(f"Active Replies in DB: {len(replied_leads)}")
    for l in replied_leads:
        print(f" [REPLY] {l.get('company_name')} ({l.get('website')}) - Contact: {l.get('email')}")

    # 3. Check for Inbound logs
    logs = db.fetch_logs(limit=100)
    inbound_logs = [l for l in logs if "Reply detected" in l.get('message', '')]
    print(f"Recent Reply Detections (Logs): {len(inbound_logs)}")
    for log in inbound_logs:
        print(f" [SIGNAL] {log.get('created_at')}: {log.get('message')}")

    print("--- AUDIT COMPLETE ---")

if __name__ == "__main__":
    check_followups()
