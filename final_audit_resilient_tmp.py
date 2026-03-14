import os
import requests
import json
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

def get_session():
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

def audit():
    session = get_session()
    headers = {'apikey': key, 'Authorization': f'Bearer {key}'}
    
    # 1. Pipeline distribution
    res = session.get(f'{url}/rest/v1/leads?select=status', headers=headers)
    leads = res.json()
    stats = {}
    for l in leads:
        s = l['status']
        stats[s] = stats.get(s, 0) + 1
    
    print("--- GLOBAL PIPELINE ---")
    for s, c in stats.items():
        print(f"{s}: {c}")
        
    # 2. Recent log activity
    print("\n--- RECENT ACTIVITY ---")
    log_res = session.get(f'{url}/rest/v1/activity_logs?order=created_at.desc&limit=8', headers=headers)
    for log in log_res.json():
        print(f"[{log['created_at']}] {log['service_name']}: {log['message']}")

if __name__ == "__main__":
    audit()
