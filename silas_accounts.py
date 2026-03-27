"""
================================================================================
  RI2CH AGENCY OS — MULTI-ACCOUNT SILAS ENGINE
  FILE: silas_accounts.py
  DROP IN: Antigravity root folder

  WHAT THIS DOES:
  ────────────────
  Manages multiple Gmail accounts for cold outreach.
  Tracks which account sent to which lead.
  Enforces daily limits per account automatically.
  Handles inbound (warm) emails on a completely separate track.
  Rotates accounts by niche so no two accounts target the same lead.

  THE TWO TRACKS:
  ────────────────
  Track 1 — COLD (Anti-Ban rules apply hard)
    Gmail accounts sending shadow site Trojan Horse emails
    20–50 emails/day per account maximum
    Leads must never receive cold email from two accounts

  Track 2 — WARM (No Anti-Ban limits)
    Anyone who paid $47 for the audit report
    Anyone who replied positively
    Anyone who clicked the shadow site CTA
    These people gave you their email voluntarily
    Follow-up freely. No daily limit.
================================================================================
"""

import os
import json
import smtplib
import logging
from datetime import datetime, date
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("silas_accounts")
logging.basicConfig(level=logging.INFO, format="[Silas] %(message)s")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
# Gmail Port 465 (SSL) is often more reliable than 587 (STARTTLS) in restricted environments.
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))


# ─── ACCOUNT REGISTRY ────────────────────────────────────────────────────────

def load_accounts() -> list[dict]:
    """
    Loads all configured Gmail accounts from environment variables.
    Returns list of account dicts with niche assignments and limits.
    """
    accounts = []
    i = 1
    while True:
        user  = os.getenv(f"SMTP_ACCOUNT_{i}_USER")
        if not user:
            break
        passw  = os.getenv(f"SMTP_ACCOUNT_{i}_PASS", "")
        niches = os.getenv(f"SMTP_ACCOUNT_{i}_NICHES", "General").split(",")
        limit  = int(os.getenv(f"SMTP_ACCOUNT_{i}_DAILY_LIMIT", "20"))

        accounts.append({
            "id":          i,
            "user":        user.strip(),
            "password":    passw.strip(),
            "niches":      [n.strip().lower() for n in niches],
            "daily_limit": limit,
        })
        i += 1

    if not accounts:
        # Fallback: single account from original SMTP_USER
        user = os.getenv("SMTP_USER", "")
        passw = os.getenv("SMTP_PASS", "")
        if user:
            accounts.append({
                "id":          1,
                "user":        user,
                "password":    passw,
                "niches":      ["all"],
                "daily_limit": 20,
            })

    return accounts


def get_warm_account() -> dict:
    """
    Returns the dedicated warm email account.
    Used for: $47 audit delivery, payment confirmation,
              retainer offers, monthly reports, positive reply follow-ups.
    No daily limit — all warm traffic.
    """
    return {
        "user":     os.getenv("SMTP_WAR_ACCOUNT_USER") or os.getenv("SMTP_WARM_USER") or os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_WAR_ACCOUNT_PASS") or os.getenv("SMTP_WARM_PASS") or os.getenv("SMTP_PASS", ""),
        "type":     "warm",
    }


# ─── DAILY LIMIT TRACKER ─────────────────────────────────────────────────────

SEND_LOG_FILE = "send_log.json"

def _load_send_log() -> dict:
    today = str(date.today())
    if os.path.exists(SEND_LOG_FILE):
        try:
            with open(SEND_LOG_FILE, "r") as f:
                data = json.load(f)
            if data.get("date") == today:
                return data
        except:
            pass
    return {"date": today, "accounts": {}, "sent_domains": [], "dnc": []}


def _save_send_log(log: dict):
    with open(SEND_LOG_FILE, "w") as f:
        json.dump(log, f)


def get_sends_today(account_user: str) -> int:
    log = _load_send_log()
    return log["accounts"].get(account_user, 0)


def record_send(account_user: str, domain: str, lead_id: str):
    log = _load_send_log()
    log["accounts"][account_user] = log["accounts"].get(account_user, 0) + 1
    if domain not in log["sent_domains"]:
        log["sent_domains"].append(domain)
    _save_send_log(log)


def domain_sent_today(domain: str) -> bool:
    log = _load_send_log()
    return domain in log["sent_domains"]


def is_dnc(email: str, db=None) -> bool:
    log = _load_send_log()
    if email in log.get("dnc", []):
        return True
    if db:
        try:
            leads = db.fetch_leads({"email": f"eq.{email}", "status": "eq.DNC"})
            return len(leads) > 0
        except:
            pass
    return False


# ─── ACCOUNT SELECTOR ────────────────────────────────────────────────────────

