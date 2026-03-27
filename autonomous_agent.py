import time
import os
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv
from database import db
from silas_inbound import poll_silas_inbound
from venom_high_ticket import run_high_ticket_wave
from venom_warm import run_warm_wave
from audit_outreach import run_audit_wave
from audit_refill import run_refill_burst
from silas_accounts import get_daily_status, print_daily_status

load_dotenv()

# Configuration
POLL_INTERVAL_INBOUND = 300  # 5 minutes
STRIKE_INTERVAL_WAVES = 3600 # 1 hour
REFILL_INTERVAL = 7200       # 2 hours
HEARTBEAT_INTERVAL = 60      # 1 minute

class RI2CHOrchestrator:
    def __init__(self):
        self.last_inbound_check = 0.0
        self.last_strike_wave = 0.0
        self.last_refill = 0.0
        self.last_heartbeat = 0.0
        self.is_running = True
        
    def signal_handler(self, sig, frame):
        print("\n[!] Shutdown signal received. Gracefully stopping RI2CH Orchestrator...")
        self.is_running = False
        sys.exit(0)

    def run(self):
        print("=======================================================")
        print("   RI2CH AUTONOMOUS ORCHESTRATOR V1.2 (LIVE) - STARTING")
        print("=======================================================")
        db.push_log("Orchestrator", "RI2CH Autonomous Agency OS Initialized. Full-Spectrum Mode ACTIVE.")
        
        while self.is_running:
            now = time.time()
            dt_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 1. Inbound Heartbeat (Replies)
            if now - self.last_inbound_check >= POLL_INTERVAL_INBOUND:
                print(f"[{dt_str}] Heartbeat: Checking Inbound Intelligence...")
                try:
                    poll_silas_inbound()
                except Exception as e:
                    print(f"[Inbound Error] {e}")
                    db.push_log("Orchestrator", f"Inbound poll failed: {e}")
                self.last_inbound_check = now
            
            # 2. Strike Orchestration (Sends)
            if now - self.last_strike_wave >= STRIKE_INTERVAL_WAVES:
                print(f"[{dt_str}] Heartbeat: Orchestrating Strike Waves...")
                
                status = get_daily_status()
                if status.get("total_remaining", 0) > 0:
                    try:
                        # Vector 1: Whale Wave ($1,500 Offer)
                        print(f"Executing Hourly Whale Mini-Wave (3)...")
                        run_high_ticket_wave(limit=3, dry_run=False)
                        
                        # Vector 2: Warm Wave ($47 Offer)
                        print("Executing Hourly Warm Mini-Wave (5)...")
                        run_warm_wave(limit=5, dry_run=False)
                        
                        # Vector  Vector 3: Audited Strike ($47 Audit Results)
                        print("Executing Hourly Audited Strike Wave (3)...")
                        run_audit_wave(limit=3, dry_run=False)
                        
                    except Exception as e:
                        print(f"Strike Error: {e}")
                        db.push_log("Orchestrator", f"Strike orchestration error: {e}")
                else:
                    print(f"[{dt_str}] Daily limit reached. Strike wave skipped.")
                
                self.last_strike_wave = now
                print_daily_status()

            # 3. Pipeline Refill (Audit Automation)
            if now - self.last_refill >= REFILL_INTERVAL:
                print(f"[{dt_str}] Heartbeat: Refilling Audit Pipeline...")
                try:
                    run_refill_burst(limit=5)
                except Exception as e:
                    print(f"Refill Error: {e}")
                self.last_refill = now
            
            # 4. System Health Pulse
            if now - self.last_heartbeat >= HEARTBEAT_INTERVAL:
                lead_count = db.get_count("leads")
                print(f"[{dt_str}] System Pulse: Online. Tracking {lead_count} Leads.")
                self.last_heartbeat = now
            
            time.sleep(1)

if __name__ == "__main__":
    orchestrator = RI2CHOrchestrator()
    signal.signal(signal.SIGINT, orchestrator.signal_handler)
    orchestrator.run()
