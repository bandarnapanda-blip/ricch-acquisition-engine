import os
import time
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
from database import db
from silas_accounts import load_accounts

load_dotenv()

def poll_silas_inbound():
    """Polls all Silas accounts for new replies and updates the leads database."""
    accounts = load_accounts()
    print(f"--- SILAS INBOUND CAPTURE: POLLING {len(accounts)} ACCOUNTS ---")
    
    for acc in accounts:
        user = acc["user"]
        password = acc["password"]
        
        try:
            # Connect to Gmail
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(user, password)
            mail.select("inbox")
            
            # Search for all unseen messages
            status, messages = mail.search(None, 'UNSEEN')
            if status != 'OK':
                print(f" [!] Error searching inbox for {user}")
                continue
                
            msg_ids = messages[0].split()
            if not msg_ids:
                print(f" [-] {user}: No new replies.")
                mail.logout()
                continue
                
            print(f" [+] {user}: {len(msg_ids)} new messages found.")
            
            for m_id in msg_ids:
                status, data = mail.fetch(m_id, '(RFC822)')
                if status != 'OK': continue
                
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Get Sender
                from_ = msg.get("From")
                subject = msg.get("Subject")
                
                # Parse email address
                sender_email = None
                if "<" in from_:
                    sender_email = from_.split("<")[-1].split(">")[0].strip().lower()
                else:
                    sender_email = from_.strip().lower()
                
                if not sender_email: continue
                
                print(f"    - Processing reply from: {sender_email} | Subject: {subject}")
                
                # Match against database
                leads = db.fetch_leads(filters={"email": f"eq.{sender_email}"})
                if not leads:
                    # Try matching by domain if direct match fails
                    domain = sender_email.split("@")[-1]
                    leads = db.fetch_leads(filters={"website": f"ilike.%{domain}%"})
                
                if leads:
                    lead = leads[0]
                    lid = lead.get("id")
                    name = lead.get("business_name") or lead.get("website", "Target")
                    
                    # Update status to Replied
                    db.update_lead(lid, {"status": "Replied", "last_event": "Email Reply Received"})
                    
                    # God View Alert
                    db.push_log("Silas", f"PRIORITY: High-intent reply received from {name} ({sender_email})")
                    print(f"      [MATCH] Updated {name} to 'Replied' status.")
                else:
                    print(f"      [NO MATCH] Sender not found in lead database.")
            
            mail.logout()
            
        except Exception as e:
            print(f" [!] Error polling {user}: {e}")

if __name__ == "__main__":
    while True:
        poll_silas_inbound()
        print("\n--- Waiting 60s for next pulse... ---")
        time.sleep(60)
