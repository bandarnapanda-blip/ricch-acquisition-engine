import subprocess
import time
import os
from datetime import datetime

def run_command(command, name):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Launching {name}...")
    try:
        # Use py for Windows execution
        process = subprocess.Popen(["py"] + command, creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        return process
    except Exception as e:
        print(f"[{name}] Failed to launch: {e}")
        return None

def main():
    print("=== RI2CH OVERNIGHT AUTOPILOT INITIALIZED ===")
    print("Cycle: Scrape -> Submit -> Sync -> Sleep")
    
    while True:
        print(f"\n--- CYCLE START @ {datetime.now().strftime('%H:%M:%S')} ---")
        
        # 1. Scrape (Industrial Hunt)
        # We run it with a limit per query to keep cycles moving
        print("Scraping New Leads...")
        subprocess.run(["py", "find_leads.py", "--limit", "15"])
        
        # 2. Submit (Outreach - Contact Form)
        print("Processing Contact Form Outreach...")
        subprocess.run(["py", "auto_submit.py"])
        
        # 3. Blast (Outreach - Direct Email)
        print("Processing Direct Email Blast...")
        subprocess.run(["py", "email_blast.py", "--limit", "25"])
        
        # 4. Sync (Inbox & Logs)
        print("Syncing Inbox Activity...")
        subprocess.run(["py", "inbox_monitor.py"])
        
        wait_time = 1800 # 30 minutes
        print(f"--- CYCLE COMPLETE. Resting for {wait_time/60} mins... ---")
        time.sleep(wait_time)

if __name__ == "__main__":
    main()
