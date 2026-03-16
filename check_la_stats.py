import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

def get_count(filters):
    endpoint = f"{url}/rest/v1/leads"
    headers = {'apikey': key, 'Authorization': f'Bearer {key}', 'Prefer': 'count=exact'}
    try:
        r = requests.get(endpoint, params=filters, headers=headers, timeout=10)
        return r.headers.get('Content-Range', '0-0/0').split('/')[-1]
    except:
        return "?"

la_total = get_count({'city': 'eq.Los Angeles, California', 'select': 'id'})
la_pi = get_count({'city': 'eq.Los Angeles, California', 'niche': 'eq.Personal Injury Attorneys', 'select': 'id'})
la_dental = get_count({'city': 'eq.Los Angeles, California', 'niche': 'eq.Dental Implants', 'select': 'id'})
la_solar = get_count({'city': 'eq.Los Angeles, California', 'niche': 'eq.Solar Energy', 'select': 'id'})

print(f"Total LA Leads: {la_total}")
print(f"Personal Injury LA: {la_pi}")
print(f"Dental Implants LA: {la_dental}")
print(f"Solar Energy LA: {la_solar}")
