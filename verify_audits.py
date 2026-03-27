import sys
import os
sys.path.append('.')
from database import db

def main():
    print("--- VERIFYING AUDIT INTEGRITY ---")
    leads = db.fetch_leads(filters={'status': 'eq.Audited'})
    print(f"Total Audited Leads: {len(leads)}")
    
    # Check for scores that look like defaults or placeholders
    for l in leads[:10]:
        print(f"Lead: {l.get('website')}")
        print(f"  - Opportunity Score: {l.get('opportunity_score')}")
        print(f"  - Revenue Loss: ${l.get('revenue_loss')}")
        print(f"  - Email: {l.get('email')}")
        print(f"  - Candidate Emails: {l.get('candidate_emails')}")
        print("-" * 20)

if __name__ == "__main__":
    main()
