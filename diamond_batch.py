import logging
import time
from database import db
from diamond_generator import generate_diamond_report

# Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("diamond_batch")

def main():
    logger.info("🚀 INITIATING DIAMOND WAVE: Target=25 high-value leads")

    # [SCALE] Fetch top leads with score >= 95
    # Limit to 25 to respect Gemini quota and storage
    url = f"{db.url}/rest/v1/leads?opportunity_score=gte.95&business_name=not.is.null&limit=25&order=opportunity_score.desc"
    resp = db._session.get(url, headers=db.headers)
    targets = resp.json()

    if not targets:
        logger.warning("No targets found matching criteria.")
        return

    logger.info(f"Targets Identified: {[t.get('business_name') for t in targets]}")

    for i, t in enumerate(targets):
        lead_id = t.get('id')
        biz_name = t.get('business_name')
        
        logger.info(f"--- Processing Diamond {i+1}/{len(targets)}: {lead_id} ({biz_name}) ---")
        
        try:
            report_path = generate_diamond_report(lead_id)
            if report_path:
                logger.info(f"✅ Diamond Audit Ready: {report_path}")
            else:
                logger.error(f"❌ Failed for {biz_name}")
        except Exception as e:
            logger.error(f"💥 Error processing {biz_name}: {e}")

        # Respect Gemini rate limits (65s delay for safe batching)
        if i < len(targets) - 1:
            logger.info("⏳ Respecting Gemini Quota... Sleeping 65 seconds.")
            time.sleep(65)

    logger.info("🏁 DIAMOND WAVE COMPLETE.")

if __name__ == "__main__":
    main()
