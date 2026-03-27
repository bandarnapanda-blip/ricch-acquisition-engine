import os
import time
import datetime
import logging
from database import db
from paystack_engine import GMAIL_USER, GMAIL_APP_PASSWORD
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import AGENCY_NAME

# Setup Logging
logger = logging.getLogger("follow_up_worker")
logging.basicConfig(level=logging.INFO)

def send_follow_up_email(lead: dict, follow_up_number: int) -> bool:
    """Send one of the 3 specified follow-up templates."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.error("GMAIL credentials missing for follow-up!")
        return False

    biz_name = lead.get("business_name") or "Your Business"
    first_name = lead.get("first_name") or biz_name.split()[0]
    city = lead.get("city") or "your area"
    niche = lead.get("niche") or "industry"
    preview_url = lead.get("demo_link") or "#"

    import json
    roast_data = {}
    if lead.get("website_roast"):
        try:
            roast_data = json.loads(lead.get("website_roast"))
        except:
            pass
            
    diamond_url = roast_data.get("diamond_audit_url")
    annual_leakage = roast_data.get("annual_leakage", "$495,000")

    templates = {
        1: {
            "subject": f"Your Custom Revenue Audit: {biz_name}",
            "body": f"Hi {first_name},\n\nI just finished a deep audit of {biz_name} and found a significant annual revenue leak: ${annual_leakage}/yr.\n\nYou can see the full breakdown here: {diamond_url}\n\nLet me know if you want to recover this.\n\n— Khalil\nRI2CH Agency"
        } if diamond_url and follow_up_number == 1 else {
            "subject": "Did you get a chance to see your preview?",
            "body": f"Hi {first_name},\n\nJust checking in — I sent over a custom preview of your new website a couple days ago.\n\nHere it is again: {preview_url}\n\nLet me know what you think.\n\n— Khalil\nRI2CH Agency"
        },
        2: {
            "subject": f"Quick question about {biz_name}",
            "body": f"Hi {first_name},\n\nI built this specifically for {biz_name} — nobody else in {city} has seen it.\n\n{preview_url}\n\nIf you want to claim it and go live within 24 hours, just reply to this email.\n\n— Khalil\nRI2CH Agency"
        },
        3: {
            "subject": f"Releasing {biz_name}'s site in 24 hours",
            "body": f"Hi {first_name},\n\nI've been holding this preview exclusively for {biz_name}.\n\n{preview_url}\n\nAfter tomorrow I'll offer it to another {niche} business in {city}.\n\nIf you want it — reply now and I'll send the invoice immediately.\n\n— Khalil\nRI2CH Agency"
        }
    }

    if follow_up_number not in templates:
        return False

    temp = templates[follow_up_number]
    msg = MIMEMultipart()
    msg['From'] = f"{AGENCY_NAME} <{GMAIL_USER}>"
    msg['To'] = lead["email"]
    msg['Subject'] = temp["subject"]
    msg.attach(MIMEText(temp["body"], 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Follow-up #{follow_up_number} sent to {lead['email']}")
        return True
    except Exception as e:
        logger.error(f"Failed to send follow-up to {lead['email']}: {e}")
        return False

def scan_and_process():
    """
    1. Scan for leads who need follow-ups added to the queue.
    2. Process the follow-up queue for due items.
    """
    logger.info("Scanning for new follow-up requirements...")
    leads = db.fetch_leads()
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    for lead in leads:
        # Only follow up with "Contacted" leads
        if lead['status'] != "Contacted":
            continue
            
        follow_up_count = lead.get('follow_up_count', 0)
        # Use last_follow_up_at if available, otherwise fallback to sent_at (first outreach)
        last_action_str = lead.get('last_follow_up_at') or lead.get('sent_at')
        
        if not last_action_str:
            continue
            
        last_action_time = datetime.datetime.fromisoformat(last_action_str.replace('Z', '+00:00'))
        days_passed = (now_utc - last_action_time).days
        
        # Follow-up Logic
        next_count = follow_up_count + 1
        needed = False
        
        if next_count == 1 and days_passed >= 2:
            needed = True
        elif next_count == 2 and days_passed >= 2: # 4 days total (2+2)
            needed = True
        elif next_count == 3 and days_passed >= 2: # 6 days total (2+2+2)
            needed = True
        elif next_count > 3 and days_passed >= 2:
            # Termination: After 6 days + F/U 3 done
            db.update_lead(lead['id'], {"status": "Closed - No Response"})
            logger.info(f"Lead {lead['id']} marked as Closed - No Response.")
            continue

        if needed:
            # Check if this follow-up is already in the queue or in progress
            scheduled = now_utc.isoformat() + "Z"
            db.queue_follow_up(lead['id'], next_count, scheduled)

    # 2. Process Pending Queue
    logger.info("Processing due follow-ups from queue...")
    pending = db.fetch_pending_follow_ups()
    for item in pending:
        lead_data = item.get("leads")
        if not lead_data or not lead_data.get("email"):
            continue
            
        if send_follow_up_email(lead_data, item["follow_up_number"]):
            # Mark queue item as sent
            db.mark_follow_up_sent(item["id"])
            # Update lead record
            db.update_lead(lead_data["id"], {
                "follow_up_count": item["follow_up_number"],
                "last_follow_up_at": datetime.datetime.utcnow().isoformat() + "Z"
            })

def main():
    logger.info("Follow-up Worker started.")
    while True:
        try:
            scan_and_process()
        except Exception as e:
            logger.error(f"Error in follow-up loop: {e}")
        
        # Sleep for 1 hour as requested
        logger.info("Sleeping for 1 hour...")
        time.sleep(3600)

if __name__ == "__main__":
    main()