def select_account_for_lead(niche: str, email: str, db=None) -> Optional[dict]:
    if is_dnc(email, db):
        logger.info(f"Skipping {email} — on DNC list")
        return None

    domain = email.split("@")[-1] if "@" in email else ""
    if domain_sent_today(domain):
        logger.info(f"Skipping {email} — domain {domain} already contacted today")
        return None

    accounts = load_accounts()
    niche_lower = niche.lower()

    available = []
    for acc in accounts:
        niche_match = ("all" in acc["niches"] or any(n in niche_lower for n in acc["niches"]))
        if not niche_match: continue

        sent_today = get_sends_today(acc["user"])
        remaining = acc["daily_limit"] - sent_today

        if remaining <= 0:
            logger.info(f"Account {acc['user']} at daily limit")
            continue

        available.append({**acc, "remaining": remaining, "sent_today": sent_today})

    if not available:
        logger.warning(f"No accounts available for niche '{niche}'")
        return None

    best = max(available, key=lambda a: a["remaining"])
    return best


# ─── EMAIL SENDER ─────────────────────────────────────────────────────────────

def send_cold_email(
    to_email:      str,
    subject:       str,
    body_text:     str,
    body_html:     str,
    niche:         str,
    lead_id:       str,
    in_reply_to:   Optional[str] = None,
    db=None,
) -> dict:
    account = select_account_for_lead(niche, to_email, db)
    if not account:
        return {"success": False, "reason": "No account available", "reschedule": True}

    result = _send_via_account(
        account=account,
        to_email=to_email,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        in_reply_to=in_reply_to,
    )

    if result["success"]:
        record_send(account["user"], to_email.split("@")[-1], lead_id)
        if db:
            try:
                db.update_lead(lead_id, {"pitch_sent": True, "sent_from_account": account["user"], "status": "Contacted"})
            except: pass
    return result


def send_warm_email(
    to_email:    str,
    subject:     str,
    body_text:   str,
    body_html:   str,
    lead_id:     str = "",
    in_reply_to: Optional[str] = None,
    attachment_bytes: Optional[bytes] = None,
    attachment_filename: Optional[str] = None,
) -> dict:
    account = get_warm_account()
    if not account["user"]:
        return {"success": False, "reason": "SMTP_WARM_USER not configured"}

    result = _send_via_account(
        account=account,
        to_email=to_email,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        in_reply_to=in_reply_to,
        attachment_bytes=attachment_bytes,
        attachment_filename=attachment_filename,
    )
    result["track"] = "warm"
    return result


def _send_via_account(
    account:     dict,
    to_email:    str,
    subject:     str,
    body_text:   str,
    body_html:   str,
    in_reply_to: Optional[str] = None,
    attachment_bytes: Optional[bytes] = None,
    attachment_filename: Optional[str] = None,
) -> dict:
    agency_name = os.getenv("AGENCY_NAME", "RI2CH Agency")
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, f"{agency_name} <{account['user']}>", to_email
    msg["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"]  = in_reply_to

    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    if attachment_bytes and attachment_filename:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{attachment_filename}"')
        
        # Re-wrap as mixed to support attachments
        main_msg = MIMEMultipart("mixed")
        main_msg["Subject"], main_msg["From"], main_msg["To"] = msg["Subject"], msg["From"], msg["To"]
        main_msg.attach(msg)
        main_msg.attach(part)
        msg = main_msg

    try:
        # Use SMTP_SSL for port 465, or standard SMTP for other ports.
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
            server.starttls()
            
        with server as s:
            s.login(account["user"], account["password"])
            s.sendmail(account["user"], to_email, msg.as_string())
        return {"success": True, "error": None, "account_used": account["user"]}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─── DAILY STATUS REPORT ─────────────────────────────────────────────────────

def get_daily_status() -> dict:
    accounts  = load_accounts(); log = _load_send_log(); warm_acc = get_warm_account()
    status = {"date": str(date.today()), "accounts": [], "total_sent": 0, "total_capacity": 0, "total_remaining": 0, "domains_cooled": len(log.get("sent_domains", [])), "warm_account": warm_acc.get("user", "Not configured")}

    for acc in accounts:
        sent = log["accounts"].get(acc["user"], 0); remaining = max(0, acc["daily_limit"] - sent)
        status["accounts"].append({"account": acc["user"], "niches": acc["niches"], "sent": sent, "limit": acc["daily_limit"], "remaining": remaining, "status": "AT LIMIT" if remaining == 0 else "AVAILABLE"})
        status["total_sent"] += sent; status["total_capacity"] += acc["daily_limit"]; status["total_remaining"] += remaining
    return status


def print_daily_status():
    s = get_daily_status(); print(f"\n{'='*55}\n  SILAS - DAILY SEND STATUS ({s['date']})\n{'='*55}")
    for acc in s["accounts"]:
        bar = ("#" * acc["sent"] + "." * acc["remaining"])[:30]
        print(f"\n  {acc['account']}\n  Niches:    {', '.join(acc['niches'])}\n  Progress:  {bar}  {acc['sent']}/{acc['limit']}\n  Status:    {acc['status']}")
    print(f"\n  TOTAL:     {s['total_sent']} sent / {s['total_capacity']} capacity\n  REMAINING: {s['total_remaining']} sends available\n{'='*55}\n")

if __name__ == "__main__":
    print_daily_status()
