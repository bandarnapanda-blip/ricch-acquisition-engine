from database import db
import requests
import time

API_URL = "http://localhost:8000"

def build_pending_whales(limit=88):
    """
    Fetches all Audited leads and triggers non-blocking shadow site generation.
    """
    print("Fetching all leads to identify audited pool...")
    all_leads = db.fetch_leads() # Fetches default chunk (usually includes all recent ones)
    
    whales = [l for l in all_leads if l.get('status') in ['Whale Audit', 'Audit Delivered']]
    print(f"Found {len(whales)} Audited leads to build.")
    
    count = 0
    for w in whales[:limit]:
        lead_id = w.get("id")
        name = w.get("business_name", "Unknown")
        print(f"[{count+1}/{len(whales)}] Triggering: {name} ({lead_id})")
        
        try:
            payload = {
                "lead_id": lead_id,
                "business_name": name,
                "niche": w.get("niche", "General"),
                "city": w.get("city", ""),
                "score": w.get("opportunity_score", 0)
            }
            # Short timeout, API is non-blocking
            r = requests.post(f"{API_URL}/api/generate", json=payload, timeout=5)
            if r.status_code == 200:
                print(f"   Success: {r.json().get('message')}")
                count += 1
            else:
                print(f"   Failed: HTTP {r.status_code}")
                
            time.sleep(0.5)
        except Exception as e:
            print(f"   Error triggering {name}: {e}")

    print(f"MODE: BUILD - Triggers COMPLETE. {count} builds in flight.")

if __name__ == "__main__":
    build_pending_whales()
