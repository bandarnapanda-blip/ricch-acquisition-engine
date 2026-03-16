import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = f"{os.getenv('SUPABASE_URL')}/rest/v1/"
headers = {
    "apikey": os.getenv("SUPABASE_KEY"),
    "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}"
}

try:
    # Just list all available tables/RPCs via spec
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        print("API Schema exists. Listing items...")
        data = resp.json()
        # Look for RPCs in the definition
        paths = data.get('paths', {})
        rpcs = [p for p in paths if p.startswith('/rpc/')]
        print(f"Found {len(rpcs)} RPCs:")
        for rpc in rpcs[:10]:
            print(f" - {rpc}")
    else:
        print(f"Error {resp.status_code}: {resp.text}")
except Exception as e:
    print(f"Connection error: {e}")
