import os
import requests
import time
from urllib.parse import quote_plus
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SERVICE_ROLE_KEY = os.getenv("SERVICE_ROLE_KEY")
REQUEST_TIMEOUT = 300  # Increased for large lead batch queries

class SupabaseDB:
    def __init__(self, use_session: bool = True):
        if not SUPABASE_URL or not (SUPABASE_KEY or SERVICE_ROLE_KEY):
            raise RuntimeError("SUPABASE_URL and a valid key must be set in environment")
        raw_url = SUPABASE_URL or ""
        self.url = raw_url.rstrip('/')
        # Use Service Role Key for elevated permissions (writes/updates) if available
        self.key: str = SERVICE_ROLE_KEY or SUPABASE_KEY or ""
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
    def fetch_leads(self, filters: Optional[Dict[str, str]] = None, columns: str = "*", limit: Optional[int] = None) -> List[Dict[str, Any]]:
        endpoint = f"{self.url}/rest/v1/leads?select={columns}&order=opportunity_score.desc"
        if limit is not None:
            endpoint += f"&limit={limit}"
        if filters:
            for k, v in filters.items():
                endpoint += f"&{quote_plus(k)}={quote_plus(v)}"
        
        # Enhanced resilience for long-running strikes
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            try:
                resp = self._session.get(endpoint, headers=self.headers, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"DB Warning: Attempt {attempt+1} failed ({e}). Retrying in 2s...")
                    time.sleep(2)
                else:
                    print(f"DB Error (fetch_leads): {e} | Endpoint: {endpoint}")
                    return []
        return []

    
    def fetch_table(self, table: str, filters: Optional[Dict[str, str]] = None, limit: int = 50) -> List[Dict[str, Any]]:
        endpoint = f"{self.url}/rest/v1/{table}?select=*&limit={int(limit)}"
        if filters:
            from urllib.parse import quote_plus
            for k, v in filters.items():
                endpoint += f"&{quote_plus(k)}={quote_plus(v)}"
        try:
            resp = self._session.get(endpoint, headers=self.headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"DB Error (fetch_table {table}): {e}")
            return []

    def update_lead(self, lead_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        endpoint = f"{self.url}/rest/v1/leads?id=eq.{lead_id}"
        retries = 3
        for i in range(retries):
            try:
                resp = self._session.patch(endpoint, headers=self._get_headers(prefer_minimal=True), json=data, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                return {"success": True}
            except Exception as e:
                if "10054" in str(e) and i < retries - 1:
                    time.sleep(1)
                    continue
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
        endpoint = f"{self.url}/rest/v1/leads" # Fix for task_id mapping if necessary
        # Simplified:
        return None

    # --- Logs ---
    def push_log(self, service_name: str, message: str) -> None:
        endpoint = f"{self.url}/rest/v1/activity_logs"
        data = {
            "service_name": service_name,
            "message": message
        }
        retries = 3
        for i in range(retries):
            try:
                self._session.post(endpoint, headers=self._get_headers(prefer_minimal=True), json=data, timeout=REQUEST_TIMEOUT)
                break
            except Exception as e:
                if "10054" in str(e) and i < retries - 1:
                    time.sleep(0.5)
                    continue
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

    def fetch_events(self, limit: int = 100) -> List[Dict[Dict[str, Any], Any]]:
        """Alias for activity_logs used by God-View."""
        endpoint = f"{self.url}/rest/v1/activity_logs?select=*&order=created_at.desc&limit={int(limit)}"
        try:
            resp = self._session.get(endpoint, headers=self.headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"DB Error (fetch_events): {e}")
            return []
    
    def get_count(self, table: str, filters: Optional[Dict[str, str]] = None) -> int:
        endpoint = f"{self.url}/rest/v1/{table}?select=id"
        if filters:
            for k, v in filters.items():
                endpoint += f"&{quote_plus(k)}=eq.{quote_plus(v)}"
        headers = self.headers.copy()
        headers["Prefer"] = "count=exact"
        headers["Range"] = "0-0"
        try:
            resp = self._session.get(endpoint, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            content_range = resp.headers.get("Content-Range", "")
            if "/" in content_range:
                return int(content_range.split("/")[-1])
            return 0
        except Exception as e:
            print(f"DB Error (get_count {table}): {e}")
            return 0

# Singleton instance
db = SupabaseDB(use_session=False)
