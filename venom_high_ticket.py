import os
import time
import random
import argparse
import json
from dotenv import load_dotenv
from database import db
from silas_accounts import send_cold_email

load_dotenv()

def get_target_whales():
    """Fetch elite whales specifically for the $1,500 production offer."""
    leads = db.fetch_leads()
    # Filter: Score >= 75 AND has a demo link AND not already 'Contacted' OR 'Nurturing'
    # We want to catch even those who were contacted before if they are high value, 
    # but for Wave 1 we focus on fresh ones.
    whales = [
        l for l in leads 
        if l.get('opportunity_score', 0) >= 75 
        and l.get('demo_link') 
        and l.get('status') not in ['Closed', 'Delivered']
    ]
    return sorted(whales, key=lambda x: x.get('opportunity_score', 0), reverse=True)

def generate_high_ticket_pitch(lead):
    """Constructs the elite $1,500 'Revenue Recovery' pitch."""
    raw_biz = lead.get('business_name') or ""
    if not raw_biz or raw_biz.lower() in ['none', 'unknown', 'unknown business']:
        biz_name = "Business Owner"
    else:
        biz_name = raw_biz
    city = lead.get('city') or "your area"
    demo = lead.get('demo_link')
    score = lead.get('opportunity_score', 0)
    
    # Calculate revenue leakage accurately from the roast if possible
    loss = 5000 # Default
    roast = lead.get('website_roast', '')
    if roast:
        try:
            # Check if it's JSON from analyzer.py or a string from task_audit_lead
            if roast.startswith('{'):
                data = json.loads(roast)
                leak_str = data.get('annual_leakage', '60000').replace('$', '').replace(',', '').strip()
                loss = float(leak_str) / 12
            else:
                # Heuristic parse if it's just a text roast
                import re
                match = re.search(r'\$(\d+,?\d+)', roast)
                if match:
                    loss = float(match.group(1).replace(',', '')) / 12
        except:
            pass

    subject = f"Priority Briefing: Recouping ${loss:,.0f}/mo at {biz_name}"
    
    body_text = f"Hi {biz_name} Team,\n\nI'm Silas from RI2CH. My technical intelligence audit of {biz_name} discovered a critical performance delta that is likely costing you ${loss:,.0f} per month in lost digital conversions.\n\nWe've already built the solution. You can view the live technical prototype here: {demo}\n\nWe are looking to merge this into your live domain this week for a one-time production fee of $1,500. This includes full DNS activation and hosting infrastructure.\n\nAre you open to a quick technical review today?\n\nBest,\nSilas\nRI2CH Agency"
    
    body_html = f"""<html><body>
    <p>Hi {biz_name} Team,</p>
    <p>I'm Silas from the RI2CH technical intelligence division. During our recent performance audit of businesses in {city}, we identified a critical performance delta on your current storefront that is likely costing you approximately <b>${loss:,.0f} per month</b> in lost digital conversions.</p>
    <p>Because the opportunity is high, we've already built the full-stack solution for you. Your live technical prototype is staged here:</p>
    <p><a href='{demo}'><b>VIEW LIVE PROTOTYPE →</b></a></p>
    <p>We are ready to merge this production-grade asset into your live domain this week. The <b>$1,500 one-time production fee</b> covers full DNS activation, high-performance hosting, and the final production merge.</p>
    <p>Would you be open to a 2-minute walkthrough of the technical recovery plan today?</p>
    <p>Best regards,<br/><b>Silas</b><br/>Lead Agent | RI2CH Agency OS</p>
    </body></html>"""
    
    return subject, body_text, body_html

def run_high_ticket_wave(limit=20, dry_run=True):
    print(f"--- WHALE STRIKE ($1,500 OFFER): STARTING (Dry Run: {dry_run}) ---")
    
    targets = get_target_whales()
    active_batch = targets[:limit]
    
    print(f"Targeting {len(active_batch)}/ {len(targets)} available elite Whales.")
    print("---------------------------------------------------------")
    
    success = 0
    
    for i, lead in enumerate(active_batch):
        # Data scrubbing
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
            print(f"[{i+1}/{len(active_batch)}] Skipping {name}: No reachable email.")
            continue
            
        subject, body_text, body_html = generate_high_ticket_pitch(lead)
        
        if dry_run:
            print(f"[{i+1}/{len(active_batch)}] [DRY RUN] High-Ticket Pitch to {name} ({target_email})")
            print(f"       Sub: {subject}")
            success += 1
            continue

        print(f"[{i+1}/{len(active_batch)}] Dispatching $1,500 payload to {name}...")
        
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
            acc = result.get("account_used", "Silas")
            print(f"       [SUCCESS] Sent via {acc}.")
            
            # God View Visibility
            db.push_log("Silas", f"High-Ticket payload ($1,500) delivered to {name} via {acc}")
            
            # Anti-ban protocol
            delay = random.randint(30, 90)
            print(f"       Waiting {delay}s for safety...")
            time.sleep(delay)
        else:
            print(f"       [FAILED] {result.get('error', 'Unknown error')}")

    print("\n" + "="*50)
    print(f" STRIKE SUMMARY: {success} payloads delivered.")
    print("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Silas $1,500 Whale Strike Engine")
    parser.add_argument("--send", action="store_true", help="Launch live outreach")
    parser.add_argument("--limit", type=int, default=20, help="Number of leads to target")
    args = parser.parse_args()
    
    run_high_ticket_wave(limit=args.limit, dry_run=not args.send)
