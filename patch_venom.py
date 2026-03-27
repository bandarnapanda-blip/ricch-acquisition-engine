with open("c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\venom_outreach.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("leads = db.fetch_leads({\"status\": \"eq.Shadow Site Ready\"})", 
                    "leads = db.fetch_leads({\"status\": \"eq.Shadow Site Ready\", \"limit\": \"20\"})")

with open("c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\venom_outreach.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Patched venom_outreach.py with limit=20 to prevent ConnectionResetError.")
