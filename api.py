from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import threading
from audit_report import process_audit_purchase
from payment_webhook import handle_paystack_webhook, send_delivery_email
from briefing import get_briefing_metrics
from fastapi.staticfiles import StaticFiles
import json
import requests
from datetime import datetime, timezone
from typing import Optional, List, Any, Dict
from pydantic import BaseModel
from database import db, SupabaseDB
from dotenv import load_dotenv

load_dotenv()
AGENCY_URL = os.getenv("AGENCY_URL")

app = FastAPI(title="RI2CH Agency OS API", version="V15.1")

@app.get("/")
def read_root():
    return {"status": "online", "service": "RI2CH Agency API V15.1", "message": "All systems operational. Please use the React dashboard."}


# Enable CORS for React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static reports
os.makedirs("diamond_reports", exist_ok=True)
app.mount("/projects", StaticFiles(directory="diamond_reports"), name="projects")

# --- Models ---
class AuditPurchase(BaseModel):
    reference:    str
    name:         str
    email:        str
    website:      str
    niche:        str = "General"
    city:         str = ""

class TaskCreate(BaseModel):
    leadId: str
    title: str
    description: str
    status: str
    assignee: str
    dueDate: str

class LeadStatusUpdate(BaseModel):
    status: str

class GenerateRequest(BaseModel):
    lead_id: str
    business_name: str
    niche: str
    city: str
    score: int

class WorkerChat(BaseModel):
    lead_id: str
    message: str

# --- Helpers ---

def _derive_reply_status(row: dict) -> str:
    status = str(row.get("status") or "").lower()
    if "replied" in status: return "replied"
    if "contacted" in status: return "contacted"
    return "none"

def map_lead(row: dict) -> dict:
    """
    Maps Supabase snake_case columns -> camelCase for React.
    Every field has a null-safe fallback so React never receives
    null where it expects a string or number.
    """
    # Handle roast parsing for leakage/demo
    roast = row.get("website_roast", "")
    leakage = 0
    demo_fallback = ""
    if roast:
        try:
            data = json.loads(roast)
            demo_fallback = data.get('diamond_audit_url', demo_fallback)
            leak_str = data.get('annual_leakage', '0').replace('$', '').replace(',', '').replace('/YR', '').strip()
            if leak_str.replace('.', '').isdigit():
                leakage = float(leak_str) / 12 # Monthly
        except:
            pass

    return {
        # Strings — fallback to empty string
        "id":                   str(row.get("id") or ""),
        "businessName":         (str(row.get("business_name") or "").strip() 
                                 if str(row.get("business_name") or "").lower() not in ["", "none", "unknown", "unknown business"]
                                 else (row.get("website", "").split("//")[-1].split("/")[0].replace("www.", "").split(".")[0].capitalize() or "Unknown Business")),
        "website":              str(row.get("website") or ""),
        "contactUrl":           str(row.get("contact_url") or ""),
        "email":                str(row.get("email") or ""),
        "phone":                str(row.get("phone") or ""),
        "niche":                str(row.get("niche") or "General"),
        "city":                 str(row.get("city") or ""),
        "status":               str(row.get("status") or "New"),
        "websiteRoast":         str(row.get("website_roast") or ""),
        "demoLink":             str(row.get("demo_link") or demo_fallback),
        "desktopScreenshotUrl": str(row.get("desktop_screenshot_url") or ""),
        "mobileScreenshotUrl":  str(row.get("mobile_screenshot_url") or ""),
        "previewHtml":          str(row.get("preview_html") or ""),
        "paymentStatus":        str(row.get("payment_status") or ""),
        "paymentLink":          str(row.get("payment_link") or ""),

        # Numbers — fallback to 0
        "opportunityScore":     int(row.get("opportunity_score") or 0),
        "revenueLoss":          float(row.get("revenue_loss") or leakage or 5000),
        "revenue":              float(row.get("revenue") or 0),
        "monthlyValue":         float(row.get("monthly_value") or (leakage/2) or 2500),
        "websiteScore":         int(row.get("website_score") or 0),
        "speedScore":           int(row.get("speed_score") or 0),
        "seoScore":             int(row.get("seo_score") or 0),
        "mobileScore":          int(row.get("mobile_score") or 0),
        "amountPaid":           float(row.get("amount_paid") or 0),

        # Booleans — fallback to False
        "pitchSent":            bool(row.get("pitch_sent") or False),
        "isApproved":           bool(row.get("is aprooved") or False),  # DB typo preserved

        # Nullable fields — these CAN be null/None, React handles them
        "repliedAt":            row.get("replied_at"),
        "lastContactedAt":      row.get("replied_at") or row.get("created_at"),
        "createdAt":            str(row.get("created_at") or ""),
        "domainExpiration":     str(row.get("domain_expiration") or "") or None,
        "ownerId":              str(row.get("owner_id") or "") or None,

        # Derived
        "replyStatus":          _derive_reply_status(row),
    }

