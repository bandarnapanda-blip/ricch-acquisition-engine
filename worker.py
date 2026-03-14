import time
import asyncio
from database import db
import tasks

def process_task(task):
    task_id = task['id']
    task_type = task['task_type']
    payload = task.get('payload', {})
    
    db.update_task_status(task_id, "processing")
    db.push_log("Worker", f"Processing task {task_id}: {task_type}")
    
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
            db.update_task_status(task_id, "completed")
            db.push_log("Worker", f"Task {task_id} completed successfully.")
        else:
            db.update_task_status(task_id, "failed", error=result.get('message') or result.get('error'))
            db.push_log("Worker", f"Task {task_id} failed: {result.get('message') or result.get('error')}")

    except Exception as e:
        db.update_task_status(task_id, "failed", error=str(e))
        db.push_log("Worker", f"CRITICAL ERROR processing task {task_id}: {e}")

def main():
    db.push_log("Worker", "Antigravity Worker Engine Online. Listening for tasks...")
    print("Antigravity Worker Engine Online. Listening for tasks...")
    
    while True:
        try:
            pending_tasks = db.fetch_pending_tasks(limit=5)
            if not pending_tasks:
                time.sleep(10) # Wait for new tasks
                continue
                
            for task in pending_tasks:
                process_task(task)
                time.sleep(2) # Small break between tasks to avoid rate limits
                
        except Exception as e:
            print(f"Worker Loop Error: {e}")
            time.sleep(30) # Backoff on major DB error

if __name__ == "__main__":
    main()
