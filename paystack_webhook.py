import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

# Template Path
TEMPLATE_PATH = os.path.join(os.getcwd(), 'templates', 'onboarding.html')

# Config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SUCCESS_BANNER_URL = "https://tmujezpueegutjlfzipw.supabase.co/storage/v1/object/public/brand/ri2ch_ai_success_banner_1773322386521.png"

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

def send_onboarding_email(email, business_name):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return False
        
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = email
    msg['Subject'] = f"Success! Welcome to Ri2ch Digital, {business_name}"
    
    body = f"""
    Hello {business_name},
    
    Congratulations! Your payment of GHS 7,500 has been successfully processed. 
    
    We are officially starting the transfer of your high-converting website prototype. We have marked your business as a 'VIP Partner'.
    
    Welcome aboard!
    
    Access your onboarding dashboard here: http://localhost:5000/onboarding?email={email}
    
    Best,
    The Ri2ch Digital Team
    """
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending onboarding email: {e}")
        return False

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "online",
        "service": "Ri2ch Digital Paystack Webhook & Onboarding Server",
        "port": 5000,
        "endpoints": ["/paystack-webhook", "/onboarding"]
    })

@app.route('/paystack-webhook', methods=['POST'])
def paystack_webhook():
    # Paystack sends a POST request with the transaction data
    data = request.json
    
    if data and data.get('event') == 'charge.success':
        customer_email = data['data']['customer']['email']
        amount_paid = data['data']['amount'] / 100 # Convert from kobo/pesewas
        
        print(f"💰 PAYMENT RECEIVED: {customer_email} paid {amount_paid}")
        
        # 1. Find lead in Supabase by email
        endpoint = f"{SUPABASE_URL}/rest/v1/leads?email=eq.{customer_email}"
        response = requests.get(endpoint, headers=get_headers())
        
        if response.status_code == 200 and response.json():
            lead = response.json()[0]
            lead_id = lead['id']
            business_name = lead.get('website', 'Partner').split('.')[0].capitalize()
            
            # 2. Update status and revenue
            update_endpoint = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}"
            requests.patch(update_endpoint, headers=get_headers(), json={
                "status": "Closed - Paid",
                "revenue": amount_paid
            })
            
            # 3. Send automated onboarding email
            send_onboarding_email(customer_email, business_name)
            
@app.route('/onboarding', methods=['GET'])
def onboarding_page():
    email = request.args.get('email', '')
    if not os.path.exists(TEMPLATE_PATH):
        return f"Onboarding template not found at {TEMPLATE_PATH}.", 404
    
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
    
    return render_template_string(html, email=email)

@app.route('/submit-onboarding', methods=['POST'])
def submit_onboarding():
    data = request.form.to_dict()
    print(f"ONBOARDING DATA RECEIVED: {data}")
    
    # 1. Update Supabase with onboarding details
    email = data.get('email')
    if email:
        # Find lead_id by email and update
        endpoint = f"{SUPABASE_URL}/rest/v1/leads?email=eq.{email}"
        response = requests.get(endpoint, headers=get_headers())
        if response.status_code == 200 and response.json():
            lead_id = response.json()[0]['id']
            update_endpoint = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}"
            # For now, let's just update the status to indicate onboarding is done
            requests.patch(update_endpoint, headers=get_headers(), json={
                "status": "Onboarding Complete - Build Starting"
            })
    
    return jsonify({"status": "success", "message": "Details received, we are starting your build!"}), 200

if __name__ == '__main__':
    # Run on port 5000 by default
    app.run(host='0.0.0.0', port=5000)
