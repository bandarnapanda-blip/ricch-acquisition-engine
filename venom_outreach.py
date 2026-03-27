import os
import time
import random
import argparse
from dotenv import load_dotenv
from database import db
from silas_accounts import send_cold_email

load_dotenv()

def get_whales():
    """Fetch elite whales ready for outreach."""
    leads = db.fetch_leads()
    # Filter: Score >= 75 AND has a demo link AND not already contacted
    whales = [
        l for l in leads 
        if l.get('opportunity_score', 0) >= 75 
        and l.get('demo_link') 
        and l.get('status') != 'Contacted'
    ]
    return sorted(whales, key=lambda x: x.get('opportunity_score', 0), reverse=True)

def generate_pitch(lead):
    """Constructs a high-impact, data-driven pitch."""
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
    demo = lead.get('demo_link')
    
    subject = f"Urgent: Revenue Leakage spotted at {name}"
    
    body_text = f"Hi {name} Team,\n\nI'm reaching out from the RI2CH Intelligence division. We identified significant 'Revenue Leakage' on your site in {city}.\n\nAnalysis shows a loss of approx ${loss:,.0f}/month.\n\nSee the solution we built for you here: {demo}\n\nBest,\nSilas"
    
    body_html = f"""<html><body>
    <p>Hi {name} Team,</p>
    <p>I'm reaching out from the RI2CH Intelligence division. During our recent technical audit of businesses in {city}, we identified significant 'Revenue Leakage' on your current digital storefront.</p>
    <p>Based on our analysis, your current site is likely resulting in a loss of approximately <b>${loss:,.0f}/month</b> in missed conversion opportunities.</p>
    <p>We've already built a fully functional concept that solves these specific issues for you here:<br/>
    <a href='{demo}'>{demo}</a></p>
    <p>Would you be open to a 5-minute walkthrough of how we can deploy this as your new primary asset?</p>
    <p>Best regards,<br/>Silas<br/>RI2CH Agency OS</p>
    </body></html>"""
    
    return subject, body_text, body_html

def run_venom_wave(limit=50, dry_run=True):
    print(f"--- VENOM OUTREACH WAVE: STARTING (Dry Run: {dry_run}) ---")
    print(f"--- PROTOCOL: VERIFY-FIRST ACTIVATED ---")
    
    whales = get_whales()
    targets = whales[:limit]
    
    print(f"Targeting {len(targets)} elite Whales across Silas accounts.")
    print("---------------------------------------------------------")
    
    success = 0
    
    for i, lead in enumerate(targets):
        primary_email = lead.get('email')
        candidates = lead.get('candidate_emails', [])
        lid = lead.get('id')
        name = lead.get('business_name')
        niche = lead.get('niche', 'General')
        
        # Determine the best target email
        target_email = None
        if candidates and isinstance(candidates, list) and len(candidates) > 0:
            # Prioritize the first candidate (usually more specific)
            target_email = candidates[0]
        elif primary_email and "@" in primary_email:
            # Use primary as fallback, but audit for high-risk generic aliases
            # These aliases have a high bounce rate or are often monitored by gatekeepers
            generic_aliases = ["info@", "admin@", "contact@", "support@", "office@", "hello@", "frontdesk@"]
            if any(alias in primary_email.lower() for alias in generic_aliases):
                print(f"[{i+1}/{len(targets)}] Skipping {name}: Primary email is a high-risk generic alias ({primary_email}).")
                continue
            target_email = primary_email
            
        if not target_email:
            print(f"[{i+1}/{len(targets)}] Skipping {name}: No qualified target email found.")
            continue
            
        subject, body_text, body_html = generate_pitch(lead)
        
        if dry_run:
            print(f"[{i+1}/{len(targets)}] [DRY RUN] Pitching {name} ({target_email}) | Niche: {niche}")
            success += 1
            continue

        print(f"[{i+1}/{len(targets)}] Pitching {name} ({target_email}) via Silas rotation...")
        
        # Using Silas Multi-Account Engine
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
            print(f"       [SUCCESS] Sent via {acc_used} | {rem} remaining for this account.")
            
            # Anti-ban jitter
            delay = random.randint(30, 90)
            print(f"       Waiting {delay}s for safety...")
            time.sleep(delay)
        else:
            print(f"       [SKIPPED/FAILED] {result.get('reason', result.get('error', 'Unknown'))}")
            if result.get("reschedule"):
                print("       (Domain cooldown or account limit hit. Moving to next niche/lead.)")

    print("\n" + "="*50)
    print(f" VENOM SUMMARY: {success} Pitches Processed")
    print("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Venom Outreach Wave")
    parser.add_argument("--send", action="store_true", help="Launch real outreach")
    parser.add_argument("--limit", type=int, default=50, help="Number of leads to pitch")
    args = parser.parse_args()
    
    run_venom_wave(limit=args.limit, dry_run=not args.send)
