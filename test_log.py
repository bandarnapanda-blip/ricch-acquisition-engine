from database import db
import time

def test_logging():
    print("Sending test log...")
    endpoint = f"{db.url}/rest/v1/activity_logs"
    data = {"service_name": "TestService", "message": f"Test log at {time.time()}"}
    try:
        r = db._session.post(endpoint, headers=db._get_headers(prefer_minimal=True), json=data)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"FAILED to send log: {e}")

if __name__ == "__main__":
    test_logging()
