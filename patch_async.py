import os

api_path = r'c:\Users\razer\.gemini\antigravity\playground\static-armstrong\api.py'
with open(api_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Remove async from synchronous database endpoints
code = code.replace('async def get_leads(', 'def get_leads(')
code = code.replace('async def get_metrics(', 'def get_metrics(')
code = code.replace('async def get_logs(', 'def get_logs(')
code = code.replace('async def god_view(', 'def god_view(')
code = code.replace('async def api_get_agents(', 'def api_get_agents(')
code = code.replace('async def api_get_briefing(', 'def api_get_briefing(')
code = code.replace('async def get_tasks(', 'def get_tasks(')
code = code.replace('async def health(', 'def health(')
code = code.replace('async def fire_silas(', 'def fire_silas(')
code = code.replace('async def generate_site(', 'def generate_site(')

with open(api_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Removed 'async def' from blocking endpoints to fix event loop deadlock.")
