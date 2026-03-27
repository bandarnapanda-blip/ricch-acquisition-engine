import os
import time
import random
import argparse
from dotenv import load_dotenv
from database import db
from silas_accounts import send_cold_email

load_dotenv()

def get_audited_leads():
    """Fetch leads that have been audited and are ready for the $47 pitch."""
    # Filter: Status == 'Audited' via Supabase natively
    targets = db.fetch_leads(filters={"status": "eq.Audited"})
    return targets

def generate_audit_pitch(lead):
    """Constructs the $47 Audit Strike pitch."""
    raw_name = lead.get('business_name')
    if not raw_name or raw_name.lower() == 'none':
        website = lead.get('website', '')
        if website:
            raw_name = website.split('//')[-1].split('/')[0].replace('www.', '').split('.')[0].capitalize()
        else:
            raw_name = "Valued Partner"
    
    name = raw_name.replace('None', '').strip() or "Valued Partner"
    city = lead.get('city') or "your area"
    loss = lead.get('revenue_loss', 5000)
    
    # We send them to the $47 landing page (simulated here or actual URL if deployed)
    # The URL can be loaded from env, typically it's the audit_landing page hosted somewhere
    # Since we are local, we'll point to a generic domain or the agency domain.
    agency_url = os.getenv("AGENCY_URL", "https://ri2ch.agency")
    audit_link = f"{agency_url}/audit"
    
    subject = f"Your {name} website audit results"
    
    body_text = f"Hi {name} Team,\n\nI'm reaching out from the RI2CH Intelligence division. We just completed a technical audit of {name} and identified severe 'Revenue Leakage' resulting in a loss of approx ${loss:,.0f}/month.\n\nWe compiled a 20-page Silicon Valley Technical Audit report detailing exactly what is broken and how to fix it.\n\nYou can claim your full report here for a one-time fee of $47: {audit_link}\n\nBest,\nSilas"
    
    body_html = f"""<html><body>
    <p>Hi {name} Team,</p>
    <p>I'm reaching out from the RI2CH Intelligence division. During our recent technical audit of businesses in {city}, we identified significant 'Revenue Leakage' on your current digital storefront.</p>
    <p>Based on our analysis, your current site is lacking critical Core Web Vitals optimizations, resulting in a loss of approximately <b>${loss:,.0f}/month</b> in missed conversions.</p>
    <p>We've compiled a full 20-page <b>Silicon Valley Technical Audit</b> report detailing exactly what is broken—and exactly how your developers can fix it.</p>
    <p>You can instantly claim your full report for a one-time fee of <b>$47</b> here:<br/>
    <a href='{audit_link}'>Get The Audit Report</a></p>
    <p>Best regards,<br/>Silas<br/>RI2CH Agency OS</p>
    </body></html>"""
    
    return subject, body_text, body_html

def run_audit_wave(limit=50, dry_run=True):
    print(f"--- AUDIT OUTREACH WAVE: STARTING (Dry Run: {dry_run}) ---")
    
    targets = get_audited_leads()
    to_pitch = targets[:limit]
    
    print(f"Targeting {len(to_pitch)} Audited Leads.")
    print("---------------------------------------------------------")
    
    success = 0
    
    for i, lead in enumerate(to_pitch):
        primary_email = lead.get('email')
        candidates = lead.get('candidate_emails', [])
        lid = lead.get('id')
        name = lead.get('business_name')
        niche = lead.get('niche', 'General')
        
        target_email = None
        if candidates and isinstance(candidates, list) and len(candidates) > 0:
            target_email = candidates[0]
        elif primary_email and "@" in primary_email:
            target_email = primary_email
            
        if not target_email:
            print(f"[{i+1}/{len(to_pitch)}] Skipping {name}: No qualified target email found.")
            continue
            
        subject, body_text, body_html = generate_audit_pitch(lead)
        
        if dry_run:
            print(f"[{i+1}/{len(to_pitch)}] [DRY RUN] Pitching {name} ({target_email})")
            success += 1
            continue

        print(f"[{i+1}/{len(to_pitch)}] Pitching {name} ({target_email})...")
        
        result = send_cold_email(
            to_email=target_email,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            niche=niche,
            lead_id=lid,
            db=db
        )
        
        if result["success"]:
            success += 1
            acc_used = result.get("account_used", "Unknown")
            rem = result.get("remaining_today", 0)
            print(f"       [SUCCESS] Sent via {acc_used} | {rem} remaining.")
            
            # Anti-ban jitter
            delay = random.randint(3, 10)
            print(f"       Waiting {delay}s for momentum...")
            time.sleep(delay)
        else:
            print(f"       [SKIPPED/FAILED] {result.get('reason', result.get('error', 'Unknown'))}")

    print("\n" + "="*50)
    print(f" AUDIT WAVE SUMMARY: {success} Pitches Processed")
    print("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit Product Outreach Wave")
    parser.add_argument("--send", action="store_true", help="Launch real outreach")
    parser.add_argument("--limit", type=int, default=50, help="Number of leads to pitch")
    args = parser.parse_args()
    
    run_audit_wave(limit=args.limit, dry_run=not args.send)
