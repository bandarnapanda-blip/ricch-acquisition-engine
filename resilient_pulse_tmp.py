import os
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

def get_session():
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

def test_connection():
    session = get_session()
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}'
    }
    
    print(f"Pulsing Supabase at {url}...")
    try:
        # Test basic connection
        r = session.get(f"{url}/rest/v1/leads?limit=1", headers=headers, timeout=20)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("SUCCESS: Connection established.")
            print(f"Sample Data: {r.json()}")
        else:
            print(f"FAILURE: Server returned {r.status_code}")
            print(r.text)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_connection()
