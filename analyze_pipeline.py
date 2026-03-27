from database import db
from collections import Counter
from datetime import datetime
import json

def analyze_pipeline():
    # 1. Total Lead Count
    # Simulating a count query by selecting * but we'll use a better approach if possible.
    # For now, let's just fetch all and count.
    leads = db.fetch_leads() # This might be limited by the API, let's verify.
    total_in_memory = len(leads)
    
    # 2. Outreach Mapping
    # We look for leads that have been contacted.
    # We'll check both 'status' and 'sent_at' (if it exists) or 'created_at' as fallback for now.
    outreach_by_day = Counter()
    
    # Let's also check activity_logs for 'Email sent' messages
    logs = db.fetch_logs(limit=1000)
    for log in logs:
        msg = log.get("message", "").lower()
        if "email sent" in msg or "sent email" in msg or "audit delivered" in msg:
            date_str = log.get("created_at", "")[:10] # YYYY-MM-DD
            if date_str:
                outreach_by_day[date_str] += 1

    # 3. Status Breakdown
    status_counts = Counter()
    for lead in leads:
        status_counts[lead.get("status", "Unknown")] += 1

    print(json.dumps({
        "total_leads_fetched": total_in_memory,
        "outreach_mapping": dict(sorted(outreach_by_day.items())),
        "status_breakdown": dict(status_counts)
    }, indent=2))

if __name__ == "__main__":
    analyze_pipeline()