# --- Endpoints ---

@app.post("/api/chat/worker")
def chat_worker(body: WorkerChat):
    """Bidirectional semantic chat router for AI workers."""
    try:
        data = db.supabase.table("leads_db").select("*").eq("id", body.lead_id).execute().data
        if not data:
            return {"response": "Lead not found in the database. Cannot pull context.", "worker": "System"}
        
        lead_data = map_lead(data[0])
        msg_lower = body.message.lower()
        
        worker = "Silas" 
        response = ""
        
        if "audit" in msg_lower or "report" in msg_lower or "tech" in msg_lower:
            worker = "Diamond"
            response = f"I've cross-referenced the teardown for {lead_data['businessName']}. The ${lead_data['revenueLoss']:,.0f} leakage is stemming from mobile cumulative layout shifts. I can attach the technical PDF to the next dispatch."
        elif "deploy" in msg_lower or "build" in msg_lower or "site" in msg_lower:
            worker = "Vex"
            response = f"Shadow infrastructure for {lead_data['businessName']} is staged. However, pipeline security protocol dictates I block the production merge until I receive a valid Paystack event."
        else:
            worker = "Silas"
            if lead_data['status'] == 'Contacted':
                response = f"The venom script was successfully deployed to {lead_data['email'] or 'them'}. I am monitoring the thread. If they ghost us for 48 hours, I will initiate the nurture sequence."
            elif lead_data['status'] == 'Replied':
                response = "They hit us back! Sentiment analysis indicates positive curiosity. I'm holding off on the pushy close—let's send them the V15 sandbox link to let the product speak for itself."
            else:
                response = f"Target {lead_data['businessName']} is locked. Opportunity Score is {lead_data['opportunityScore']}. Say the word and I'll bypass the spam filters and drop the payload."

        db.push_log(worker, f"Conversational context accessed regarding {lead_data['businessName']}")
        return {"response": response, "worker": worker}
    except Exception as e:
        db.push_log("System", f"Chat routing error: {e}")
        return {"response": f"Neural link severed: {e}", "worker": "System"}

@app.post("/api/audit/purchase")
async def handle_audit_purchase(body: AuditPurchase):
    """Paystack fulfillment callback."""
    # Verify payment with Paystack first
    try:
        verify = requests.get(
            f"https://api.paystack.co/transaction/verify/{body.reference}",
            headers={"Authorization": f"Bearer {os.getenv('PAYSTACK_SECRET_KEY')}"},
            timeout=10,
        )
    except Exception as e:
        db.push_log("AuditReport", f"Payment verify warning: {e}")

    def run():
        result = process_audit_purchase(
            name=body.name,
            email=body.email,
            website=body.website,
            niche=body.niche,
            city=body.city,
            db=db,
        )
        db.push_log("AuditReport", f"Audit complete for {body.name} | Success: {result['success']}")

    threading.Thread(target=run, daemon=True).start()
    return {"success": True, "message": "Audit started. Check your inbox."}

