import time
import asyncio
from database import db
import tasks
import socket

# Unique identifier for this worker instance
WORKER_ID = f"worker-{socket.gethostname()}-{os.getpid()}" if hasattr(os, 'getpid') else f"worker-{socket.gethostname()}"

def process_task(task):
    task_id = task['id']
    task_type = task['task_type']
    payload = task.get('payload', {})
    
    db.push_log("Worker", f"Starting processing for task {task_id}: {task_type}")
    
    try:
        result = None
        if task_type == "scrape":
            niche = payload.get('niche', 'Roofing')
            city = payload.get('city', 'Dallas')
            result = tasks.task_scrape_leads(niche, city)
            
        elif task_type == "audit":
            lead_id = payload.get('lead_id')
            if lead_id:
                result = tasks.task_audit_lead(lead_id)
            else:
                result = {"status": "error", "message": "Missing lead_id"}
                
        elif task_type == "redesign":
            lead_id = payload.get('lead_id')
            if lead_id:
                result = tasks.task_generate_redesign(lead_id)
            else:
                result = {"status": "error", "message": "Missing lead_id"}
                
        elif task_type == "outreach":
            lead_id = payload.get('lead_id')
            if lead_id:
                # Run the async outreach task in the event loop
                result = asyncio.run(tasks.task_send_outreach(lead_id))
            else:
                result = {"status": "error", "message": "Missing lead_id"}
        
        else:
            result = {"status": "error", "message": f"Unknown task type: {task_type}"}

        if result and result.get('status') == "success":
            db.mark_task_done(task_id)
            db.push_log("Worker", f"Task {task_id} marked as DONE.")
        else:
            err = result.get('message') or result.get('error') or "Unknown failure"
            db.mark_task_failed(task_id, err)
            db.push_log("Worker", f"Task {task_id} FAILED: {err}")

    except Exception as e:
        db.mark_task_failed(task_id, str(e))
        db.push_log("Worker", f"CRITICAL ERROR processing task {task_id}: {e}")

def main():
    db.push_log("Worker", f"Antigravity Worker Engine Online [{WORKER_ID}]. Listening for tasks...")
    print(f"Antigravity Worker Engine Online [{WORKER_ID}]. Listening for tasks...")
    
    while True:
        try:
            # Atomic claim: Only this worker gets this specific task
            task = db.claim_task(WORKER_ID)
            
            if not task:
                time.sleep(10) # Wait for new tasks
                continue
                
            process_task(task)
            time.sleep(2) # Small break between tasks to avoid rate limits
                
        except Exception as e:
            print(f"Worker Loop Error: {e}")
            time.sleep(30) # Backoff on major DB error

if __name__ == "__main__":
    import os # Needed for getpid fallback
    main()
