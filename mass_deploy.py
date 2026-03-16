from database import db
from config import CITIES, NICHES
import time
import sys

# Set encoding for better compatibility on Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def mass_deploy():
    print("DEPLOY: Initiating Industrial Scale Deployment: The Great Harvest")
    print(f"Targeting {len(NICHES)} niches across {len(CITIES)} cities.")
    
    task_count = 0
    # Prioritize Gold Mine niches as per 2026 intelligence
    priority_niches = ["Luxury Home Remodeling", "Dental Implant Specialists", "Personal Injury Attorneys"]
    
    # Sort niches to put priority ones first
    sorted_niches = sorted(NICHES, key=lambda x: x not in priority_niches)
    
    for niche in sorted_niches:
        is_priority = niche in priority_niches
        label = "[PRIORITY]" if is_priority else "[STANDARD]"
        
        for city in CITIES:
            payload = {"niche": niche, "city": city}
            print(f"  {label} Queuing {niche} in {city}...")
            
            try:
                db.queue_task("scrape", payload)
                db.push_log("MassDeploy", f"Queued {label} {niche} hunt in {city}")
                task_count += 1
            except Exception as e:
                print(f"  [ERROR] Failed to queue {niche} in {city}: {e}")
            
            # Throttle to prevent database connection spikes
            time.sleep(0.1)

    print(f"\nSUCCESS: Deployment Complete! {task_count} missions active.")
    print("Background harvesters are now excavating the digital industrial landscape.")

if __name__ == "__main__":
    mass_deploy()
