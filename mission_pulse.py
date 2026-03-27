from database import db
from silas_accounts import _load_send_log
from datetime import date

log = _load_send_log()
today = str(date.today())
print(f"--- MISSION PULSE: {today} ---")
print(f"Total Domains Contacted Today: {len(log.get('sent_domains', []))}")

# Breakdown by Table Status
leads = db.fetch_leads()
replied = [l for l in leads if l.get('status') == 'Replied']
contacted_today = [l for l in leads if l.get('status') == 'Contacted' and l.get('id') in str(log.get('sent_domains', ''))] # Approximation

print(f"Leads with 'Replied' Status: {len(replied)}")

# Calculate Phase progress
whales = [l for l in leads if l.get('opportunity_score', 0) >= 75]
warm = [l for l in leads if 51 <= l.get('opportunity_score', 0) <= 74]

# Check Silas Logs
print("\nGod View - Last 5 Silas Events:")
logs = db.fetch_logs(limit=10)
silas_logs = [l for l in logs if l.get('service_name') == 'Silas'][:5]
for l in silas_logs:
    print(f" - [{l.get('created_at')}] {l.get('message')}")
