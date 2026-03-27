import re

# Patch API
with open("c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\api.py", "r", encoding="utf-8") as f:
    api_code = f.read()

root_get = """
@app.get("/")
def read_root():
    return {"status": "online", "service": "RI2CH Agency API V15.1", "message": "All systems operational. Please use the React dashboard."}
"""

if "def read_root():" not in api_code:
    api_code = api_code.replace('app = FastAPI(title="RI2CH Agency OS API", version="V15.1")', 
                                'app = FastAPI(title="RI2CH Agency OS API", version="V15.1")\n' + root_get)
    with open("c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\api.py", "w", encoding="utf-8") as f:
        f.write(api_code)

# Patch webhook handler
with open("c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\webhook_handler.py", "r", encoding="utf-8") as f:
    webhook_code = f.read()

webhook_root = """
@app.route("/", methods=["GET"])
def index():
    return '{"status": "online", "service": "RI2CH Webhook Handler", "message": "Listening for Paystack events."}', 200, {'Content-Type': 'application/json'}
"""

if 'def index():' not in webhook_code:
    webhook_code = webhook_code.replace("app = Flask(__name__)", "app = Flask(__name__)\n" + webhook_root)
    with open("c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\webhook_handler.py", "w", encoding="utf-8") as f:
        f.write(webhook_code)

print("Patched API and Webhook root endpoints.")
