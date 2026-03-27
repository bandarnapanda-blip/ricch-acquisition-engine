import os

db_path = r'c:\Users\razer\.gemini\antigravity\playground\static-armstrong\database.py'
with open(db_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Update fetch_leads to support columns
old_line = 'def fetch_leads(self, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:'
new_line = 'def fetch_leads(self, filters: Optional[Dict[str, str]] = None, columns: str = "*") -> List[Dict[str, Any]]:'
code = code.replace(old_line, new_line)

# Correct the endpoint in fetch_leads
old_endpoint = 'endpoint = f"{self.url}/rest/v1/leads?select=*&order=opportunity_score.desc&limit=1000"'
new_endpoint = 'endpoint = f"{self.url}/rest/v1/leads?select={columns}&order=opportunity_score.desc&limit=1000"'
code = code.replace(old_endpoint, new_endpoint)

with open(db_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated database.py with column support for fetch_leads.")
