import os
import json
import logging
import smtplib
from flask import Flask, request, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import db
from paystack_engine import GMAIL_USER, GMAIL_APP_PASSWORD
from config import AGENCY_NAME

# Setup Logging
logger = logging.getLogger("webhook_handler")
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return '{"status": "online", "service": "RI2CH Webhook Handler", "message": "Listening for Paystack events."}', 200, {'Content-Type': 'application/json'}


KHALIL_EMAIL = os.getenv("KHALIL_EMAIL")

def send_confirmation_emails(lead_data: dict, amount: float):
    """
    1. Send confirmation to the client.
    2. Send notification to Khalil.
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.error("GMAIL credentials missing for webhook confirmation!")
        return

    biz_name = lead_data.get("business_name") or "Your Business"
    first_name = lead_data.get("first_name") or biz_name.split()[0]
    email = lead_data.get("email")

    # 1. Client Confirmation
    client_subject = "Payment Confirmed — We're building your site now 🚀"
    client_body = f"""Hi {first_name},

Payment received. Thank you.

Your new {biz_name} website is now in production.

You'll receive a link to review it within 24 hours.

— Khalil
RI2CH Agency
"""
    
    # 2. Khalil Notification
    khalil_subject = f"💰 NEW PAYMENT: ${amount} from {biz_name}"
    khalil_body = f"""Khalil,

New payment received!

Client: {biz_name}
Niche: {lead_data.get('niche')}
City: {lead_data.get('city')}
Amount: ${amount}
Lead ID: {lead_data.get('id')}

The confirmation email has been sent to the client.
"""


    from silas_accounts import send_warm_email
    email_success = True
    if email:
        res = send_warm_email(to_email=email, subject=client_subject, body_text=client_body, body_html=None, lead_id=lead_data.get('id'))
        if not res.get("success"): email_success = False
    if KHALIL_EMAIL:
        send_warm_email(to_email=KHALIL_EMAIL, subject=khalil_subject, body_text=khalil_body, body_html=None, lead_id=lead_data.get('id'))


@app.route("/paystack-webhook", methods=["POST"])
def paystack_webhook():
    """Handle Paystack Webhook events."""
    # Note: In production, you MUST verify the Paystack signature using x-paystack-signature header
    # and your secret key. For this implementation, we will proceed to logic.
    
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data"}), 400

    event = data.get("event")
    if event == "charge.success":
        meta = data.get("data", {}).get("metadata", {})
        lead_id = meta.get("lead_id")
        amount_kobo = data.get("data", {}).get("amount", 0)
        amount_usd = amount_kobo / 100  # Paystack USD is in cents * 100
        
        if lead_id:
            logger.info(f"Payment Success Event for Lead: {lead_id} | Amount: ${amount_usd}")
            
            # 1. Update Lead Status in DB
            if db.record_payment(lead_id, amount_usd):
                # 2. Fetch lead for email details
                leads = db.fetch_leads({"id": f"eq.{lead_id}"})
                if leads:
                    send_confirmation_emails(leads[0], amount_usd)
                
                db.push_log("Webhook", f"Success: Received ${amount_usd} from {meta.get('business_name')}")
                return jsonify({"status": "success"}), 200
            else:
                logger.error(f"Failed to record payment for lead {lead_id}")
                return jsonify({"status": "error", "message": "DB Update failed"}), 500

    return jsonify({"status": "ignored"}), 200

if __name__ == "__main__":
    # Internal port for webhook tunnel (e.g. ngrok)
    app.run(port=5000)
