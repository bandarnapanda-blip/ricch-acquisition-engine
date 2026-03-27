import sys
import os
import time
import requests
import re
from urllib.parse import quote
sys.path.append('.')
from database import db

def scrape_emails_from_ddg(query):
    """Scrape DuckDuckGo HTML for email addresses."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return []
        
        # Regex for common email patterns in text
        content = resp.text
        # Look for emails in snippets and results
        email_pattern = r'[a-zA-Z0-9.\-_+#~!$&\'()*+,;=:]+@[a-zA-Z0-9.\-_]+\.[a-zA-Z]{2,}'
        found = re.findall(email_pattern, content)
        
        # Filter out common false positives or system emails
        filtered = [e.lower() for e in found if not any(x in e.lower() for x in ['example.com', 'sentry.io', 'domain.com', 'email.com', 'yourwebsite.com'])]
        return list(set(filtered))
        
    except Exception as e:
        print(f"    [SCRAPE ERROR] {e}")
        return []

def main():
    print("--- ENRICHING AUDITED LEADS (DRD RECOVERY MODE) ---")
    leads = db.fetch_leads(filters={'status': 'eq.Audited'})
    
    # Filter for leads missing emails
    to_enrich = [l for l in leads if not l.get('email') and not l.get('candidate_emails')]
    print(f"Targeting {len(to_enrich)} leads for email discovery.")
    
    enriched_count = 0
    for i, lead in enumerate(to_enrich):
        website = lead.get('website')
        if not website:
            continue
            
        domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
        print(f"[{i+1}/{len(to_enrich)}] Searching for emails for: {domain}")
        
        # Try a specific search query
        query = f'email "@ {domain}"'
        emails = scrape_emails_from_ddg(query)
        
        if not emails:
            # Try second pattern
            query = f'contact email for {domain}'
            emails = scrape_emails_from_ddg(query)
            
        if emails:
            db.update_lead(lead['id'], {'candidate_emails': emails})
            print(f"    [FOUND] {len(emails)} emails: {', '.join(emails[:3])}")
            enriched_count += 1
        else:
            print("    [NONE FOUND]")
            
        # Jitter to avoid DDG limits
        time.sleep(random.uniform(2, 5) if 'random' in globals() else 3)

    print(f"\n--- SUCCESS: {enriched_count} Leads Enriched ---")

if __name__ == "__main__":
    import random # ensure random is available for jitter
    main()
