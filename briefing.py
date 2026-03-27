import json
from database import db
from typing import Dict, Any
from silas_accounts import get_daily_status

def get_briefing_metrics() -> Dict[str, Any]:
    """
    Aggregates metrics for the 'Briefing.' command using high-performance count queries.
    """
    try:
        # 1. Money Alerts
        paid_leads = db.fetch_table("leads", {"payment_status": "eq.paid"}, limit=5)
        money_alerts = []
        for lead in paid_leads:
            money_alerts.append({
                "name": lead.get("business_name", "Unknown"),
                "amount": lead.get("amount_paid", 0),
                "date": lead.get("paid_at", "Recent")
            })

        # 2. Pipeline Status (Optimized Counts)
        scraped = db.get_count("leads", {"status": "in.(New,Qualified)"})
        audited = db.get_count("leads", {"status": "ilike.*audit*"})
        shadow_ready = db.get_count("leads", {"status": "in.(Demo Ready,Site Generated,Shadow Site Ready)"})
        outreach_sent = db.get_count("leads", {"status": "eq.Contacted"}) # Updated status mapping
        replied = db.get_count("leads", {"status": "ilike.*replied*"})

        total_sent = outreach_sent + replied
        reply_rate = (replied / total_sent * 100) if total_sent > 0 else 0

        # 3. Email Account Status (Silas)
        email_status = get_daily_status()

        # 4. Errors
        failed_tasks = db.fetch_table("tasks", {"status": "eq.failed"}, limit=5)

        return {
            "money": money_alerts,
            "pipeline": {
                "scraped": scraped,
                "audited": audited,
                "shadow_ready": shadow_ready,
                "outreach_sent": outreach_sent,
                "replied": replied,
                "reply_rate": round(reply_rate, 1)
            },
            "email_capacity": {
                "total_sent": email_status["total_sent"],
                "total_remaining": email_status["total_remaining"],
                "accounts": email_status["accounts"]
            },
            "errors": [t.get("error_message", "Unknown error") for t in failed_tasks],
            "recommendation": _get_recommendation({
                "scraped": scraped,
                "audited": audited,
                "shadow_ready": shadow_ready,
                "outreach_sent": outreach_sent
            })
        }
    except Exception as e:
        return {"error": str(e)}

def _get_recommendation(pipeline: Dict[str, int]) -> str:
    if pipeline["scraped"] < 50:
        return "MODE: SCRAPE — Pipeline is running low on fresh leads."
    if pipeline["audited"] > 5 and pipeline["shadow_ready"] < 2:
        return "MODE: BUILD — Audited Whales are sitting without shadow sites."
    if pipeline["outreach_sent"] < 100 and pipeline["shadow_ready"] > 0:
        return "MODE: SEND — Shadow sites are ready for pitching."
    return "MODE: AUDIT PRODUCT — Focus on bringing in quick $47 purchases."

if __name__ == "__main__":
    metrics = get_briefing_metrics()
    print(json.dumps(metrics, indent=2))
