import sys
sys.path.append('.')
from database import db
from datetime import datetime

def audit_v2():
    print("--- DEEP-DIVE OVERNIGHT AUDIT (RI2CH) ---")
    
    # 1. Fetch 500 Logs
    logs = db.fetch_logs(limit=500)
    orchestrator_logs = [l for l in logs if l.get('service_name') == 'Orchestrator']
    
    # Count Waves
    waves = [l for l in orchestrator_logs if "Strike Wave" in l.get('message', '')]
    refills = [l for l in orchestrator_logs if "Refill Burst" in l.get('message', '')]
    heartbeats = [l for l in orchestrator_logs if "Heartbeat" in l.get('message', '')]
    
    print(f"Orchestrator Status: ACTIVE")
    print(f"Strike Waves (Last 500 logs): {len(waves)}")
    print(f"Refill Bursts (Last 500 logs): {len(refills)}")
    print(f"System Heartbeats: {len(heartbeats)}")
    
    if waves:
        print("Latest Strike Waves:")
        for w in waves[:5]:
            print(f" - {w.get('created_at')}: {w.get('message')}")

    # 2. Total Contacted
    contacted = db.get_count("leads", filters={"status": "Contacted"})
    print(f"Current Total Contacted: {contacted}")
    
    # 3. Conversions
    conversions = db.get_count("activity_logs", filters={"service_name": "API", "message": "Audit Purchase Processed"})
    print(f"Total Conversions: {conversions}")

    print("--- AUDIT COMPLETE ---")

if __name__ == "__main__":
    audit_v2()