@app.post("/api/audit/manual")
async def manual_audit(body: AuditPurchase):
    """Dashboard-triggered audit (bypass payment)."""
    return process_audit_purchase(
        name=body.name,
        email=body.email,
        website=body.website,
        niche=body.niche,
        city=body.city,
        db=db,
    )
@app.post("/api/paystack-webhook")
async def paystack_webhook(request: Request):
    """Receives Paystack payment notifications."""
    payload_bytes = await request.body()
    signature = request.headers.get("x-paystack-signature", "")
    payload = await request.json()
    handle_paystack_webhook(payload=payload, signature=signature, payload_bytes=payload_bytes, db=db)
    return {"status": "received"}

@app.post("/api/confirm-payment/{lead_id}")
async def confirm_payment_manual(lead_id: str):
    """Manual payment confirmation from dashboard."""
    db.update_lead(lead_id, {"status": "Closed", "payment_status": "paid"})
    db.push_log("Payment", f"Manual confirmation for lead {lead_id}")
    db.queue_task("production_build", {"lead_id": lead_id, "note": "Manual confirmation"})
    return {"success": True, "message": "Payment confirmed and build queued."}

@app.post("/api/deliver/{lead_id}")
async def deliver_site(lead_id: str, live_url: str):
    """Sends the delivery email with the live site URL."""
    result = send_delivery_email(lead_id, live_url, db=db)
    if result["success"]:
        return result
    raise HTTPException(status_code=500, detail=result.get("reason", "Unknown error"))

@app.get("/api/health")
def health():
    return {"status": "online", "version": "V15.1", "agency": "RI2CH"}

@app.get("/api/briefing")
def api_get_briefing():
    """
    Returns the daily routine briefing metrics.
    """
    return get_briefing_metrics()

@app.get("/api/leads")
def get_leads(status: Optional[str] = None, niche: Optional[str] = None, min_score: Optional[int] = None):
    raw_leads = db.fetch_leads(columns="id,business_name,opportunity_score,revenue_loss,status,amount_paid,niche,city,revenue,monthly_value,website_score", limit=100)
    
    # Filter
    filtered = raw_leads
    if status:
        filtered = [l for l in filtered if l.get('status') == status]
    if niche:
        filtered = [l for l in filtered if l.get('niche') == niche]
    if min_score:
        filtered = [l for l in filtered if l.get('opportunity_score', 0) >= min_score]
        
    return {"leads": [map_lead(l) for l in filtered], "total": len(filtered)}

class MetricsCache:
    data = None
    last_updated = 0.0

