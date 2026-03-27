from database import db
leads = db.fetch_leads()
replied = [l for l in leads if l.get('status') == 'Replied']

print(f"Total Replied Signals: {len(replied)}")
for l in replied:
    print(f" - {l.get('business_name')} ({l.get('email')})")

from silas_accounts import get_daily_status
status = get_daily_status()
print("\nDaily Send Progress:")
print(f" - Total Sent: {status['total_sent']}")
print(f" - Remaining:   {status['total_remaining']}")
