import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class SupabaseDB:
    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def _get_headers(self, prefer_minimal=False):
        headers = self.headers.copy()
        if prefer_minimal:
            headers["Prefer"] = "return=minimal"
        return headers

    # --- Leads ---
    def fetch_leads(self, filters=None):
        endpoint = f"{self.url}/rest/v1/leads?select=*&order=opportunity_score.desc"
        if filters:
            # Simple filter implementation (e.g., status=eq.New)
            for k, v in filters.items():
                endpoint += f"&{k}={v}"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"DB Error (fetch_leads): {e}")
            return []

    def update_lead(self, lead_id, data):
        endpoint = f"{self.url}/rest/v1/leads?id=eq.{lead_id}"
        try:
            response = requests.patch(endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"DB Error (update_lead): {e}")
            return None

    def upsert_lead(self, lead_data):
        endpoint = f"{self.url}/rest/v1/leads"
        headers = self._get_headers()
        headers["Prefer"] = "resolution=merge-duplicates"
        try:
            response = requests.post(endpoint, headers=headers, json=lead_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"DB Error (upsert_lead): {e}")
            return None

    # --- Tasks (Project Antigravity Queue) ---
    def queue_task(self, task_type, payload):
        endpoint = f"{self.url}/rest/v1/tasks"
        data = {
            "task_type": task_type,
            "payload": payload,
            "status": "pending"
        }
        try:
            response = requests.post(endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"DB Error (queue_task): {e}")
            return None

    def fetch_pending_tasks(self, limit=10):
        endpoint = f"{self.url}/rest/v1/tasks?status=eq.pending&limit={limit}"
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"DB Error (fetch_pending_tasks): {e}")
            return []

    def update_task_status(self, task_id, status, error=None):
        endpoint = f"{self.url}/rest/v1/tasks?id=eq.{task_id}"
        data = {"status": status}
        if error:
            data["error_message"] = str(error)
        
        try:
            response = requests.patch(endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"DB Error (update_task_status): {e}")
            return None

    # --- Logs ---
    def push_log(self, service_name, message):
        endpoint = f"{self.url}/rest/v1/activity_logs"
        data = {
            "service_name": service_name,
            "message": message
        }
        try:
            requests.post(endpoint, headers=self._get_headers(prefer_minimal=True), json=data)
        except Exception as e:
            print(f"DB Error (push_log): {e}")

    def fetch_logs(self, limit=50):
        endpoint = f"{self.url}/rest/v1/activity_logs?select=*&order=created_at.desc&limit={limit}"
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"DB Error (fetch_logs): {e}")
            return []

# Singleton instance
db = SupabaseDB()
