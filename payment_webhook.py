import os
import hmac
import hashlib
import logging
import requests
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from silas_accounts import send_warm_email
import audit_report

load_dotenv()

logger = logging.getLogger("payment_webhook")
logging.basicConfig(level=logging.INFO, format="[Payment] %(message)s")

PAYSTACK_SECRET_KEY    = os.getenv("PAYSTACK_SECRET_KEY", "")
PAYSTACK_WEBHOOK_SECRET = os.getenv("PAYSTACK_WEBHOOK_SECRET", "")
AGENCY_NAME = os.getenv("AGENCY_NAME", "RI2CH Agency")

# ─── PAYSTACK VERIFICATION ────────────────────────────────────────────────────

def verify_webhook_signature(payload_bytes: bytes, signature: str) -> bool:
    if not PAYSTACK_WEBHOOK_SECRET:
        return True
    expected = hmac.new(PAYSTACK_WEBHOOK_SECRET.encode("utf-8"), payload_bytes, hashlib.sha512).hexdigest()
    return hmac.compare_digest(expected, signature)

def verify_payment_with_api(reference: str) -> Optional[dict]:
    if not PAYSTACK_SECRET_KEY: return None
    try:
        resp = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", 
                             headers={"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}, timeout=15)
        data = resp.json()
        return data["data"] if data.get("status") and data.get("data", {}).get("status") == "success" else None
    except: return None

# ─── NICHE TONE & TEMPLATES ──────────────────────────────────────────────────

def _get_niche_group(niche: str) -> str:
    n = (niche or "").lower()
    if any(k in n for k in ["law", "legal"]): return "law"
    if any(k in n for k in ["dental", "medical"]): return "medical"
    return "trades"

def _build_confirmation_email(business_name: str, niche: str, amount_usd: float, reference: str) -> dict:
    now = datetime.utcnow().strftime("%B %d, %Y at %I:%M %p UTC")
    
    body = f"Payment of ${amount_usd:,.0f} confirmed for {business_name} production build.\nReference: {reference}\nConfirmed: {now}\n\n"
    body += "Our team has initiated the 48-hour production build. You will receive your live URL and DNS activation steps shortly."
    
    subject = f"Payment Confirmed — {business_name}"
    html = f"<html><body><h2>Payment Confirmed ✓</h2><p>{body}</p></body></html>"
    return {"subject": subject, "body_text": body, "body_html": html}

def _build_delivery_email(business_name: str, niche: str, live_url: str) -> dict:
    subject = f"Your Site Is Live — {business_name}"
    body = f"Congratulations! Your production site is live at: {live_url}\n\nDNS instructions attached. Your 30-day support window starts today."
    html = f"<html><body><h2>🚀 Your Site Is Live</h2><p>{body}</p><a href='{live_url}'>View Site →</a></body></html>"
    return {"subject": subject, "body_text": body, "body_html": html}

# ─── MASTER HANDLERS ─────────────────────────────────────────────────────────

def handle_paystack_webhook(payload: dict, signature: str, payload_bytes: bytes, db=None) -> dict:
    if not verify_webhook_signature(payload_bytes, signature): return {"success": False}
    data = payload.get("data", {}); reference = data.get("reference", "")
    email = data.get("customer", {}).get("email", "")
    meta = data.get("metadata", {}); lead_id = meta.get("lead_id", "")
    biz_name = meta.get("business_name", "Valued Client")
    niche = meta.get("niche", "General")
    amount_usd = meta.get("amount_usd", 1500)

    if not verify_payment_with_api(reference): return {"success": False}

    email_content = _build_confirmation_email(biz_name, niche, amount_usd, reference)
    # Using Silas WARM channel for payment confirmation
    send_warm_email(
        to_email=email,
        subject=email_content["subject"],
        body_text=email_content["body_text"],
        body_html=email_content["body_html"],
        lead_id=lead_id
    )

    if db and lead_id:
        if amount_usd == 47:
            logger.info("Triggering Audit Delivery for $47 purchase.")
            audit_report.process_audit_purchase(name=biz_name, email=email, website=meta.get("website", ""), niche=niche, city=meta.get("city", ""), db=db)
            db.update_lead(lead_id, {"status": "Audit Delivered", "payment_status": "paid", "amount_paid": amount_usd})
            db.push_log("Payment", f"PAID: {biz_name} | $47 Audit | ref: {reference}")
        else:
            db.update_lead(lead_id, {"status": "Closed", "payment_status": "paid", "amount_paid": amount_usd})
            db.push_log("Payment", f"PAID: {biz_name} | ${amount_usd} | ref: {reference}")
            db.queue_task("production_build", {"lead_id": lead_id, "business_name": biz_name, "niche": niche, "amount_usd": amount_usd, "email": email})

    return {"success": True, "business_name": biz_name}

def send_delivery_email(lead_id: str, live_url: str, db=None) -> dict:
    if not db: return {"success": False}
    leads = db.fetch_leads({"id": f"eq.{lead_id}"})
    if not leads: return {"success": False, "reason": "Lead not found"}
    lead = leads[0]
    email, biz_name, niche = lead.get("email"), lead.get("business_name"), lead.get("niche")
    
    content = _build_delivery_email(biz_name, niche, live_url)
    
    # Using Silas WARM channel for delivery
    result = send_warm_email(
        to_email=email,
        subject=content["subject"],
        body_text=content["body_text"],
        body_html=content["body_html"],
        lead_id=lead_id
    )
    
    if result["success"]:
        db.update_lead(lead_id, {"status": "Delivered", "demo_link": live_url})
        db.push_log("Delivery", f"DELIVERED: {biz_name} | {live_url}")
        return {"success": True}
    return {"success": False, "reason": result.get("error", "Unknown error")}
