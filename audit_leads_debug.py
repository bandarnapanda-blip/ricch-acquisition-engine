import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def audit():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    
    # Get the 50 most recent leads
    res = requests.get(f'{url}/rest/v1/leads?select=website,niche,opportunity_score,website_roast,created_at&order=created_at.desc&limit=50', headers=headers)
    
    if res.status_code != 200:
        print(f"Error: {res.status_code} - {res.text}")
        return

    leads = res.json()
    if not leads:
        print("No leads found in database.")
        return

    df = pd.DataFrame(leads)
    
    print("\n--- INDUSTRIAL HUNT QUALITY REPORT ---")
    print(f"Total Leads Audited: {len(df)}")
    print(f"Latest Lead Date: {df['created_at'].max()}")
    print("-" * 40)
    
    # Tiering
    a_tier = df[df['opportunity_score'] >= 75]
    b_tier = df[(df['opportunity_score'] >= 45) & (df['opportunity_score'] < 75)]
    c_tier = df[df['opportunity_score'] < 45]
    
    print(f"A-Tier (Elite): {len(a_tier)}")
    print(f"B-Tier (Growth): {len(b_tier)}")
    print(f"C-Tier (Standard): {len(c_tier)}")
    print("-" * 40)
    
    print("\nTop 10 High-Authority Targets Found:")
    top_10 = df.sort_values('opportunity_score', ascending=False).head(10)
    for _, row in top_10.iterrows():
        print(f"[{row['opportunity_score']}] {row['niche']} @ {row['website']}")

if __name__ == "__main__":
    audit()
