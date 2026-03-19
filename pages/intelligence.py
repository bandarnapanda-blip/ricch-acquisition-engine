import streamlit as st
import pandas as pd
from database import db
import logging

def render_intelligence():
    st.title("🧠 Behavioral Intelligence Engine")
    st.write("Real-time behavioral scoring and hot prospect promotion.")

    # 1. Stats Row
    leads = db.fetch_leads()
    hot_prospects = [l for l in leads if l.get('status') == 'Hot Prospect']
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Leads Tracked", len(leads))
    col2.metric("Hot Prospects", len(hot_prospects))
    col3.metric("Avg Opp Score", int(sum(l.get('opportunity_score', 0) for l in leads)/len(leads)) if leads else 0)

    # 2. Lead Table with Diamond Audits
    st.subheader("High-Value Lead Pipeline")
    
    data = []
    for l in leads:
        biz_name = l.get('business_name', 'Unknown')
        # Match audit filename logic
        audit_filename = f"{biz_name.lower().replace(' ', '-')}-audit.html"
        audit_url = f"https://bandarnapanda-blip.github.io/ricch-acquisition-engine/diamond_reports/{audit_filename}"
        
        data.append({
            "Business": biz_name,
            "Opp Score": l.get('opportunity_score', 0),
            "Status": l.get('status', 'Leaking'),
            "Last Seen": l.get('updated_at', 'N/A')[:10],
            "Diamond Audit": audit_url
        })
    
    df = pd.DataFrame(data)
    
    # Render with clickable links
    st.dataframe(
        df,
        column_config={
            "Diamond Audit": st.column_config.LinkColumn("Diamond Audit", help="Click to view bespoke revenue audit")
        },
        use_container_width=True
    )

    # 3. Live Pulse
    st.subheader("Live Activity Stream")
    logs = db._session.get(f"{db.url}/rest/v1/activity_logs?order=created_at.desc&limit=10", headers=db.headers).json()
    for entry in logs:
        st.info(f"[{entry.get('created_at', '')[11:16]}] {entry.get('message', '')}")

if __name__ == "__main__":
    render_intelligence()
