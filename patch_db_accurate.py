import os

db_path = r'c:\Users\razer\.gemini\antigravity\playground\static-armstrong\database.py'
with open(db_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace limit=100 with dynamic limits
old_limit = 'def fetch_leads(self, filters: Optional[Dict[str, str]] = None, columns: str = "*") -> List[Dict[str, Any]]:\n        endpoint = f"{self.url}/rest/v1/leads?select={columns}&order=opportunity_score.desc&limit=100"'
new_limit = '''def fetch_leads(self, filters: Optional[Dict[str, str]] = None, columns: str = "*", limit: Optional[int] = None) -> List[Dict[str, Any]]:
        endpoint = f"{self.url}/rest/v1/leads?select={columns}&order=opportunity_score.desc"
        if limit is not None:
            endpoint += f"&limit={limit}"'''
code = code.replace(old_limit, new_limit)

with open(db_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Patched database.py for dynamic metrics.")
