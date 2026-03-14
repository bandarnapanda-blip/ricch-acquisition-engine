import os, requests, json
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

def get_detailed_metrics():
    print("--- COMPREHENSIVE MORNING AUDIT ---")
    
    # 1. Pipeline Snapshot
    res = requests.get(f'{url}/rest/v1/leads?select=status,opportunity_score', headers=headers)
    leads = res.json()
    stats = {}
    for l in leads:
        s = l['status']
        stats[s] = stats.get(s, 0) + 1
    
    print("\n[PIPELINE SNAPSHOT]")
    for s, c in stats.items():
        print(f"- {s}: {c}")

    # 2. Latest Outreach Hits
    print("\n[LATEST OUTREACH ACTIVITY]")
    outreach_res = requests.get(f'{url}/rest/v1/activity_logs?service_name=eq.Outreach&order=created_at.desc&limit=10', headers=headers)
    for log in outreach_res.json():
        print(f"[{log['created_at']}] {log['message']}")

    # 3. Latest Scraper Hits
    print("\n[LATEST SCRAPER ACTIVITY]")
    scraper_res = requests.get(f'{url}/rest/v1/activity_logs?service_name=eq.Scraper&order=created_at.desc&limit=5', headers=headers)
    for log in scraper_res.json():
        print(f"[{log['created_at']}] {log['message']}")

if __name__ == "__main__":
    get_detailed_metrics()
