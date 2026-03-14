import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

def check_activity():
    print("--- RECENT ACTIVITY ---")
    log_res = requests.get(f'{url}/rest/v1/activity_logs?order=created_at.desc&limit=5', headers=headers)
    try:
        logs = log_res.json()
        for log in logs:
            print(f"[{log['created_at']}] {log['service_name']}: {log['message']}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Response: {log_res.text}")

if __name__ == "__main__":
    check_activity()
