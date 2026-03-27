from database import db
import os
import json

def final_check():
    # 1. Pipeline Counts (via LIGHTWEIGHT get_count)
    counts = {
        "New": db.get_count("leads", {"status": "eq.New"}),
        "Audited": db.get_count("leads", {"status": "ilike.*audit*"}),
        "Demo Ready": db.get_count("leads", {"status": "eq.Demo Ready"}),
        "Outreach Sent": db.get_count("leads", {"status": "eq.Demo Sent"})
    }
    
    # 2. Local File Counts
    reports_folder = "diamond_reports"
    files = os.listdir(reports_folder) if os.path.exists(reports_folder) else []
    
    print(json.dumps({
        "database_counts": counts,
        "local_report_files": len(files)
    }, indent=2))

if __name__ == "__main__":
    final_check()
