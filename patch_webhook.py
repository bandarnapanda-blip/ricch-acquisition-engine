import re

with open("c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\webhook_handler.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the smtplib snippet with send_warm_email
replacement = """
    from silas_accounts import send_warm_email
    email_success = True
    if email:
        res = send_warm_email(to_email=email, subject=client_subject, body_text=client_body, body_html=None, lead_id=lead_data.get('id'))
        if not res.get("success"): email_success = False
    if KHALIL_EMAIL:
        send_warm_email(to_email=KHALIL_EMAIL, subject=khalil_subject, body_text=khalil_body, body_html=None, lead_id=lead_data.get('id'))
"""

target = """    def send(to, sub, body):
        msg = MIMEMultipart()
        msg['From'] = f"{AGENCY_NAME} <{GMAIL_USER}>"
        msg['To'] = to
        msg['Subject'] = sub
        msg.attach(MIMEText(body, 'plain'))
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")

    # Send both
    if email:
        send(email, client_subject, client_body)
    if KHALIL_EMAIL:
        send(KHALIL_EMAIL, khalil_subject, khalil_body)"""

new_content = content.replace(target, replacement)
with open("c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\webhook_handler.py", "w", encoding="utf-8") as f:
    f.write(new_content)
    
print("Replaced webhook email logic.")
