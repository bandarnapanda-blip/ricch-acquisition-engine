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
    val = l.get('candidate_emails')
    print(f"Lead ID: {l.get('id')}")
    print(f"Column:  candidate_emails")
    print(f"Value:   {val}")
    print(f"Type:    {type(val)}")
    
    # Try a test update with a simple list to see the 400 error in detail
    print("\n--- Test Update (List format) ---")
    res = db.update_lead(l.get('id'), {"candidate_emails": ["test@example.com"]})
    print(f"Result:  {res is not None}")
