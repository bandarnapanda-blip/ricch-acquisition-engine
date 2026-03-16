import os
import requests
from dotenv import load_dotenv
load_dotenv()

url = f"{os.getenv('SUPABASE_URL')}/rest/v1/sent_designs?select=id&limit=1"
headers = {
    "apikey": os.getenv("SUPABASE_KEY"),
    "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}"
}

try:
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        print("Table exists")
    elif resp.status_code == 404:
        print("Table does not exist")
    else:
        print(f"Error {resp.status_code}: {resp.text}")
except Exception as e:
    print(f"Connection error: {e}")
