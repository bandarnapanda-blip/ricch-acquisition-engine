import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()

USER = os.getenv("SMTP_ACCOUNT_1_USER")
PASS = os.getenv("SMTP_ACCOUNT_1_PASS")
HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
PORT = 465 # Testing SSL direct

print(f"Testing SSL connection to {HOST}:{PORT} for {USER}...")

try:
    with smtplib.SMTP_SSL(HOST, PORT, timeout=15) as s:
        print("Connected SSL. EHLO...")
        s.ehlo()
        print(f"Logging in as {USER}...")
        s.login(USER, PASS)
        print("LOGIN SUCCESS!")
        
except Exception as e:
    print(f"FAILED: {e}")
