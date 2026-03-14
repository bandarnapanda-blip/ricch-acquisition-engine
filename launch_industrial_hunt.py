from database import db
import time

# "Gold Mine" Niches and Elite Cities 2026
CAMPAIGNS = [
    {
        "niche": "Luxury Home Remodeling",
        "cities": ["Beverly Hills", "Palo Alto", "Palm Beach", "Austin", "Greenwich"]
    },
    {
        "niche": "Dental Implant Specialists",
        "cities": ["Scottsdale", "San Diego", "Newport Beach", "Seattle", "Boston"]
    },
    {
        "niche": "Personal Injury Attorneys",
        "cities": ["Dallas", "Houston", "Atlanta", "Miami", "Chicago"]
    }
]

def launch_hunt():
    print("[Antigravity Industrial Hunt] Initializing...")
    total_queued = 0
    
    for camp in CAMPAIGNS:
        niche = camp["niche"]
        for city in camp["cities"]:
            print(f"Queuing: {niche} in {city}...")
            # Use the db.queue_task helper
            res = db.queue_task(
                task_type="scrape",
                payload={
                    "niche": niche,
                    "city": city,
                    "industrial": True, # Flag for worker to go deeper
                    "tier": "A"
                }
            )
            if res:
                total_queued += 1
            else:
                print(f"FAILED to queue {niche} in {city}")
            time.sleep(0.5)

    print(f"\nSUCCESS: {total_queued} industrial missions launched into orbit.")
    db.push_log("System/Commander", f"Launched Massive Industrial Hunt: {total_queued} campaigns active.")

if __name__ == "__main__":
    launch_hunt()
