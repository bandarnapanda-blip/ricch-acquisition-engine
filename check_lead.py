from database import db
import sys

# Set encoding to utf-8 for terminal output
try:
    if sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except:
    pass

leads = db.fetch_leads({"opportunity_score": "eq.100"})
if not leads:
    print("No leads with score 100 found.")
else:
    l = leads[0]
    print(f"ID:     {l.get('id')}")
    print(f"Name:   {l.get('business_name')}")
    print(f"Status: {l.get('status')}")
    print(f"Link:   {l.get('demo_link')}")
