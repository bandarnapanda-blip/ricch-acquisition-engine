import os
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
    # 1. Check existing column
    if lead.get('business_name'):
        return lead.get('business_name')
    
    url = lead.get('website')
    if not url: return "Elite Services"
    
    print(f"  [NAME REPAIR] {url}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=8, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else ""
        h1 = soup.find('h1').text if soup.find('h1') else ""
        
        prompt = f"Extract the professional company name from: URL={url}, Title={title}, H1={h1}. Only return the name."
        name = generate_ai_completion(prompt)
        name = name.strip('"').strip("'").strip()
        if len(name) > 60: name = name[:60]
        
        # Save back to DB for future use
        db.update_lead(lead['id'], {"business_name": name})
        return name
    except Exception:
        # Fallback to domain
        domain = urlparse(url).netloc.replace('www.', '').split('.')[0].capitalize()
        return domain

def generate_for_lead(lead):
    name = get_or_extract_name(lead)
    niche = lead.get('niche') or "Industry Leader"
    city = lead.get('city') or "Los Angeles"
    score = lead.get('opportunity_score', 50)
    lead_id = lead.get('id')
    
    # Safe slug for filename
    safe_name = "".join(x for x in name if x.isalnum() or x == ' ').strip().replace(' ', '-')
    safe_city = "".join(x for x in city if x.isalnum() or x == ' ').strip().replace(' ', '-')
    slug = f"{safe_name.lower()}-{safe_city.lower()}"
    
    print(f"\n[DEPLOY] {name} | {niche} | Score: {score}")
    
    cmd = [
        ".\\venv\\Scripts\\python.exe",
        "generate_landing.py",
        name,
        niche,
        city,
        str(lead_id),
        slug,
        str(score)
    ]
    
    try:
        # generate_landing.py handles the GitHub API upload and DB update internally
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Extract the resulting URL from the output if needed
        # generate_landing.py prints "Netlify Deployment Successful: <url>"
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
                
        print(f"  -> CHECK: Site generated but URL extraction skipped. Output: {result.stdout[-100:]}")
        return True
    except Exception as e:
        print(f"  -> FAILED: {e}")
        return False

def main():
    FORCE_RESET = True # Set to True to remake ALL sites with new templates
    
    leads = db.fetch_leads()
    if FORCE_RESET:
        ready_leads = [l for l in leads if l.get('opportunity_score', 0) >= 60]
        print(f"THE GREAT RESET: Remaking {len(ready_leads)} leads with 'Aesthetic Excellence' templates.")
    else:
        ready_leads = [l for l in leads if not l.get('demo_link') and l.get('opportunity_score', 0) >= 60]
        print(f"Billion-Dollar Fleet: {len(ready_leads)} leads queued for deployment.")
    
    count = 0
    for lead in ready_leads:
        if generate_for_lead(lead):
            count += 1
        
        if count >= 30: # Full queue processing
            break
            
        time.sleep(1)

    print(f"\nPhase Complete. Deployed {count} premium shadow sites.")

if __name__ == "__main__":
    main()
