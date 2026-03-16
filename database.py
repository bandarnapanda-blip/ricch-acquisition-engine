import os
import requests
from urllib.parse import quote_plus
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
REQUEST_TIMEOUT = 10  # seconds

class SupabaseDB:
    def __init__(self, use_session: bool = True):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in environment")
        raw_url = SUPABASE_URL or ""
        self.url = raw_url.rstrip('/')
        self.key: str = SUPABASE_KEY if SUPABASE_KEY else ""
        self._session = requests.Session() if use_session else requests
        self.headers: Dict[str, str] = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def _get_headers(self, prefer_minimal: bool = False) -> Dict[str, str]:
        headers = self.headers.copy()
        headers["Prefer"] = "return=minimal" if prefer_minimal else "return=representation"
        return headers

    # --- Leads ---
    def fetch_leads(self, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        endpoint = f"{self.url}/rest/v1/leads?select=*&order=opportunity_score.desc"
        if filters:
            for k, v in filters.items():
                endpoint += f"&{quote_plus(k)}={quote_plus(v)}"
        try:
            resp = self._session.get(endpoint, headers=self.headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"DB Error (fetch_leads): {e}")
            return []

    def update_lead(self, lead_id: str, data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        endpoint = f"{self.url}/rest/v1/leads?id=eq.{quote_plus(lead_id)}"
        try:
            resp = self._session.patch(endpoint, headers=self._get_headers(), json=data, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"DB Error (update_lead): {e}")
            return None

    def upsert_lead(self, lead_data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        endpoint = f"{self.url}/rest/v1/leads"
        headers = self._get_headers()
        headers["Prefer"] = "resolution=merge-duplicates"
        try:
            resp = self._session.post(endpoint, headers=headers, json=lead_data, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"DB Error (upsert_lead): {e}")
            return None

    # --- Tasks (Project Antigravity Queue) ---
    def queue_task(self, task_type: str, payload: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        endpoint = f"{self.url}/rest/v1/tasks"
        data = {
            "task_type": task_type,
            "payload": payload,
            "status": "pending"
        }
        try:
            resp = self._session.post(endpoint, headers=self._get_headers(), json=data, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"DB Error (queue_task): {e}")
            return None

    def fetch_pending_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        endpoint = f"{self.url}/rest/v1/tasks?status=eq.pending&order=created_at.asc&limit={int(limit)}"
        try:
            resp = self._session.get(endpoint, headers=self.headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"DB Error (fetch_pending_tasks): {e}")
            return []

    # Atomic claim: change status from pending -> in_progress and return one row (safe for workers)
    def claim_task(self, worker_id: str, timeout_seconds: int = 300) -> Optional[Dict[str, Any]]:
        """
        Atomically claims a single pending task by updating status and setting a lease timestamp.
        Requires the use of a service key (trusted environment).
        """
        endpoint = f"{self.url}/rest/v1/tasks?status=eq.pending&order=created_at.asc&limit=1"
        data = {"status": "in_progress"}
        headers = self._get_headers()
        headers["Prefer"] = "return=representation"
        try:
            resp = self._session.patch(endpoint, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            results = resp.json()
            return results[0] if results else None
        except Exception as e:
            print(f"DB Error (claim_task): {e}")
            return None

    def mark_task_done(self, task_id: str) -> Optional[List[Dict[str, Any]]]:
        endpoint = f"{self.url}/rest/v1/tasks?id=eq.{quote_plus(task_id)}"
        import datetime
        data = {"status": "done", "completed_at": datetime.datetime.utcnow().isoformat() + "Z"}
        try:
            resp = self._session.patch(endpoint, headers=self._get_headers(), json=data, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"DB Error (mark_task_done): {e}")
            return None

    def mark_task_failed(self, task_id: str, error_message: str) -> Optional[List[Dict[str, Any]]]:
        endpoint = f"{self.url}/rest/v1/tasks?id=eq.{quote_plus(task_id)}"
        data = {"status": "failed", "error_message": str(error_message)}
        try:
            resp = self._session.patch(endpoint, headers=self._get_headers(), json=data, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"DB Error (mark_task_failed): {e}")
            return None

    def update_task_status(self, task_id: str, status: str, error: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        endpoint = f"{self.url}/rest/v1/tasks?id=eq.{quote_plus(task_id)}"
        data = {"status": status}
        if error:
            data["error_message"] = str(error)
        try:
            resp = self._session.patch(endpoint, headers=self._get_headers(), json=data, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"DB Error (update_task_status): {e}")
            return None

    # --- Logs ---
    def push_log(self, service_name: str, message: str) -> None:
        endpoint = f"{self.url}/rest/v1/activity_logs"
        data = {
            "service_name": service_name,
            "message": message
        }
        try:
            self._session.post(endpoint, headers=self._get_headers(prefer_minimal=True), json=data, timeout=REQUEST_TIMEOUT)
        except Exception as e:
            print(f"DB Error (push_log): {e}")

    def fetch_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        endpoint = f"{self.url}/rest/v1/activity_logs?select=*&order=created_at.desc&limit={int(limit)}"
        try:
            resp = self._session.get(endpoint, headers=self.headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"DB Error (fetch_logs): {e}")
            return []

    # --- Follow-up Queue ---
    def queue_follow_up(self, lead_id: str, count: int, scheduled_for: str) -> bool:
        endpoint = f"{self.url}/rest/v1/follow_up_queue"
        data = {
            "lead_id": lead_id,
            "follow_up_number": count,
            "scheduled_for": scheduled_for,
            "status": "pending"
        }
        try:
            resp = self._session.post(endpoint, headers=self._get_headers(), json=data, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return True
        except Exception as e:
            print(f"DB Error (queue_follow_up): {e}")
            return False

    def fetch_pending_follow_ups(self) -> List[Dict[str, Any]]:
        import datetime
        now = datetime.datetime.utcnow().isoformat() + "Z"
        endpoint = f"{self.url}/rest/v1/follow_up_queue?status=eq.pending&scheduled_for=lte.{now}&select=*,leads(*)"
        try:
            resp = self._session.get(endpoint, headers=self.headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"DB Error (fetch_pending_follow_ups): {e}")
            return []

    def mark_follow_up_sent(self, follow_up_id: str) -> bool:
        import datetime
        endpoint = f"{self.url}/rest/v1/follow_up_queue?id=eq.{follow_up_id}"
        data = {
            "status": "sent",
            "sent_at": datetime.datetime.utcnow().isoformat() + "Z"
        }
        try:
            resp = self._session.patch(endpoint, headers=self._get_headers(), json=data, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return True
        except Exception as e:
            print(f"DB Error (mark_follow_up_sent): {e}")
            return False

    # --- Revenue Tracking ---
    def record_payment(self, lead_id: str, amount: float, status: str = "paid") -> bool:
        import datetime
        lead_endpoint = f"{self.url}/rest/v1/leads?id=eq.{lead_id}"
        data = {
            "payment_status": status,
            "amount_paid": amount,
            "paid_at": datetime.datetime.utcnow().isoformat() + "Z",
            "status": "Closed - Won"
        }
        try:
            resp = self._session.patch(lead_endpoint, headers=self._get_headers(), json=data, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return True
        except Exception as e:
            print(f"DB Error (record_payment): {e}")
            return False

# Singleton instance
db = SupabaseDB()
