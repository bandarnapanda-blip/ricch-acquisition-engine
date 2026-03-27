import os
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api_health():
    try:
        r = requests.get(f"{BASE_URL}/api/health")
        print(f"API Health: {r.status_code} | {r.json()}")
        return True
    except Exception as e:
        print(f"API Health Failed: {e}")
        return False

def test_payment_confirmation():
    # Fetch a lead that's in 'Demo Sent'
    from database import db
    leads = db.fetch_leads({"status": "eq.Demo Sent"})
    if not leads:
        print("No 'Demo Sent' leads found. Mocking confirmation for a 'New' lead instead.")
        leads = db.fetch_leads({"status": "eq.New"})
    
    if leads:
        lead_id = leads[0]["id"]
        biz_name = leads[0]["business_name"]
        print(f"Testing confirmation for: {biz_name} ({lead_id})")
        
        # Test the manual confirmation endpoint
        try:
            r = requests.post(f"{BASE_URL}/api/confirm-payment/{lead_id}")
            print(f"Confirmation Response: {r.status_code} | {r.json()}")
            
            # Verify DB state
            updated = db.fetch_leads({"id": f"eq.{lead_id}"})
            if updated and updated[0]["status"] == "Closed":
                print("✓ DB State: Lead successfully marked as CLOSED")
            else:
                print("✗ DB State: Lead status mismatch")
        except Exception as e:
            print(f"Confirmation Request Failed: {e}")
    else:
        print("No leads found for testing.")

if __name__ == "__main__":
    if test_api_health():
        test_payment_confirmation()
