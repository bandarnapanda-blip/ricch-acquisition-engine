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

def check_schema():
    print("--- CHECKING SCHEMA ---")
    res = requests.get(f'{url}/rest/v1/leads?limit=1', headers=headers)
    try:
        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            print(f"Columns: {list(data[0].keys())}")
        else:
            print(f"Empty or unexpected response: {data}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Response: {res.text}")

if __name__ == "__main__":
    check_schema()
