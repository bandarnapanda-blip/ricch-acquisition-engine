import os

api_path = r'c:\Users\razer\.gemini\antigravity\playground\static-armstrong\api.py'
with open(api_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Update get_metrics to use columns
old_call = 'raw_leads = db.fetch_leads()'
new_call = 'raw_leads = db.fetch_leads(columns="id,business_name,opportunity_score,revenue_loss,status,amount_paid,niche,city,revenue,monthly_value,website_score")'
code = code.replace(old_call, new_call)

with open(api_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated api.py to use column-restricted fetch_leads in get_metrics.")
