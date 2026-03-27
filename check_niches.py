import json
from database import db

def check_niches():
    try:
        leads = db.fetch_leads(columns="niche")
        niches = {}
        empty_count = 0
        for l in leads:
            n = l.get("niche")
            if not n:
                empty_count += 1
                n = "Unknown/Empty"
            niches[n] = niches.get(n, 0) + 1
        
        print("TOTAL LEADS FETCHED:", len(leads))
        print("DISTINCT NICHES IN DB:")
        for k, v in sorted(niches.items(), key=lambda item: item[1], reverse=True):
            print(f"  {k}: {v}")
    except Exception as e:
        print("Error fetching niches:", e)

if __name__ == "__main__":
    check_niches()
