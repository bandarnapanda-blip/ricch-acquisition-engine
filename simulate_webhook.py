import requests
import json

payload = {
    "reference": "test_txn_47",
    "name": "Santos Law Demo",
    "email": "ri2ch.digital@gmail.com",
    "website": "santoslaw.com",
    "niche": "Personal Injury",
    "city": "Los Angeles"
}
try:
    resp = requests.post("http://localhost:8001/api/audit/purchase", json=payload, timeout=15)
    print(resp.status_code, resp.json())
except Exception as e:
    print("Error:", e)
