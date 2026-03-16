import os
import json
import time
import random
import smtplib
import logging
import argparse
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from openai import OpenAI
from config import AGENCY_NAME, AGENCY_EMAIL

# Load environment
load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email_blast")

# Config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
GEMINI_API_KEYS = os.getenv("GEMINI_API_KEYS", "").split(",")

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

def request_with_retry(method, url, **kwargs):
    """Wrapper for requests with exponential backoff."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            res = requests.request(method, url, **kwargs)
            res.raise_for_status()
            return res
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Request failed after {max_retries} attempts: {e}")
                raise
            wait = 2 ** attempt + random.uniform(0, 1)
            logger.warning(f"Connection issue ({e}). Retrying in {wait:.1f}s...")
            time.sleep(wait)
    return None

def fetch_targets():
    """Fetch high-value leads ready for direct email outreach."""
    # Prioritizing leads with verified shadow sites
    statuses = ["Shadow Site Ready", "High Intel Ready", "High Priority"]
    all_leads = []
    
    for status in statuses:
        url = f"{SUPABASE_URL}/rest/v1/leads?status=eq.{status.replace(' ', '%20')}&select=*"
        try:
            res = request_with_retry("GET", url, headers=get_headers())
            if res and res.status_code == 200:
                leads = res.json()
                # If we have a special flag or just return all for checking
                all_leads.extend(leads)
        except Exception as e:
            logger.error(f"Error fetching leads for status {status}: {e}")
            
    # Return unique leads by ID/Email
    seen_ids = set()
    unique_leads = []
    for l in all_leads:
        if l["id"] not in seen_ids:
            unique_leads.append(l)
            seen_ids.add(l["id"])
            
    return unique_leads

def generate_ai_pitch(lead):
    """Generate a high-authority, short pitch via Gemini."""
    domain = lead.get("website", "").split("//")[-1].replace("www.", "").split("/")[0]
    niche = lead.get("niche", "business")
    loss = lead.get("revenue_loss", "5,000")
    city = lead.get("city", "your area")
    
    # Use the verified demo link from our new Netlify Isolated Site Strategy
    preview_url = lead.get("demo_link", "")

    api_keys = [k.strip() for k in GEMINI_API_KEYS if k.strip()]
    if not api_keys:
        return f"Have a look at this: I've hand-built a high-performance redesign for {domain} because your current site is leaking an estimated ${loss}/mo in revenue in {city}. You can view the prototype here: {preview_url} - Interested in the full technical audit breakdown?"
        
    api_key = random.choice(api_keys)
    # Using v1 endpoint for stable content generation
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = f"""
    ROLE: Senior Revenue Consultant at {AGENCY_NAME}.
    TARGET: {lead.get('business_name', domain)} ({niche}).
    PROBLEM: Their site in {city} is leaking ${loss}/mo in high-ticket leads.
    SOLUTION: I've already hand-built a high-performance, niche-specific prototype for them here: {preview_url}
    
    TASK: 
    Write a 3-sentence direct email. 
    1. Hook on the leakage and the competitiveness of the {city} market for {niche}.
    2. Direct them to the custom prototype I already built specifically for them.
    3. Ask if they want the full technical audit breakdown.
    
    STRICT STYLE:
    - NO FLUFF. NO "DEAR". NO "BEST REGARDS".
    - START WITH "HAVE A LOOK AT THIS:".
    - Tone: High-authority, professional, slightly aggressive on the revenue loss.
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7}
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        if res.status_code == 200:
            data = res.json()
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            logger.warning(f"AI Pitch API failed ({res.status_code}): {res.text}")
            raise Exception("API failure")
    except Exception as e:
        logger.warning(f"AI Pitch generation failed: {e}. Using fallback.")
        return f"Have a look at this: I've hand-built a high-performance, niche-specific redesign for {domain} because your current site is leaking an estimated ${loss}/mo in revenue in {city}. You can view the prototype here: {preview_url} - Interested in the full technical audit breakdown?"

def send_email(to_email, subject, body):
    """Send outreach email via Gmail SMTP."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.error("GMAIL credentials missing!")
        return False
        
    msg = MIMEMultipart()
    msg['From'] = f"{AGENCY_NAME} <{GMAIL_USER}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

def update_lead_status(lead_id):
    """Update lead status to 'Contacted (Email)' in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}"
    try:
        request_with_retry("PATCH", url, headers=get_headers(), json={"status": "Contacted (Email)"})
    except Exception as e:
        logger.error(f"Failed to update lead {lead_id}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Ri2ch Automated Email Blast")
    parser.add_argument("--dry-run", action="store_true", help="Generate pitches without sending emails.")
    parser.add_argument("--limit", type=int, default=10, help="Max emails to send in this batch.")
    args = parser.parse_args()
    
    logger.info("Starting Email Blast Engine...")
    targets = fetch_targets()
    
    if not targets:
        logger.info("No valid targets found with emails. Hunt more leads!")
        return
        
    logger.info(f"Identified {len(targets)} high-value targets. Processing top {args.limit}...")
    
    processed = 0
    for lead in targets[:args.limit]:
        email = lead["email"]
        biz = lead.get("business_name") or lead.get("website")
        logger.info(f"Analyzing {biz} ({email})...")
        
        pitch = generate_ai_pitch(lead)
        subject = f"Revenue Leakage Audit for {lead.get('website', 'your business')}"
        
        if args.dry_run:
            logger.info(f"[DRY-RUN] To: {email}")
            logger.info(f"[DRY-RUN] Subject: {subject}")
            logger.info(f"[DRY-RUN] Body:\n{pitch}\n")
        else:
            success = send_email(email, subject, pitch)
            if success:
                logger.info(f"Successfully contacted {email}")
                update_lead_status(lead["id"])
                processed += 1
                # Anti-spam delay
                time.sleep(random.randint(20, 45))
            else:
                logger.error(f"Failed to contact {email}")
                
    logger.info(f"Email Blast complete. {processed} outreach sent.")

if __name__ == "__main__":
    main()
