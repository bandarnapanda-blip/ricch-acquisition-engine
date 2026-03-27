import os
import logging
from database import db

# Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backfill_diamond")

def main():
    logger.info("Starting Diamond Metadata Backfill...")
    
    # 1. List all files in diamond_reports
    folder = "diamond_reports"
    if not os.path.exists(folder):
        logger.warning("No diamond_reports folder found.")
        return

    files = [f for f in os.listdir(folder) if f.endswith(".html")]
    logger.info(f"Found {len(files)} local reports.")

    # 2. Fetch all leads to match names
    leads = db.fetch_leads()
    
    count = 0
    for f in files:
        # File format: biz-name-audit.html
        biz_slug = f.replace("-audit.html", "").replace("-", " ")
        
        # Find matching lead
        match = None
        for l in leads:
            biz_name = (l.get('business_name') or "").lower()
            if biz_name and (biz_slug in biz_name or biz_name in biz_slug):
                match = l
                break
        
        if match:
            lid = match['id']
            audit_url = f"https://bandarnapanda-blip.github.io/ricch-acquisition-engine/diamond_reports/{f}"
            
            import json
            # Update DB using website_roast as JSON carrier
            db.update_lead(lid, {
                "website_roast": json.dumps({
                    "diamond_audit_url": audit_url,
                    "diamond_audit_path": os.path.join(folder, f),
                    "annual_leakage": "Calculating..."
                })
            })
            logger.info(f"✅ Synced {match.get('business_name')} -> {audit_url}")
            count += 1
        else:
            logger.warning(f"❓ Could not match file: {f}")

    logger.info(f"Backfill Complete. {count} leads updated.")

if __name__ == "__main__":
    main()
