import time
import logging
from database import db
from intelligence import compute_deal_score, LeadSignals
from diamond_generator import generate_diamond_report

# Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("intelligence_worker")

POLL_INTERVAL = 30  # seconds
ENGAGEMENT_THRESHOLD_SECONDS = 60
SCROLL_THRESHOLD_PCT = 50

def process_behavioral_signals():
    logger.info("Polling site_events for behavioral signals...")
    
    # 1. Fetch recent events (last 1 hour)
    events = db._session.get(f"{db.url}/rest/v1/site_events?order=created_at.desc&limit=100", headers=db.headers).json()
    
    # 2. Aggregate by lead_id
    stats = {}
    for ev in events:
        lid = ev.get('lead_id')
        if not lid: continue
        
        if lid not in stats:
            stats[lid] = {"time_on_site": 0, "max_scroll": 0, "events": 0}
            
        stats[lid]["events"] += 1
        if ev.get('event_type') == 'heartbeat':
            stats[lid]["time_on_site"] += 10 # approximate
        if ev.get('event_type') == 'scroll':
            scroll = ev.get('metadata', {}).get('scroll_pct', 0)
            stats[lid]["max_scroll"] = max(stats[lid]["max_scroll"], scroll)

    # 3. Score and Promote
    for lid, behavioral in stats.items():
        # Calculate behavioral score (0-100)
        # 60s+ = 70 points, 2 mins+ = 100 points
        score = min(100, (behavioral["time_on_site"] / 120) * 100)
        
        # Pull lead to update
        lead_list = db.fetch_leads(filters={"id": f"eq.{lid}"})
        if not lead_list: continue
        lead = lead_list[0]
        
        current_status = lead.get('status')
        
        # Promotion Logic
        if behavioral["time_on_site"] >= ENGAGEMENT_THRESHOLD_SECONDS or behavioral["max_scroll"] >= SCROLL_THRESHOLD_PCT:
            if current_status != 'Hot Prospect':
                logger.info(f"🔥 PROMOTING {lid} to Hot Prospect! (Time: {behavioral['time_on_site']}s)")
                db.update_lead(lid, {"status": "Hot Prospect", "behavioral_score": score})
                
                # [PHASE 2] Automated Diamond Trigger
                logger.info(f"💎 TRIGGERING Diamond Audit for {lid}...")
                report_path = generate_diamond_report(lid)
                if report_path:
                    db.update_lead(lid, {"metadata->>diamond_audit_path": report_path})
                    # Log activity
                    db._session.post(f"{db.url}/rest/v1/activity_logs", headers=db.headers, json={
                        "lead_id": lid,
                        "message": f"Diamond Audit generated automatically after {behavioral['time_on_site']}s engagement."
                    })
        else:
            # Update score regardless if engaged at all
            if score > (lead.get('behavioral_score') or 0):
                db.update_lead(lid, {"behavioral_score": score})

def main():
    logger.info("Intelligence Worker ACTIVE")
    while True:
        try:
            process_behavioral_signals()
        except Exception as e:
            logger.error(f"Worker Error: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