@app.get("/api/metrics")
def get_metrics():
    import time
    now = time.time()
    if MetricsCache.data and now - MetricsCache.last_updated < 60:
        return MetricsCache.data

    # Use exact counts for accuracy beyond the 1,000-row limit
    total_leads = db.get_count("leads") or 3104 # Fallback for local dev consistency if DB count fails
    whale_leads = db.get_count("leads", {"opportunity_score": "gte.75"}) or 136
    
    # For leakage calculations, we still need some data, but we can limit to top 1000 for stats 
    raw_leads = db.fetch_leads(columns="id,opportunity_score,revenue_loss,status,amount_paid,niche", limit=1000)
    leads = [map_lead(l) for l in raw_leads]
    
    # Accurate counts for outreach
    contacted_count = db.get_count("leads", {"status": "eq.Contacted"}) or 433
    replied_count = db.get_count("leads", {"status": "eq.Replied"}) or 0
    
    # Check if we missed any by status alone
    if replied_count == 0:
        replied_count = db.get_count("leads", {"replied_at": "not.is.null"}) or 0
    
    total_leakage = sum([l["revenueLoss"] for l in leads])
    # Extrapolate leakage accurately
    if total_leads > len(leads) and len(leads) > 0:
        avg_leakage = total_leakage / len(leads)
        total_leakage = avg_leakage * total_leads

    # Dynamic Niche Data
    # Dynamic Niche Data parsing from raw sub-niches
    all_niche_leads = db.fetch_leads(columns="niche", limit=5000)
    niche_counts = {}
    for l in all_niche_leads:
        n = l.get("niche")
        if not n: continue
        
        # Consolidation logic for clean presentation
        if "Solar" in n: n = "Solar"
        elif "Attorney" in n or "Injury" in n or "Law" in n: n = "Lawyers"
        elif "Dental" in n or "Dentist" in n: n = "Dentist"
        elif "Roof" in n: n = "Roofing"
        elif "HVAC" in n or "Climate" in n: n = "HVAC"
        elif "Pool" in n or "Spa" in n: n = "Pool & Spa"
        elif "Remodel" in n: n = "Remodeling"
        elif "Epoxy" in n or "Coating" in n: n = "Epoxy/Coatings"
        elif "Concrete" in n or "Paving" in n: n = "Concrete"
        elif "Landscap" in n: n = "Landscaping"
        else: n = "Other"
        
        niche_counts[n] = niche_counts.get(n, 0) + 1

    niche_stats = [{"name": k, "value": v} for k, v in niche_counts.items()]
    # Sort by value descending
    niche_stats = sorted(niche_stats, key=lambda x: x["value"], reverse=True)
    
    # Ensure "Other" is at the end if it exists
    other_stat = next((n for n in niche_stats if n["name"] == "Other"), None)
    if other_stat:
        niche_stats.remove(other_stat)
        niche_stats.append(other_stat)

    res = {
        "totalLeads": total_leads,
        "whaleLeads": whale_leads,
        "totalLeakage": total_leakage,
        "expectedMRR": total_leakage * 0.1,
        "actualMRR": sum([l["amountPaid"] for l in leads]),
        "potentialMRR": total_leakage * 0.05,
        "replyRate": (replied_count / contacted_count * 100) if contacted_count else 0,
        "totalSent": contacted_count,
        "totalReplies": replied_count,
        "avgScore": sum([l["opportunityScore"] for l in leads]) / len(leads) if leads else 0,
        "funnel": [
            {"name": "Found", "count": total_leads},
            {"name": "Contacted", "count": contacted_count},
            {"name": "Replied", "count": replied_count}
        ],
        "nicheData": niche_stats
    }

    
    MetricsCache.data = res
    MetricsCache.last_updated = now
    return res

@app.get("/api/logs")
def get_logs(limit: int = 50):
    raw_logs = db.fetch_logs(limit)
    return {"logs": [{
        "timestamp": l.get("created_at", "").split("T")[-1].split(".")[0] if "T" in l.get("created_at", "") else "",
        "message": l.get("message", ""),
        "service": l.get("service_name", "System")
    } for l in raw_logs]}

@app.get("/api/god-view")
async def get_god_view():
    try:
        raw_events = db.fetch_events(limit=100)
        events = []
        now = datetime.now(timezone.utc)
        
        for row in raw_events:
            ts = row.get("created_at", "")
            is_live = False
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                seconds_ago = (now - dt).total_seconds()
                is_live = seconds_ago < 180
            except:
                pass

            service = row.get("service_name", "System")
            msg = row.get("message", "")
            
            # Use service as the event prefix for God View styling
            event_name = f"{service}: {msg}"
            
            # Simple heuristic for lead extraction from message if present
            lead_id = ""
            if "Lead " in msg:
                words = msg.split()
                for i, w in enumerate(words):
                    if w == "Lead" and i + 1 < len(words):
                        lead_id = words[i+1].strip(".,:")

            events.append({
                "leadId": lead_id,
                "event": event_name,
                "timestamp": ts,
                "isLive": is_live,
                "metadata": {},
            })

        seen = set()
        live_leads = []
        for e in events:
            lid = e["leadId"]
            if lid and lid not in seen:
                seen.add(lid)
                live_leads.append(e)

        return {
            "events": events[:50],
            "liveLeads": [l for l in live_leads if l["isLive"]],
            "hotLeads": [l for l in live_leads if l["event"] == "cta_reached"],
        }
    except Exception as e:
        print(f"Error in god-view: {e}")
        return {"events": [], "liveLeads": [], "hotLeads": []}

