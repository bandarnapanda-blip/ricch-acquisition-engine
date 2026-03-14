import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

def audit():
    res = requests.get(f'{url}/rest/v1/leads?select=status,last_stage', headers=headers)
    try:
        leads = res.json()
    except:
        print(f"Error parsing JSON: {res.text}")
        return
        
    if isinstance(leads, dict) and 'message' in leads:
        print(f"Supabase Error: {leads['message']}")
        return

    if not isinstance(leads, list):
        print(f"Unexpected response type: {type(leads)}")
        print(leads)
        return
    status_counts = {}
    stage_counts = {}
    
    for l in leads:
        s = l.get('status', 'Unknown')
        ls = l.get('last_stage', 'None')
        status_counts[s] = status_counts.get(s, 0) + 1
        stage_counts[ls] = stage_counts.get(ls, 0) + 1
        
    for s, c in status_counts.items():
        print(f"Status {s}: {c}")
    print("\n--- STAGE BREAKDOWN ---")
    for s, c in stage_counts.items():
        print(f"Stage {s}: {c}")

    # 2. Activity Logs for Nurture/Follow-up
    print("\n--- RECENT NURTURE ACTIVITY ---")
    log_res = requests.get(f'{url}/rest/v1/activity_logs?service_name=in.(Nurture,Follow-up)&order=created_at.desc&limit=10', headers=headers)
    logs = log_res.json()
    for log in logs:
        print(f"[{log['created_at']}] {log['service_name']}: {log['message']}")

if __name__ == "__main__":
    audit()
