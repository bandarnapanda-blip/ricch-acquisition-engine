import sys
import os
import time
sys.path.append('.')
from database import db
from analyzer import analyze_site, calculate_opportunity_score, calculate_revenue_loss

def run_refill_burst(limit=20):
    print(f"--- REFILLING AUDITED BUCKET (LIMIT: {limit}) ---")
    # Get leads that are Shadow Site Ready but not yet Audited
    leads = db.fetch_leads(filters={'status': 'eq.Shadow Site Ready'})
    print(f"Total Ready Leads: {len(leads)}")
    
    refill_count = 0
    
    for i, lead in enumerate(leads[:limit]):
        website = lead.get('website')
        if not website:
            continue
            
        print(f"[{i+1}/{limit}] Auditing: {website}")
        
        try:
            # Perform the technical audit
            audit_res = analyze_site(website)
            if audit_res:
                score = calculate_opportunity_score(audit_res)
                loss = calculate_revenue_loss('General', audit_res)
                
                # Update status and data
                db.update_lead(lead['id'], {
                    'status': 'Audited',
                    'opportunity_score': score,
                    'revenue_loss': loss
                })
                print(f"    [SUCCESS] Score: {score} | Loss: ${loss}/mo")
                refill_count += 1
            else:
                print("    [FAILED] No audit results")
        except Exception as e:
            print(f"    [ERROR] {e}")
            
        time.sleep(1)

    print(f"\n--- REFILL COMPLETE: {refill_count} leads promoted to Audited ---")

def main():
    run_refill_burst(limit=20)

if __name__ == "__main__":
    main()
