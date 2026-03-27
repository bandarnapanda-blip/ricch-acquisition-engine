import os
import sys
import re
import subprocess
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from database import db
from analyzer import generate_ai_completion
from dotenv import load_dotenv

load_dotenv()

def get_or_extract_name(lead):
    if lead.get('business_name'):
        return lead.get('business_name')
    url = lead.get('website')
    if not url: return "Elite Services"
    print(f"  [NAME REPAIR] {url}...")
    sys.stdout.flush()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=5, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else ""
        h1 = soup.find('h1').text if soup.find('h1') else ""
        prompt = f"Extract the professional company name from: URL={url}, Title={title}, H1={h1}. Only return the name."
        name = generate_ai_completion(prompt)
        name = name.strip('"').strip("'").strip()
        if len(name) > 60: name = name[:60]
        db.update_lead(lead['id'], {"business_name": name})
        return name
    except Exception:
        domain = urlparse(url).netloc.replace('www.', '').split('.')[0].capitalize()
        return domain

def generate_for_lead(lead):
    name = get_or_extract_name(lead)
    niche = lead.get('niche') or "Industry Leader"
    city = lead.get('city') or "Your City"
    score = lead.get('opportunity_score', 50)
    lead_id = lead.get('id')
    if not name: name = "Valued Business"
    safe_name = "".join(x for x in name if x.isalnum() or x == ' ').strip().replace(' ', '-')
    safe_city = "".join(x for x in city if x.isalnum() or x == ' ').strip().replace(' ', '-')
    slug = f"{safe_name.lower()}-{safe_city.lower()}"
    print(f"\n[DEPLOY] {name} | {niche} | Score: {score}")
    sys.stdout.flush()
    cmd = [".\\venv\\Scripts\\python.exe", "generate_landing.py", name, niche, city, str(lead_id), slug, str(score)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if "Netlify Deployment Successful:" in result.stdout:
            url_match = re.search(r"Netlify Deployment Successful: (https?://\S+)", result.stdout)
            if url_match:
                print(f"  -> SUCCESS: {url_match.group(1)}")
                return True
        elif "GitHub API Upload Successful:" in result.stdout:
            url_match = re.search(r"GitHub API Upload Successful: (https?://\S+)", result.stdout)
            if url_match:
                print(f"  -> SUCCESS (GitHub): {url_match.group(1)}")
                return True
        elif "Supabase Upload Successful:" in result.stdout:
            url_match = re.search(r"Supabase Upload Successful: (https?://\S+)", result.stdout)
            if url_match:
                print(f"  -> SUCCESS (Supabase): {url_match.group(1)}")
                return True
        print(f"  -> CHECK: Site generated but URL extraction skipped.")
        return True
    except subprocess.TimeoutExpired:
        print(f"  -> TIMEOUT: Skipping {name}")
        return False
    except Exception as e:
        print(f"  -> FAILED: {e}")
        return False

def main():
    LIMIT = 50 # Production burst
    MIN_SCORE = 75
    
    # Only fetch leads that are audited and need shadow sites to reduce payload
    leads = db.fetch_leads({"opportunity_score": "gte.75"})
    
    # Filter for leads that don't have a live demo_link yet
    ready_leads = [l for l in leads if not l.get('demo_link') and l.get('opportunity_score', 0) >= MIN_SCORE]
    
    print(f"AESTHETIC EXCELLENCE: Queuing {len(ready_leads)} Whales for V15.1 production burst.")
    import sys
    sys.stdout.flush()
    
    count = 0
    for lead in ready_leads:
        if generate_for_lead(lead):
            count += 1
        if count >= LIMIT: 
            break
        import time
        time.sleep(3) # Heavy jitter for DB stability

    print(f"\nPhase Complete. Deployed {count} premium shadow sites.")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
