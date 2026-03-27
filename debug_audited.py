from database import db
leads = db.fetch_leads(filters={'status': 'eq.Audited'}, limit=10)
for l in leads:
    print(f"ID: {l.get('id')}")
    print(f"Business: {l.get('business_name')}")
    print(f"Email: {l.get('email')}")
    print(f"Candidate Emails: {l.get('candidate_emails')}")
    print("-" * 20)
