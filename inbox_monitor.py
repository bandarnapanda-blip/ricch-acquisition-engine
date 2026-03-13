import os
import re
import imaplib
import email
from email.header import decode_header
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from urllib.parse import urlparse
import random
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GMAIL_USER = os.getenv("GMAIL_USER", "ri2ch.digital@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
PAYSTACK_LINK = os.getenv("PAYSTACK_LINK", "https://paystack.com/pay/ri2ch-digital")
SERVICE_PRICE = os.getenv("SERVICE_PRICE", "499")
SERVICE_CURRENCY = os.getenv("SERVICE_CURRENCY", "GHS")

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

def request_with_retry(method, url, **kwargs):
    """Wrapper for requests with exponential backoff to handle connection drops."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
            if attempt == max_retries - 1:
                print(f"  [ERROR] Request failed after {max_retries} attempts: {e}")
                raise
            wait = 2 ** attempt + random.uniform(0, 1)
            print(f"  [RETRY] Connection issue ({e}). Retrying in {wait:.1f}s...")
            time.sleep(wait)
    return None

def push_log(service, message):
    """Push a log entry to Supabase."""
    endpoint = f"{SUPABASE_URL}/rest/v1/activity_logs"
    try:
        request_with_retry("POST", endpoint, headers=get_headers(), json={"service_name": service, "message": message}, timeout=10)
    except Exception as e:
        print(f"Log Error: {e}")

def fetch_known_domains():
    """Fetch all known lead domains from Supabase."""
    endpoint = f"{SUPABASE_URL}/rest/v1/leads?select=id,website,status,niche"
    try:
        response = request_with_retry("GET", endpoint, headers=get_headers())
        if response:
            leads = response.json()
            domain_map = {}
            for lead in leads:
                website = lead.get("website", "")
                domain = str(urlparse(website).netloc).replace("www.", "")
                if domain:
                    domain_map[domain] = lead
            return domain_map
        return {}
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return {}

def update_lead_replied(lead_id, patch_data):
    """Update a lead with reply metadata."""
    endpoint = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}"
    try:
        response = request_with_retry("PATCH", endpoint, headers=get_headers(), json=patch_data)
        return True
    except Exception as e:
        print(f"Error updating lead: {e}")
        return False

def send_auto_reply(to_email, subject, body, msg_id):
    """Send an automated reply via Gmail SMTP."""
    if not GMAIL_APP_PASSWORD or not GMAIL_USER:
        print("Error: GMAIL_APP_PASSWORD or GMAIL_USER not set.")
        return False
        
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = f"Re: {subject}" if not subject.lower().startswith('re:') else subject
    if msg_id:
        msg['In-Reply-To'] = msg_id
        msg['References'] = msg_id
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        if not GMAIL_APP_PASSWORD: return False
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error sending reply: {e}")
        return False

def classify_intent(subject, body_text):
    """Classify reply intent into 'positive', 'negative', or 'other'."""
    api_keys_str = os.environ.get("GEMINI_API_KEYS")
    if not api_keys_str:
        return "other"
        
    api_keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]
    api_key = random.choice(api_keys)
        
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        prompt = f"""
        Analyze this email reply from a business owner.
        Subject: {subject}
        Body: {body_text}
        
        Classify intent into ONE category:
        1. 'positive' - Interested, wants to see demo, says yes, sure, let's talk.
        2. 'negative' - No, unsubscribe, stop, not interested.
        3. 'other' - Questions, asking about identity, generic replies.
        
        Respond ONLY with the category word.
        """
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1}
        }
        response = request_with_retry("POST", url, headers=headers, json=payload, timeout=15)
        if response:
            data = response.json()
            result = data['candidates'][0]['content']['parts'][0]['text'].strip().lower()
            if result in ['positive', 'negative', 'other']:
                return result
        return "other"
    except Exception as e:
        print(f"Error classifying intent: {e}")
        return "other"

def process_lead_reply(msg, sender_email, lead, sender_domain):
    """Worker function to process a single hot lead reply."""
    try:
        subject = ""
        raw_subject = msg.get("Subject", "")
        decoded = decode_header(raw_subject)
        for part, enc in decoded:
            if isinstance(part, bytes):
                subject += part.decode(enc or "utf-8", errors="replace")
            else:
                subject += part
        
        print(f"\n🔥 HOT LEAD REPLY DETECTED!")
        print(f"  From:    {sender_email}")
        print(f"  Subject: {subject}")
        print(f"  Matches: {lead.get('website')}")
        push_log("Inbox", f"HOT LEAD DETECTED: Reply from {sender_email} ({lead.get('website')})")
        
        # Extract plain text body
        body_text = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body_text = part.get_payload(decode=True).decode()
                    except: pass
                    break
        else:
            try:
                body_text = msg.get_payload(decode=True).decode()
            except: pass
        
        body_text = body_text[:1200]
        
        # Classify intent via AI
        sentiment = classify_intent(subject, body_text)
        print(f"  🤖 AI Intent Classification: {sentiment}")
        
        from datetime import datetime, timezone
        now_ts = datetime.now(timezone.utc).isoformat()
        
        patch_data = {
            "reply_at": now_ts,
            "reply_text": body_text,
            "reply_source": "gmail-monitor",
            "reply_status": sentiment,
            "last_stage": "replied",
            "status": "Replied"
        }
        
        # Update lead status based on intent
        if sentiment == "positive":
            print(f"  🚀 Launching Industrial Closer for {lead.get('website')}")
            from generate_landing import generate_page, upload_to_supabase_storage
            
            # Clean name for filename
            business_name = lead.get('website', '').replace('https://','').replace('http://','').replace('www.', '').split('.')[0].capitalize()
            city = lead.get('city', 'Your City')
            niche = lead.get('niche', 'Contracting')
            
            import re
            safe_name = re.sub(r'[^a-zA-Z0-9]', '-', business_name.lower()).strip('-')
            filename = f"{safe_name}-{city.lower()}-redesign.html"
            
            html = generate_page(business_name, niche, city)
            demo_link = upload_to_supabase_storage(html, filename) if html else None
            
            if demo_link:
                patch_data.update({
                    "demo_link": demo_link,
                    "status": "Demo Sent & Invoice Placed",
                    "last_stage": "demo_sent",
                    "monthly_value": 499 if niche not in ["Solar Energy", "Personal Injury Law"] else (800 if "Law" in niche else 500)
                })
                update_lead_replied(lead["id"], patch_data)
                
                # Send email
                msg_id = msg.get("Message-ID", "")
                reply_body = f"Awesome, here is the live prototype I built for you:\n{demo_link}\n\nAs you can see, it loads in under 1 second and is heavily optimized to convert mobile traffic into actual phone calls for your {niche.lower()} business. I build these exclusively for contractors.\n\nNormally agencies charge $3,000+ for this and take weeks. Since I already built the foundation for you, I can transfer this entire site to your domain, fully customized with your photos and reviews, for a flat {SERVICE_CURRENCY} {SERVICE_PRICE} (approx. $499 USD).\n\nIf you want it, just claim it here securely via Paystack: {PAYSTACK_LINK}\n\nOnce paid, I'll have it live on your domain within 48 hours. Let me know what you think!"
                send_auto_reply(sender_email, raw_subject, reply_body, msg_id)
                push_log("Inbox", f"Auto-Closer Success: Demo and Invoice sent to {sender_email}")
            else:
                update_lead_replied(lead["id"], patch_data)
        elif sentiment == "negative":
            patch_data["status"] = "Dead"
            update_lead_replied(lead["id"], patch_data)
        else:
            patch_data["status"] = "Question/Manual"
            update_lead_replied(lead["id"], patch_data)
        
        return True
    except Exception as e:
        print(f"  [ERROR] Processing lead {sender_email}: {e}")
        return False

def check_inbox():
    """Connect to Gmail via IMAP and check for new replies from known lead domains."""
    if not GMAIL_APP_PASSWORD:
        print("Error: GMAIL_APP_PASSWORD not set.")
        return
    
    print("=" * 60)
    print("  INBOX MONITOR - Industrial Mode (Parallel Processing)")
    print("=" * 60)
    
    domain_map = fetch_known_domains()
    if not domain_map:
        print("No leads in database to track.")
        return
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("INBOX")
        
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages[0]:
            print("No new messages.")
            mail.logout()
            return
        
        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} unread emails. Analyzing...")
        
        tasks_to_process = []
        
        for eid in email_ids:
            status, msg_data = mail.fetch(eid, "(RFC822)")
            if status != "OK": continue
            
            msg = email.message_from_bytes(msg_data[0][1])
            from_header = msg.get("From", "")
            match = re.search(r'[\w\.-]+@[\w\.-]+', from_header)
            sender_email = match.group(0).lower() if match else ""
            sender_domain = sender_email.split("@")[-1] if "@" in sender_email else ""
            
            # Match domain
            for known_domain, lead in domain_map.items():
                if str(known_domain) in str(sender_domain) or str(sender_domain) in str(known_domain):
                    tasks_to_process.append((msg, sender_email, lead, sender_domain))
                    break
        
        # Parallel Execution
        if tasks_to_process:
            print(f"Dispatched {len(tasks_to_process)} hot leads to Parallel Workers...")
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(process_lead_reply, *task) for task in tasks_to_process]
                for future in as_completed(futures):
                    future.result() # Log errors inside worker
            
        mail.logout()
        print(f"\n{'=' * 60}")
        print(f"  SCAN COMPLETE: Processed {len(tasks_to_process)} lead interactions")
        print(f"{'=' * 60}")
        
    except imaplib.IMAP4.error as e:
        print(f"IMAP Error: {e}")
        print("Make sure your Gmail App Password is correct.")
    except Exception as e:
        print(f"Error: {e}")

import time
if __name__ == "__main__":
    print("Starting continuous inbox monitoring (checking every 2 minutes)...")
    while True:
        check_inbox()
        print("Sleeping for 2 minutes...")
        time.sleep(120)
