from database import db
import sys

# Set encoding to utf-8 for terminal output
try:
    if sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except:
    pass

# Fetch leads contacted on March 20th
leads = db.fetch_leads({"status": "eq.Contacted"})

print(f"\n--- Bounce Audit: Examining {len(leads)} Contacted Leads ---\n")

for l in leads[:40]:
    name = l.get('business_name', 'Unknown')
    primary_email = l.get('email')
    candidate_emails = l.get('candidate_emails', [])
    
    # Check if we have a real email
    email_str = ", ".join(candidate_emails) if isinstance(candidate_emails, list) else str(candidate_emails)
    
    # Flag suspicious emails
    is_suspicious = False
    if not primary_email and (not candidate_emails or len(candidate_emails) == 0):
        is_suspicious = True
    
    print(f"Lead: {name}")
    print(f"  Primary Email:   {primary_email or 'NONE'}")
    print(f"  Candidate List:  {email_str or 'NONE'}")
    
    if primary_email and "@" in primary_email:
        # Check if the primary email looks like a generic scraper throwaway
        if any(kw in primary_email.lower() for kw in ["admin@", "info@", "contact@", "support@", "office@"]):
            print(f"  [NOTE] Primary is a generic address (high bounce risk)")
            
    if is_suspicious:
        print(f"  [CRITICAL] NO TARGET EMAIL FOUND")
    
    print("-" * 30)