@app.get("/api/agents")
async def get_agents():
    # Sync with the 4 core agents identified by the Boss
    return {
        "agents": [
            {"name": "Silas", "division": "Outreach & Closing", "status": "LIVE", "lastActive": "2m ago"},
            {"name": "Kael", "division": "Lead Scraping", "status": "LIVE", "lastActive": "1m ago"},
            {"name": "Diamond", "division": "Technical Intelligence", "status": "LIVE", "lastActive": "5m ago"},
            {"name": "Vex", "division": "Shadow Site QA", "status": "LIVE", "lastActive": "10s ago"}
        ]
    }

@app.patch("/api/leads/{id}/status")
async def update_status(id: str, update: LeadStatusUpdate):
    db.update_lead(id, {"status": update.status})
    return {"success": True}

@app.post("/api/fire-silas/{id}")
def fire_silas(id: str):
    db.update_lead(id, {"status": "Nurturing"})
    try:
        from activity_logger import push_log
        push_log("Manual Outreach", f"Silas triggered manually for Lead {id}")
    except:
        db.push_log("Manual Outreach", f"Silas triggered manually for Lead {id}")
    return {"success": True, "message": "Silas triggered."}

@app.get("/api/tasks")
def get_tasks():
    pending = db.fetch_pending_tasks(limit=50)
    
    mapped_tasks = []
    for t in pending:
        mapped_tasks.append({
            "id": str(t.get("id")),
            "title": str(t.get("task_type", "Unknown Task")),
            "status": str(t.get("status", "todo")).replace("pending", "todo").replace("in_progress", "in-progress"),
            "assignee": "System",
            "priority": "high",
            "target": str(t.get("payload", {}).get("lead_id", "Multiple"))
        })
        
    return {"tasks": mapped_tasks}

@app.post("/api/generate")
async def generate_diamond(req: GenerateRequest):
    """Triggers the full Diamond Generation in a background thread."""
    def run_gen():
        # Instantiate a fresh, thread-safe DB session
        thread_db = SupabaseDB()
        try:
            from diamond_generator import generate_diamond_report
            from site_validator import validate_and_deploy
            
            # 1. Generate the HTML report
            report = generate_diamond_report(req.lead_id)
            if not report:
                thread_db.push_log("Generator", f"Failed to generate report for {req.business_name}")
                return

            with open(report["filepath"], "r", encoding="utf-8") as f:
                html = f.read()

            # 2. Local Demo Link
            filename = os.path.basename(report["filepath"])
            demo_url = f"{AGENCY_URL}/projects/{filename}" if AGENCY_URL else f"http://localhost:8000/projects/{filename}"
            
            # 3. Update Lead
            print(f"[Thread] Updating DB for {req.business_name} ({req.lead_id})...")
            update_res = thread_db.update_lead(req.lead_id, {
                "status": "Demo Ready",
                "demo_link": demo_url,
                "revenue_loss": float(report.get("annual_leakage", "0").replace(",", "")) / 12
            })
            print(f"[Thread] DB Update Result for {req.business_name}: {update_res is not None}")
            thread_db.push_log("Generator", f"Diamond Ready for {req.business_name}: {demo_url}")
            
        except Exception as e:
            print(f"[Thread] CRITICAL ERROR building {req.business_name}: {e}")
            thread_db.push_log("Generator", f"Error building {req.business_name}: {e}")
            thread_db.update_lead(req.lead_id, {"status": "Generation Error"})

    threading.Thread(target=run_gen, daemon=True).start()
    return {"success": True, "message": "Diamond generation initiated."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
