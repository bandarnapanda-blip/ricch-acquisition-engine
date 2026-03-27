import os
import re

api_path = r'c:\Users\razer\.gemini\antigravity\playground\static-armstrong\api.py'
with open(api_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update /api/leads to have limit=100
old_leads = 'def get_leads(status: Optional[str] = None, niche: Optional[str] = None, min_score: Optional[int] = None):\n    raw_leads = db.fetch_leads(columns="id,business_name,opportunity_score,revenue_loss,status,amount_paid,niche,city,revenue,monthly_value,website_score")'
new_leads = 'def get_leads(status: Optional[str] = None, niche: Optional[str] = None, min_score: Optional[int] = None):\n    raw_leads = db.fetch_leads(columns="id,business_name,opportunity_score,revenue_loss,status,amount_paid,niche,city,revenue,monthly_value,website_score", limit=100)'
code = code.replace(old_leads, new_leads)

# 2. Update /api/metrics to ensure it specifically has no limit
old_metrics = 'def get_metrics():\n    raw_leads = db.fetch_leads(columns="id,business_name,opportunity_score,revenue_loss,status,amount_paid,niche,city,revenue,monthly_value,website_score")'
new_metrics = 'def get_metrics():\n    raw_leads = db.fetch_leads(columns="id,business_name,opportunity_score,revenue_loss,status,amount_paid,niche,city,revenue,monthly_value,website_score", limit=None)'
code = code.replace(old_metrics, new_metrics)

# 3. Update /api/god-view to use fetch_logs instead of fetch_events
old_god_view = '''@app.get("/api/god-view")
def get_god_view():
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

            events.append({
                "leadId": str(row.get("lead_id") or ""),
                "event": str(row.get("event") or ""),
                "timestamp": ts,
                "isLive": is_live,
                "metadata": row.get("metadata") or {},
            })'''
new_god_view = '''@app.get("/api/god-view")
def get_god_view():
    try:
        raw_logs = db.fetch_logs(limit=100)
        events = []
        now = datetime.now(timezone.utc)
        
        for row in raw_logs:
            ts = row.get("created_at", "")
            is_live = False
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                seconds_ago = (now - dt).total_seconds()
                is_live = seconds_ago < 180
            except:
                pass
                
            msg = str(row.get("message") or "")
            # Extract lead ID if present or just use hash of message
            import hashlib
            lead_id = hashlib.md5(msg.encode()).hexdigest()[:8]

            events.append({
                "leadId": lead_id,
                "event": str(row.get("service_name") or "System") + ": " + (msg[:30] + '...' if len(msg) > 30 else msg),
                "timestamp": ts,
                "isLive": is_live,
                "metadata": {},
            })'''
code = code.replace(old_god_view, new_god_view)

# 4. Update /api/agents to dynamically read logs
old_agents = '''@app.get("/api/agents")
def api_get_agents():
    return {"agents": [
        {"name": "Silas", "division": "Outreach", "status": "LIVE", "lastActive": "Now"},
        {"name": "Diamond", "division": "Intelligence", "status": "LIVE", "lastActive": "Now"},
        {"name": "Vex", "division": "QA", "status": "LIVE", "lastActive": "Now"}
    ]}'''
new_agents = '''@app.get("/api/agents")
def api_get_agents():
    logs = db.fetch_logs(limit=50)
    
    agents = {
        "Silas": {"name": "Silas", "division": "Outreach", "status": "IDLE", "lastActive": "Unknown"},
        "Diamond": {"name": "Diamond", "division": "Intelligence", "status": "IDLE", "lastActive": "Unknown"},
        "Vex": {"name": "Vex", "division": "QA", "status": "IDLE", "lastActive": "Unknown"}
    }
    
    now = datetime.now(timezone.utc)
    for log in logs:
        svc = str(log.get("service_name", "")).lower()
        ts = log.get("created_at", "")
        
        agent_name = None
        if "silas" in svc or "outreach" in svc: agent_name = "Silas"
        elif "diamond" in svc or "gen" in svc or "intel" in svc: agent_name = "Diamond"
        elif "vex" in svc or "qa" in svc or "validat" in svc: agent_name = "Vex"
        
        if agent_name and agents[agent_name]["status"] == "IDLE":
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                mins_ago = (now - dt).total_seconds() / 60
                agents[agent_name]["lastActive"] = f"{int(mins_ago)}m ago"
                if mins_ago < 15:
                    agents[agent_name]["status"] = "LIVE"
                else:
                    agents[agent_name]["status"] = "SLEEPING"
            except:
                pass
                
    return {"agents": list(agents.values())}'''
code = code.replace(old_agents, new_agents)

# 5. Update /api/tasks to fetch pending
old_tasks = '''@app.get("/api/tasks")
def get_tasks():
    # Placeholder for tasks table
    return {"tasks": []}'''
new_tasks = '''@app.get("/api/tasks")
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
        
    return {"tasks": mapped_tasks}'''
code = code.replace(old_tasks, new_tasks)

with open(api_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Patched api.py for fully accurate dashboard sync.")
