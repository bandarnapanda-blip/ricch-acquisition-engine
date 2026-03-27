import requests
resp = requests.get("http://localhost:8001/api/metrics")
print(resp.json())
