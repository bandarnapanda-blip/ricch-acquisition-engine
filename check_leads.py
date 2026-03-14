import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

def check_top_leads():
    try:
        # Fetching a single row to check available columns
        res = requests.get(f'{url}/rest/v1/leads?select=*&limit=1', headers=headers)
        if res.status_code != 200:
            print(f"PostgREST Error: {res.text}")
            return
            
        leads = res.json()
        if leads:
            print(f"Available Columns: {list(leads[0].keys())}")
            print("-" * 30)
        else:
            print("No leads found in database.")
            return

        # Fetching top leads
        res = requests.get(f'{url}/rest/v1/leads?select=website,business_name,opportunity_score,status,website_roast,revenue_loss&order=opportunity_score.desc&limit=5', headers=headers)
        leads = res.json()
            
        print(f"--- TOP LEAD INTELLIGENCE ---")
        for lead in leads:
            score = lead.get('opportunity_score', 0)
            site = lead.get('website', 'unknown')
            biz = lead.get('business_name', 'unknown')
            status = lead.get('status', 'N/A')
            roast = lead.get('website_roast')
            loss = lead.get('revenue_loss', 'N/A')
            
            roast_snippet = roast[:100] + "..." if roast and isinstance(roast, str) else "No roast yet"
            
            print(f"Business: {biz} ({site})")
            print(f"  Score: {score} | Status: {status}")
            print(f"  Revenue Loss Est: {loss}")
            print(f"  Intel Snippet: {roast_snippet}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Script Error: {e}")

if __name__ == "__main__":
    check_top_leads()
