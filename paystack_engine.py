import os
import requests
import time
import random
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from config import AGENCY_NAME, AGENCY_EMAIL

load_dotenv()

# Setup Logging
logger = logging.getLogger("paystack_engine")
logging.basicConfig(level=logging.INFO)

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def generate_payment_link(lead_id: str, email: str, business_name: str, city: str, niche: str, amount_usd: int = 1500) -> str:
    """
    Generate a Paystack payment link for a lead.
    Paystack expects amount in cents (USD * 100).
    """
    if not PAYSTACK_SECRET_KEY:
        logger.error("PAYSTACK_SECRET_KEY not found in environment!")
        return None

    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    # reference: RI2CH-{lead_id}-{timestamp}
    reference = f"RI2CH-{lead_id}-{int(time.time())}"
    
    payload = {
        "email": email,
        "amount": amount_usd * 100,  # Paystack cents
        "currency": "USD",
        "reference": reference,
        "metadata": {
            "lead_id": lead_id,
            "business_name": business_name,
            "city": city,
            "niche": niche
        },
        # You can add a callback_url here if you want Paystack to redirect back to the dashboard
        "callback_url": "https://ri2ch-agency.netlify.app/payment-success" # Placeholder
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status"):
            return data["data"]["authorization_url"]
        else:
            logger.error(f"Paystack Error: {data.get('message')}")
            return None
    except Exception as e:
        logger.error(f"Failed to generate Paystack link: {e}")
        return None

def send_invoice_email(lead: dict, payment_link: str, amount_usd: int = 1500) -> bool:
    """Send the invoice email with the payment link."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.error("GMAIL credentials missing!")
        return False

    biz_name = lead.get("business_name") or "Your Business"
    first_name = lead.get("first_name") or biz_name.split()[0]
    
    subject = f"Your RI2CH Invoice — {biz_name} Website"
    
    body = f"""Hi {first_name},

Excited to get this live for you.

Here is your secure payment link:
{payment_link}

What happens after payment:
✅ Your site goes live within 24 hours
✅ Custom domain setup included
✅ 30 days of free edits
✅ Mobile optimized and SEO ready

Total: ${amount_usd:,} USD

Any questions just reply to this email.

— Khalil
RI2CH Agency
"""

    msg = MIMEMultipart()
    msg['From'] = f"{AGENCY_NAME} <{GMAIL_USER}>"
    msg['To'] = lead["email"]
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Invoice sent to {lead['email']} for {biz_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to send invoice to {lead['email']}: {e}")
        return False
