from database import db
import json

def get_diamond_stats():
    leads = db.fetch_leads()
    audits = []
    for l in leads:
        roast = l.get('website_roast')
        if roast:
            try:
                data = json.loads(roast)
                if data.get('diamond_audit_url'):
                    l['metadata'] = data # Mock metadata for the print logic
                    audits.append(l)
            except:
                pass
    
    print(f"LEAD INTELLIGENCE SUMMARY")
    print(f"Total Leads Tracked: {len(leads)}")
    print(f"Live Diamond Audits Ready: {len(audits)}")
    print("-" * 30)
    print("🔥 TOP DIAMOND PROSPECTS")
    
    # Sort by opportunity score
    sorted_audits = sorted(audits, key=lambda x: x.get('opportunity_score', 0), reverse=True)
    
    for i, l in enumerate(sorted_audits[:10]):
        biz = l.get('business_name', 'Unknown')
        score = l.get('opportunity_score', 0)
        status = l.get('status', 'N/A')
        leak = l.get('metadata', {}).get('annual_leakage', 'Calculating...')
        print(f"{i+1}. {biz} (Score: {score}) - Leak: ${leak}/yr [{status}]")

if __name__ == "__main__":
    get_diamond_stats()
