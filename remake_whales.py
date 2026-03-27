import os
import subprocess
import time
import sys
from database import db

def remake_leads(limit=200, start_offset=0, min_score=51, max_score=74):
    print(f"--- VEX MASS PRODUCTION: WARM LEADS (Score {min_score}-{max_score}) ---")
    
    # HYPER-STABLE SYNC: Fetch IDs first to avoid timeouts on 3102 leads
    url = f"{db.url}/rest/v1/leads?opportunity_score=gte.{min_score}&opportunity_score=lte.{max_score}&select=id"
    res = db._session.get(url, headers=db.headers).json()
    if not isinstance(res, list):
        print(f"Error fetching IDs: {res}")
        return
        
    target_ids = [r['id'] for r in res if 'id' in r]
    print(f"--- TARGETING {min(limit, len(target_ids))} LEADS IN BATCH ---")
    print("---------------------------------------------------------")
    
    success_count = 0
    fail_count = 0
    
    # Slice for the current wave
    batch_ids = target_ids[start_offset:start_offset + limit]

    for i, lid in enumerate(batch_ids):
        progress = f"[{i+1+start_offset}/{len(target_ids)}]"
        
        # Individual fetch to prevent Supabase Read Timeouts
        lead_url = f"{db.url}/rest/v1/leads?id=eq.{lid}&select=*"
        lead_res = db._session.get(lead_url, headers=db.headers).json()
        if not lead_res or not isinstance(lead_res, list):
            print(f"{progress} [ERROR] Could not fetch lead data for {lid}")
            continue
            
        lead = lead_res[0]
        name = lead.get('business_name') or "Valued Client"
        niche = lead.get('niche') or "General Services"
        city = lead.get('city') or "Your City"
        score = lead.get('opportunity_score', 0)
        
        print(f"\n{progress} Remaking: {name} ({city})")
        print(f"       Score: {score} | Lead ID: {lid}")
        
        # Run generate_landing.py
        cmd = [
            "py", "generate_landing.py",
            name,
            niche,
            city,
            str(lid),
            "None", # auto-slug
            str(score)
        ]
        
        start_time = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            elapsed = time.time() - start_time
            if result.returncode == 0:
                success_count += 1
                status_msg = "[SUCCESS]"
                if "Verified Live" in result.stdout or "Shadow Site Live" in result.stdout:
                    status_msg += " [VEX: VERIFIED LIVE]"
                print(f"       {status_msg} ({elapsed:.1f}s)")
            else:
                fail_count += 1
                print(f"       [ERROR] Generation failed (Code {result.returncode})")
                print(f"       Trace: {result.stderr[:200]}...")
        except subprocess.TimeoutExpired:
            fail_count += 1
            print(f"       [TIMEOUT] Vex taking too long, skipping to next lead.")
        except Exception as e:
            fail_count += 1
            print(f"       [FATAL] {str(e)}")

        print("       " + "-"*30)

    print("\n" + "="*50)
    print(f" WAVE SUMMARY: {success_count} Successes | {fail_count} Failures")
    print(f" Next Wave recommended offset: {start_offset + limit}")
    print("="*50)

if __name__ == "__main__":
    # Warm Leads: 186 leads (Score 51-74)
    remake_leads(limit=200, start_offset=0, min_score=51, max_score=74)
