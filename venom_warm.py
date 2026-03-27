import os
import time
import random
import argparse
from dotenv import load_dotenv
from database import db
from silas_accounts import send_cold_email

load_dotenv()

def get_target_warm_leads(limit=200):
    """Fetch leads in the Warm tier (Score 51-74) for the $47 strike."""
    print("--- FETCHING WARM LEADS (SCORE 51-74) ---")
    all_leads = db.fetch_leads()
    
    # Tier filtering: Score 51-74 AND qualified status
    targets = [
        l for l in all_leads 
        if 51 <= l.get('opportunity_score', 0) <= 74 
        and l.get('status') not in ['Contacted', 'Closed', 'Delivered', 'DNC']
        and (l.get('email') or (l.get('candidate_emails') and len(l.get('candidate_emails')) > 0))
    ]
    
    # Sort by score desc primarily (best of warm first)
    targets.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
    
    return targets[:limit]

def generate_warm_pitch(lead):
    """Constructs the $47 Audit Floodgate pitch."""
    raw_name = lead.get('business_name')
    if not raw_name or raw_name.lower() in ['none', 'unknown', 'unknown business']:
        website = lead.get('website', '')
        if website:
            raw_name = website.split('//')[-1].split('/')[0].replace('www.', '').split('.')[0].capitalize()
        else:
            raw_name = "Business Owner"
    
    name = raw_name.replace('None', '').replace('Unknown', '').strip() or "Business Owner"
    city = lead.get('city') or "your area"
    loss = lead.get('revenue_loss', 2500)
    
    agency_url = os.getenv("AGENCY_URL", "https://ri2ch.agency")
    audit_link = f"{agency_url}/audit"
    
    subject = f"Urgent: {name} website performance audit"
    
    body_text = f"Hi {name} Team,\n\nI'm Silas from the RI2CH Intelligence division. We've identified approximately ${loss:,.0f}/month in 'Revenue Leakage' on your current site due to basic technical errors.\n\nWe've generated a 20-page Professional Audit report that highlights exactly how to plug these holes.\n\nYou can claim the full report here for $47: {audit_link}\n\nBest,\nSilas"
    
    body_html = f"""<html><body>
    <p>Hi {name} Team,</p>
    <p>I'm Silas from the RI2CH Intelligence division. We just completed a high-level scan of {name}'s current digital infrastructure.</p>
    <p>Our intelligence engine detected approximately <b>${loss:,.0f}/month</b> in 'Revenue Leakage' caused by standard technical friction points that are invisible to the naked eye.</p>
    <p>I have a <b>20-page Professional Audit</b> report ready for you that breaks down every critical fix required to recover this revenue.</p>
    <p>You can instantly claim your report for $47 here:<br/>
    <a href='{audit_link}'>Claim Audit Report ($47)</a></p>
    <p>Best regards,<br/>Silas<br/>RI2CH Agency OS</p>
    </body></html>"""
    
    return subject, body_text, body_html

def run_warm_wave(limit=50, dry_run=True):
    print(f"--- WARM FLOODGATE STRIKE ($47): STARTING (Dry Run: {dry_run}) ---")
    
    targets = get_target_warm_leads(limit=limit)
    print(f"Targeting {len(targets)} available Warm leads.")
    print("---------------------------------------------------------")
    
    success = 0
    
    for i, lead in enumerate(targets):
        primary_email = lead.get('email')
        candidates = lead.get('candidate_emails', [])
        lid = lead.get('id')
        raw_biz = lead.get('business_name') or ""
        if not raw_biz or raw_biz.lower() in ['none', 'unknown', 'unknown business']:
            biz_name = "Business Owner"
        else:
            biz_name = raw_biz
        # The original 'name' variable assignment is replaced by 'biz_name' logic
        niche = lead.get('niche', 'General')
        score = lead.get('opportunity_score', 0)
        
        target_email = None
        if candidates and isinstance(candidates, list) and len(candidates) > 0:
            target_email = candidates[0]
        elif primary_email and "@" in primary_email:
            target_email = primary_email
            
        if not target_email:
            continue
            
        subject, body_text, body_html = generate_warm_pitch(lead)
        
        if dry_run:
            print(f"[{i+1}/{len(targets)}] [DRY RUN] Pitching {biz_name} (Score: {score}) at {target_email}")
            success += 1
            continue

        print(f"[{i+1}/{len(targets)}] Pitching {biz_name} (Score: {score}) via {target_email}...")
        
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
            db.push_log("Silas", f"Warm Floodgate payload ($47) delivered to {biz_name} (Score: {score}) via {acc}")
            
            # Anti-ban protocol
            delay = random.randint(3, 10) # Faster jitter for $47 volume
            print(f"       Waiting {delay}s for momentum...")
            time.sleep(delay)
        else:
            print(f"       [SKIPPED/FAILED] {result.get('reason', result.get('error', 'Unknown'))}")

    print("\n" + "="*50)
    print(f" WARM FLOODGATE SUMMARY: {success} Pitches Processed")
    print("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Warm Lead ($47) Floodgate Strike")
    parser.add_argument("--send", action="store_true", help="Launch real outreach")
    parser.add_argument("--limit", type=int, default=50, help="Number of leads to pitch")
    args = parser.parse_args()
    
    run_warm_wave(limit=args.limit, dry_run=not args.send)
