import os, requests, json
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

def get_metrics():
    print("--- MORNING METRICS AUDIT ---")
    
    # 1. Pipeline Distribution
    try:
        res = requests.get(f'{url}/rest/v1/leads?select=status,opportunity_score', headers=headers)
        leads = res.json()
        stats = {}
        high_opp = 0
        for l in leads:
            s = l['status']
            stats[s] = stats.get(s, 0) + 1
            if l.get('opportunity_score', 0) >= 70:
                high_opp += 1
        
        print(f"\n[PIPELINE DISTRIBUTION]")
        for s, c in stats.items():
            print(f"- {s}: {c}")
        print(f"- High Authority Targets (70+ Score): {high_opp}")
    except Exception as e:
        print(f"Error fetching leads: {e}")

    # 2. Activity Trends (Last 24h)
    try:
        log_res = requests.get(f'{url}/rest/v1/activity_logs?select=*&order=created_at.desc&limit=15', headers=headers)
        logs = log_res.json()
        print(f"\n[RECENT ACTIVITY LOGS]")
        for log in logs:
            print(f"[{log['created_at']}] {log['service_name']}: {log['message']}")
    except Exception as e:
        print(f"Error fetching logs: {e}")

if __name__ == "__main__":
    get_metrics()
