from pyngrok import ngrok, conf
import os
from dotenv import load_dotenv

load_dotenv()

# Point to local ngrok binary
conf.get_default().ngrok_path = "./ngrok.exe"

print("Starting Public Bridge (ngrok) to Port 5000...")
try:
    # Open a HTTP tunnel on port 5000
    public_url = ngrok.connect(5000).public_url
    print("\n============================================================")
    print(f"  YOUR PUBLIC WEBHOOK URL: {public_url}/paystack-webhook")
    print(f"  ONBOARDING PAGE URL: {public_url}/onboarding")
    print("============================================================\n")
    print("Keep this script running while the Success Bot is active!")
    
    # Keep it running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Closing tunnel...")
    ngrok.kill()
