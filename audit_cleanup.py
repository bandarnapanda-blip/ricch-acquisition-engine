from database import db
import json

def cleanup():
    print("--- PLACEHOLDER PURGE: DATA INTEGRITY SYNC ---")
    leads = db.fetch_leads()
    if not leads:
        print("No leads found to audit.")
        return
        
    print(f"Auditing {len(leads)} leads for placeholder contamination...")
    
    purged_count = 0
    fixed_count = 0
    
    for l in leads:
        lid = l['id']
        emails = l.get('candidate_emails')
        
        if not emails:
            continue
            
        data_str = json.dumps(emails).lower()
        if 'valued' in data_str or 'vclient' in data_str:
            # Check if we can filter out just the bad ones
            new_emails = [e for e in emails if 'valued' not in e.lower() and 'vclient' not in e.lower()]
            
            if not new_emails:
                # If all were placeholders, clear the the list
                db.update_lead(lid, {"candidate_emails": []})
                purged_count += 1
            else:
                # If some were real (unlikely but safe), update to just those
                db.update_lead(lid, {"candidate_emails": new_emails})
                fixed_count += 1
                
    print(f"DONE. Purged: {purged_count} | Fixed: {fixed_count} leads.")

if __name__ == "__main__":
    cleanup()
