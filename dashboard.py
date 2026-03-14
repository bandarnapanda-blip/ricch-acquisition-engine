import streamlit as st
import requests
import os
import json
import pandas as pd
import pydeck as pdk
import plotly.express as px
import textwrap
from datetime import datetime
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
from streamlit_supabase_auth import login_form
from config import CITIES, NICHES, AGENCY_NAME, AGENCY_DOMAIN

# Load Environment
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ──────────────────────────────  CONFIG & DATA  ──────────────────────────────
COORDS_FILE = "city_coords.json"
BENCHMARK_FILE = "competitor_benchmarks.json"

import subprocess
try:
    CREATE_NEW_CONSOLE = subprocess.CREATE_NEW_CONSOLE
except AttributeError:
    CREATE_NEW_CONSOLE = 0x00000010

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

@st.cache_data(ttl=3600)
def load_coords():
    """Load and cache coordinate data."""
    if os.path.exists(COORDS_FILE):
        with open(COORDS_FILE, 'r') as f:
            return json.load(f)
    return {}

@st.cache_data(ttl=300)
def fetch_leads():
    """Fetch leads from Supabase."""
    endpoint = f"{SUPABASE_URL}/rest/v1/leads?select=*&order=created_at.desc"
    try:
        response = requests.get(endpoint, headers=get_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching leads: {e}")
        return []

def update_lead_status(lead_id, new_status):
    """Update a lead's status in Supabase."""
    endpoint = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}"
    try:
        response = requests.patch(endpoint, headers=get_headers(), json={"status": new_status})
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error updating lead: {e}")
        return False

@st.cache_data(ttl=5) # Slightly longer for stability
def fetch_activity_logs(limit=30):
    """Fetch recent activity logs from Supabase."""
    endpoint = f"{SUPABASE_URL}/rest/v1/activity_logs?select=*&order=created_at.desc&limit={limit}"
    try:
        response = requests.get(endpoint, headers=get_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return []

def push_log(service, message):
    """Push a log entry to Supabase (mostly for internal use in other scripts, but kept here for completeness)."""
    endpoint = f"{SUPABASE_URL}/rest/v1/activity_logs"
    try:
        requests.post(endpoint, headers=get_headers(), json={"service_name": service, "message": message})
    except:
        pass

# ──────────────────────────────  PAGE CONFIG  ──────────────────────────────
st.set_page_config(
    page_title=f"{AGENCY_NAME} OS",
    page_icon="💎",
    layout="wide"
)

# ──────────────────────────────  CUSTOM CSS  ──────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=Outfit:wght@300;700;900&display=swap');
    
    :root {
        --bg-main: #0a0b10;
        --bg-side: #0e1018;
        --bg-card: #161922;
        --border: rgba(255, 255, 255, 0.05);
        --text-dim: rgba(255, 255, 255, 0.4);
        --accent-pink: #ff4d94;
        --accent-purple: #9d7cff;
        --accent-blue: #00e5ff;
    }

    .stApp {
        background-color: var(--bg-main);
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #fff;
    }

    /* Top Bar */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0 30px 0;
    }
    .search-container {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 5px 15px;
        display: flex;
        align-items: center;
        width: 300px;
    }
    .profile-circle {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        background: linear-gradient(45deg, var(--accent-pink), var(--accent-purple));
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid rgba(255,255,255,0.1);
    }

    /* Layout Cards */
    .lx-card {
        background: linear-gradient(145deg, #1a1d28, #11131a);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 24px;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .lx-card:hover {
        border-color: rgba(255, 255, 255, 0.3);
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    }
    .lx-card.elite-card {
        border: 2px solid #ffd70033;
        background: linear-gradient(145deg, #1f1a0a, #11131a);
    }
    .lx-card.elite-card:hover {
        border-color: #ffd700;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.2);
    }

    /* Circular Progress */
    .circle-wrap {
        position: relative;
        width: 80px;
        height: 80px;
    }
    .circle-bg {
        fill: none;
        stroke: rgba(255,255,255,0.05);
        stroke-width: 4;
    }
    .circle-progress {
        fill: none;
        stroke-width: 4;
        stroke-linecap: round;
        transform: rotate(-90deg);
        transform-origin: center;
        transition: stroke-dasharray 0.5s ease;
    }

    /* Sidebar simulation - Responsive fix */
    @media (min-width: 1200px) {
        .side-nav {
            position: fixed;
            left: 20px;
            top: 20px;
            bottom: 20px;
            width: 70px;
            background: var(--bg-side);
            border-radius: 20px;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 30px 0;
            z-index: 1000;
        }
        .main-content {
            margin-left: 100px;
        }
    }
    @media (max-width: 1199px) {
        .side-nav {
            display: none;
        }
        .main-content {
            margin-left: 0;
        }
    }
    .side-icon {
        width: 40px;
        height: 40px;
        margin-bottom: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        color: var(--text-dim);
        cursor: pointer;
        transition: all 0.2s;
    }
    .side-icon.active {
        color: var(--accent-pink);
        background: rgba(255, 77, 148, 0.1);
    }

    /* Lead Item */
    .lead-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px;
        border-bottom: 1px solid var(--border);
        transition: background 0.2s;
    }
    .lead-item:hover {
        background: rgba(255,255,255,0.02);
    }
    .lead-icon {
        width: 40px;
        height: 40px;
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
    }
    
    /* Scanning Animation Overlay */
    @keyframes scanline {
        0% { transform: translateY(-100%); }
        100% { transform: translateY(100%); }
    }
    .scanning-overlay {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(to bottom, transparent 50%, rgba(255, 77, 148, 0.05) 50%);
        background-size: 100% 4px;
        pointer-events: none;
        z-index: 9999;
        opacity: 0.3;
        animation: scanline 10s linear infinite;
    }
    .scanning-glow {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle at center, rgba(157, 124, 255, 0.05) 0%, transparent 70%);
        pointer-events: none;
        z-index: 9998;
    }
    .live-badge {
        background: var(--accent-pink);
        color: white;
        padding: 4px 12px;
        border-radius: 30px;
        font-size: 0.65rem;
        font-weight: 900;
        letter-spacing: 1.5px;
        box-shadow: 0 0 15px var(--accent-pink);
        animation: pulse 2s infinite;
        vertical-align: middle;
        margin-left: 10px;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    .stTabs [data-baseweb="tab-list"] { gap: 30px; }
    .stTabs [data-baseweb="tab"] { color: var(--text-dim); border: none; font-weight: 600; font-size: 1rem; }
    .stTabs [aria-selected="true"] { color: #fff !important; border-bottom: 2px solid var(--accent-pink) !important; }
    
    /* Global Card Hover Precision */
    div[data-testid="stVerticalBlock"] > div.lx-card {
        cursor: pointer;
    }
</style>
<script>
const updateMouse = (e) => {
    const cards = document.querySelectorAll('.lx-card');
    cards.forEach(card => {
        const rect = card.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        card.style.setProperty('--mouse-x', `${x}%`);
        card.style.setProperty('--mouse-y', `${y}%`);
    });
};
window.addEventListener('mousemove', updateMouse);
</script>
""", unsafe_allow_html=True)

# ──────────────────────────────  SESSION STATE  ──────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "map_bearing" not in st.session_state:
    st.session_state.map_bearing = 30
if "is_scraping" not in st.session_state:
    st.session_state.is_scraping = False
if "system_logs" not in st.session_state:
    st.session_state.system_logs = ["System Initialized.", "Authenticating with Supabase OS...", "Ready for Command."]

def add_log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.system_logs.append(f"[{timestamp}] {msg}")
    if len(st.session_state.system_logs) > 50:
        st.session_state.system_logs.pop(0)

@st.fragment(run_every="5s")
def render_orbital_map(df_map):
    st.session_state.map_bearing = (st.session_state.map_bearing + 5) % 360
    
    view_state = pdk.ViewState(
        latitude=df_map['lat'].mean() if not df_map.empty else 37.09,
        longitude=df_map['lon'].mean() if not df_map.empty else -95.71,
        zoom=3.5,
        pitch=60,
        bearing=st.session_state.map_bearing
    )
    
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v10',
        initial_view_state=view_state,
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df_map,
                get_position='[lon, lat]',
                get_color='[255, 77, 148, 200]',
                get_radius='size',
                pickable=True,
                auto_highlight=True,
                radius_min_pixels=5,
                radius_max_pixels=30
            ),
            pdk.Layer(
                'TextLayer',
                data=df_map,
                get_position='[lon, lat]',
                get_text='name',
                get_color='[255, 255, 255, 200]',
                get_size=18,
                get_alignment_baseline='"bottom"',
                font_family='"Outfit", sans-serif'
            )
        ],
        tooltip={"text": "{name}"}
    ))

# ──────────────────────────────  SHADOW PREVIEW ROUTER  ──────────────────────
if "preview_id" in st.query_params:
    pid = st.query_params["preview_id"]
    leads = fetch_leads()
    found_lead = next((l for l in leads if str(l.get('id')) == str(pid)), None)
    
    if found_lead:
        from generate_landing import generate_page
        opp_score = found_lead.get('opportunity_score', 0)
        html_code = generate_page(
            found_lead.get('business_name', 'Lead'),
            found_lead.get('niche', 'Niche'),
            found_lead.get('city', 'City'),
            lead_id=found_lead.get('id'),
            score=opp_score
        )
        
        # Display the redesign in a clean full-screen wrapper
        st.markdown("""
            <style>
                [data-testid="stSidebar"] { display: none; }
                .stApp { background: white !important; }
                footer {visibility: hidden;}
                header {visibility: hidden;}
            </style>
        """, unsafe_allow_html=True)
        
        st.components.v1.html(html_code, height=900, scrolling=True)
        
        if st.button("⬅️ EXIT PREVIEW & RETURN TO COMMAND"):
            # Clear query params to return to dashboard
            st.query_params.clear()
            st.rerun()
        st.stop()
    else:
        st.error(f"Redesign Profile {pid} not found in the local database.")
        if st.button("Return to Intelligence HQ"):
            st.query_params.clear()
            st.rerun()
        st.stop()
# 1. Check for Active Session or Bypass
session = None
if os.getenv("DEV_BYPASS", "False").lower() == "true" or st.session_state.get("auth_bypassed", False):
    session = {"user": {"email": "dev@luxury-os.local"}}

if not session:
    # 2. Sidebar Troubleshooting (Visible during Login)
    with st.sidebar.expander("🛠️ Login Troubleshooting"):
        st.write("If you are hitting Supabase email rate limits:")
        if st.button("🚀 ENTER LOCAL DEV MODE"):
            st.session_state.auth_bypassed = True
            st.rerun()

    # 3. Standard Login Form
    session = login_form(
        url=SUPABASE_URL,
        apiKey=SUPABASE_KEY,
        providers=[],
    )

if not session:
    st.info("Secure Login Required. (Use 'Login Troubleshooting' in the sidebar if you are rate-limited)")
    st.stop()

if st.session_state.get("auth_bypassed", False):
    st.sidebar.success("🛡️ LOGGED IN VIA DEV BYPASS")

# ──────────────────────────────  DATA PREP  ──────────────────────────────
leads = fetch_leads()
df = pd.DataFrame(leads)
activity_logs = fetch_activity_logs()

if not df.empty:
    # Fix potential NaN errors
    df['revenue'] = df.get('revenue', pd.Series([0]*len(df))).fillna(0).astype(float)
    df['opportunity_score'] = df.get('opportunity_score', pd.Series([0]*len(df))).fillna(0).astype(int)
    df['mobile_score'] = df.get('mobile_score', pd.Series([0]*len(df))).fillna(0).astype(int)
    df['speed_score'] = df.get('speed_score', pd.Series([0]*len(df))).fillna(0).astype(int)
    df['seo_score'] = df.get('seo_score', pd.Series([0]*len(df))).fillna(0).astype(int)
    df['monthly_value'] = df.get('monthly_value', pd.Series([0]*len(df))).fillna(0).astype(float)
    df['revenue_loss'] = df.get('revenue_loss', pd.Series([0]*len(df))).fillna(0).astype(float)
    df['reply_status'] = df.get('reply_status', pd.Series(['']*len(df))).fillna('')
    
    total_rev = df['revenue'].sum()
    total_leads = len(df)
    leads_contacted = len(df[df['status'].isin(['Contacted', 'Replied', 'Demo Sent', 'Closed'])])
    
    # New $1B+ Business Metrics
    total_leakage = df['revenue_loss'].sum()
    
    actual_mrr = df[df['status'] == 'Closed']['monthly_value'].sum()
    potential_mrr = df[df['status'].isin(['Replied', 'Demo Sent'])]['monthly_value'].sum()
    pipeline_mrr = df[df['status'] == 'Contacted']['monthly_value'].sum() * 0.1
    expected_mrr = actual_mrr + potential_mrr + pipeline_mrr
    
    avg_opp = df['opportunity_score'].mean()
    
    # Outreach & Reply Intelligence
    total_sent = len(df[df['status'].isin(['Contacted', 'Replied', 'Demo Sent', 'Closed'])])
    total_replies = len(df[df['status'].isin(['Replied', 'Demo Sent', 'Closed'])])
    reply_rate = (total_replies / total_sent * 100) if total_sent > 0 else 0
    hot_leads = len(df[df['reply_status'] == 'positive'])
else:
    total_rev = 0
    total_leads = 0
    leads_contacted = 0
    total_leakage = 0
    expected_mrr = 0
    avg_opp = 0
    total_sent = 0
    total_replies = 0
    reply_rate = 0
    hot_leads = 0
    potential_mrr = 0

# Calc Heartbeats
def get_service_status(service_name, logs):
    from datetime import timezone
    now = datetime.now(timezone.utc)
    service_logs = [l for l in logs if l['service_name'] == service_name]
    if not service_logs: return "#ff4444"
    last_log_time = datetime.fromisoformat(service_logs[0]['created_at'].replace('Z', '+00:00'))
    diff = (now - last_log_time).total_seconds()
    if diff < 120: return "#00ff88"
    if diff < 600: return "#ffcc00"
    return "#ff4444"

scraper_status = get_service_status("Scraper", activity_logs)
inbox_status = get_service_status("Inbox", activity_logs)
outreach_status = get_service_status("Outreach", activity_logs)

# ──────────────────────────────  UI RENDER  ──────────────────────────────

# ──────────────────────────────  UI RENDER  ──────────────────────────────

with st.sidebar:
    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; color: #ff4d94; font-family: Outfit; font-weight: 900; font-size: 1.2rem;'>{AGENCY_NAME} OS</div>", unsafe_allow_html=True)
    st.write("---")
    
    # Modern Sidebar Menu
    selected_tab = option_menu(
        menu_title=None,
        options=["Dashboard", "Pipeline", "Intelligence", "Showcase", "Settings"],
        icons=["house", "funnel", "graph-up-arrow", "stars", "gear"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "white", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"5px", "--hover-color": "#262730"},
            "nav-link-selected": {"background-color": "#ff4d94"}, # Antigravity Pink
        }
    )
    
    st.write("---")
    if st.button("🔓 Logout", width="stretch"):
        st.session_state.auth_bypassed = False
        st.session_state.authenticated = False
        st.rerun()

# ──────────────────────────────  PAGE ROUTING  ──────────────────────────────
if selected_tab == "Dashboard":
    container = st.container()
    with container:
        # Top Row: Circular Metrics
        def render_circle_metric(label, val, target, color, prefix="$", suffix=""):
            percent = min(100, int((val / target) * 100)) if target > 0 else 0
            dash = percent 
            st.markdown(textwrap.dedent(f"""\
            <div class="lx-card" style="display:flex; align-items:center; justify-content:space-between; height: 120px;">
                <div>
                    <div style="color:var(--text-dim); font-size:0.75rem; text-transform:uppercase; letter-spacing:1.5px; font-weight:600;">{label}</div>
                    <div style="font-size:2rem; font-weight:900; margin:5px 0; font-family:'Outfit'; color:#fff;">{prefix}{val:,}{suffix}</div>
                    <div style="color:rgba(255,255,255,0.2); font-size:0.7rem;">Target: {prefix}{target:,}{suffix}</div>
                </div>
                <div class="circle-wrap">
                    <svg viewBox="0 0 36 36" style="width:100%; height:100%;">
                        <circle class="circle-bg" cx="18" cy="18" r="16" />
                        <circle class="circle-progress" cx="18" cy="18" r="16" 
                                style="stroke:{color}; stroke-dasharray: {dash}, 100; filter: drop-shadow(0 0 5px {color});" />
                    </svg>
                    <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-size:0.85rem; font-weight:800; color:#fff;">{percent}%</div>
                </div>
            </div>
            """), unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1: render_circle_metric("Global Revenue", int(total_rev), 100000, "#ff4d94") 
        with col2: render_circle_metric("Total Leads", total_leads, 5000, "#00e5ff", prefix="")
        with col3: render_circle_metric("Annual Leakage", int((total_leakage * 12)/1000), 5000, "#ff6464", prefix="$", suffix="k")
        with col4: render_circle_metric("Expected MRR", int(expected_mrr), 10000, "#00ff88")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🦾 Outreach Command Centers")
        c1, c2, c3, c4 = st.columns(4)
        with c1: render_circle_metric("Total Sent", total_sent, total_leads, "#ffcc00", prefix="")
        with c2: render_circle_metric("Total Replies", total_replies, total_sent if total_sent > 0 else 100, "#ff4d94", prefix="")
        with c3: render_circle_metric("Reply Rate", int(reply_rate), 100, "#00e5ff", prefix="", suffix="%")
        with c4: render_circle_metric("Hot Leads", hot_leads, total_replies if total_replies > 0 else 20, "#00ff88", prefix="")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Funnel Chart
        st.markdown("### 🌪️ Real-Time Conversion Funnel")
        if not df.empty:
            funnel_data = pd.DataFrame([
                {"Stage": "Found", "Count": len(df)},
                {"Stage": "Contacted", "Count": len(df[df['status'].isin(['Contacted', 'Replied', 'Demo Sent', 'Closed'])])},
                {"Stage": "Replied", "Count": len(df[df['status'].isin(['Replied', 'Demo Sent', 'Closed'])])},
                {"Stage": "Demo Sent", "Count": len(df[df['status'].isin(['Demo Sent', 'Closed'])])},
                {"Stage": "Closed", "Count": len(df[df['status'] == 'Closed'])}
            ])
            import plotly.express as px
            fig_funnel = px.bar(funnel_data, x='Stage', y='Count', color='Stage',
                               color_discrete_map={'Closed': '#ff4d94'},
                               color_discrete_sequence=['#1a1d28'])
            fig_funnel.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                    font_color="white", margin=dict(l=0, r=0, t=10, b=0), height=300, showlegend=False)
            st.plotly_chart(fig_funnel, use_container_width=True)
        
        # System Controls Section
        st.markdown("### ⚙️ OS Command Center")
        ctrl1, ctrl2, ctrl3, ctrl4 = st.columns(4)
        with ctrl1:
            if st.button("🚀 Force Lead Scrape", width="stretch"):
                st.session_state.is_scraping = True
                add_log("Spinning up Lead Discovery Engine...")
                subprocess.Popen(["python", "find_leads.py"], creationflags=CREATE_NEW_CONSOLE)
        with ctrl2:
            if st.button("🧠 Backfill Intel", width="stretch"):
                add_log("Analyzing historical leads...")
                subprocess.Popen(["python", "find_leads.py", "--backfill"], creationflags=CREATE_NEW_CONSOLE)
        with ctrl3:
            if st.button("📥 Inbox & Nurture", width="stretch"):
                add_log("Checking for replies and follow-up opportunities...")
                subprocess.Popen(["python", "inbox_monitor.py"], creationflags=CREATE_NEW_CONSOLE)
                subprocess.Popen(["python", "nurture_engine.py"], creationflags=CREATE_NEW_CONSOLE)
        with ctrl4:
            if st.session_state.is_scraping:
                if st.button("🛑 STOP ENGINE", width="stretch", type="primary"):
                    st.session_state.is_scraping = False
                    add_log("Emergency Engine Shutdown triggered.")
                    st.rerun()
            else:
                a_tier_ready = len(df[df['status'] == 'High Intel Ready']) if not df.empty else 0
                if st.button(f"🤖 War Room: Submit {a_tier_ready} Leads", width="stretch", disabled=a_tier_ready == 0):
                    add_log(f"Initiating mass outreach sequence for {a_tier_ready} high-intel leads...")
                    subprocess.Popen(["python", "auto_submit.py"], creationflags=CREATE_NEW_CONSOLE)

        st.markdown("<br>", unsafe_allow_html=True)
        col_scale1, col_scale2 = st.columns([1, 2])
        with col_scale1:
            st.markdown('<div class="lx-card" style="height:380px;">', unsafe_allow_html=True)
            st.markdown("##### Target Sector Velocity")
            active_niche = st.selectbox("Select Scaling Niche", NICHES, index=0)
            st.markdown(textwrap.dedent(f"""\
            <div style="margin-top:20px; padding:15px; background:rgba(255, 77, 148, 0.05); border-radius:12px; border:1px solid rgba(255, 77, 148, 0.1);">
                <div style="font-size:0.7rem; color:var(--accent-pink); font-weight:800;">CURRENT PARADIGM</div>
                <div style="font-size:1.1rem; font-weight:900; color:#fff; margin:5px 0;">{active_niche}</div>
                <div style="font-size:0.7rem; color:var(--text-dim);">Estimated LTV: $5,500 - $12,000</div>
            </div>
            """), unsafe_allow_html=True)
            if st.button(f"🚀 Deploy {active_niche} Ops", width="stretch"):
                st.session_state.is_scraping = True
                add_log(f"Redirecting Scraper to {active_niche} (High-Ticket Mode)...")
                subprocess.Popen(["python", "find_leads.py", "--niche", active_niche], creationflags=CREATE_NEW_CONSOLE)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_scale2:
            st.markdown('<div class="lx-card" style="height:380px;">', unsafe_allow_html=True)
            st.markdown("##### Executive $10k Pipeline Vision")
            chart_df = pd.DataFrame({
                "Milestone": ["Foundation", "Momentum", "Executive ($10k)"],
                "Required MRR": [1000, 3500, 10000],
                "Current Projection": [potential_mrr] * 3
            })
            fig = px.bar(chart_df, x="Milestone", y=["Required MRR", "Current Projection"], barmode="group", color_discrete_sequence=["#11131a", "#ff4d94"])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(l=0, r=0, t=20, b=0), height=250)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f'<div style="text-align:right; font-size:0.75rem; color:var(--text-dim);">Current Trajectory: <b>${int(potential_mrr):,}/mo</b></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c_left, c_right = st.columns([2, 1])
        with c_left:
            st.markdown('<div class="lx-card" style="height:400px;">', unsafe_allow_html=True)
            st.markdown("### Outreach Performance")
            if not df.empty:
                df['date'] = pd.to_datetime(df['created_at']).dt.date
                daily = df.groupby('date').size().reset_index(name='leads')
                fig_outreach = px.area(daily, x='date', y='leads', color_discrete_sequence=['#ff4d94'])
                fig_outreach.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(l=0, r=0, t=10, b=0), height=300)
                st.plotly_chart(fig_outreach, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c_right:
            st.markdown('<div class="lx-card" style="height:400px; overflow-y:auto;">', unsafe_allow_html=True)
            st.markdown("### Recent Activity Feed")
            recent_logs = activity_logs[:20]
            for log in recent_logs:
                ts = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00')).strftime("%H:%M")
                st.markdown(f'<div style="font-size:0.7rem; color:var(--text-dim); margin-bottom:5px;">[{ts}] {log["message"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            # Bottom Activity Feed Terminal
            st.markdown('<div class="lx-card" style="background:#000; border:1px solid #1a1a1a; padding:15px; font-family:\'Courier New\', monospace; height:200px; overflow-y:auto; border-radius:12px;">', unsafe_allow_html=True)
            st.markdown('<div style="color:#33ff33; font-size:0.8rem; border-bottom:1px solid #1a1a1a; margin-bottom:10px; padding-bottom:5px;">> GLOBAL ACTIVITY TERM [SYNCED]</div>', unsafe_allow_html=True)
            recent_logs_long = activity_logs[:50]
            log_content = ""
            for log in recent_logs_long:
                ts_long = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00')).strftime("%H:%M:%S")
                log_content += f"[{ts_long}] [{log['service_name']}] {log['message']}\n"
            st.code(log_content, language="bash")
            st.markdown('</div>', unsafe_allow_html=True)

elif selected_tab == "Pipeline":
    st.markdown("### 🦾 Industry Pipeline Management")
    
    # Filters in top bar style
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    with fc1: search = st.text_input("🔍 Search leads...", "")
    with fc2: status_f = st.multiselect("Status", df['status'].unique() if not df.empty else ["New"])
    with fc3: min_score = st.slider("Min Score", 0, 100, 0)
    
    filtered_df = df
    if search: filtered_df = filtered_df[filtered_df['website'].str.contains(search, case=False)]
    if status_f: filtered_df = filtered_df[filtered_df['status'].isin(status_f)]
    filtered_df = filtered_df[filtered_df['opportunity_score'] >= min_score]
    
    for _, lead in filtered_df.iterrows():
        with st.container():
            # Fallback score calculation if DB has 0 but audit fields exist
            display_score = lead['opportunity_score']
            from analyzer import get_tier
            tier_label = get_tier(display_score)
            
            from preview_engine import generate_preview_metadata
            preview_meta = generate_preview_metadata(lead)
            preview_url = preview_meta.get("preview_url", "#")

            leakage_html = ""
            if lead.get('revenue_loss', 0) > 0:
                leakage_html = textwrap.dedent(f"""\
                <div style="background:rgba(255,100,100,0.1); border-radius:5px; padding:4px 8px; margin-bottom:5px;">
                    <span style="color:#ff6464; font-size:0.65rem; font-weight:800; display:block; text-transform:uppercase;">Monthly Leakage</span>
                    <span style="color:#ff6464; font-size:1.1rem; font-weight:900;">${lead['revenue_loss']:,}</span>
                </div>
                """)

            st.markdown(f"""
            <div class="lx-card" style="padding:15px; margin-bottom:15px; border-left:4px solid {'var(--accent-pink)' if display_score >= 70 else 'rgba(255,255,255,0.1)'};">
                <div style="display:flex; align-items:center; justify-content:space-between;">
                    <div style="display:flex; align-items:center; gap:15px;">
                        <span style="background:rgba(255, 77, 148, 0.1); color:var(--accent-pink); padding:4px 10px; border-radius:30px; font-size:0.7rem; font-weight:800;">{tier_label}</span>
                        <div>
                            <div style="font-size:1.1rem; font-weight:900; color:#fff; font-family:\'Outfit\';">{lead['website'].replace('https://','').replace('http://','').replace('www.','').strip('/')}</div>
                            <div style="display:flex; align-items:center; gap:5px; margin-top:4px;">
                                <div style="font-size:0.7rem; color:var(--text-dim); text-transform:uppercase; letter-spacing:1px;">{lead.get('niche', 'High-Ticket Lead')} • {lead.get('city', 'United States')}</div>
                            </div>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        {leakage_html}
                        <div style="margin-top:8px;">
                            <span style="color:var(--text-dim); font-size:0.7rem; margin-right:5px;">INTEL SCORE</span>
                            <span style="font-size:1.6rem; font-weight:900; color:{'var(--accent-pink)' if display_score >= 70 else 'white'}; font-family:\'Outfit\';">{display_score}</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Deep Intelligence Audit"):
                icol1, icol2 = st.columns([2, 1])
                with icol1:
                    st.markdown("#### 🦾 Revenue Audit Metrics")
                    t1, t2, t3 = st.columns(3)
                    t1.metric("Mobile Speed", f"{lead['speed_score']}/100")
                    t2.metric("SEO Health", f"{lead.get('seo_score', 0)}/100")
                    t3.metric("Funnel Status", "MISSING" if lead.get('missing_quote_form', True) else "ACTIVE")
                    
                    st.markdown(f"**Shadow Site Preview:** [View Ready-to-Send Demo]({preview_url})")
                    
                    if lead.get('website_roast'):
                        st.markdown('<div style="background:rgba(0, 229, 255, 0.05); border-left:3px solid #00e5ff; padding:15px; border-radius:8px;">', unsafe_allow_html=True)
                        st.markdown(f"**⚡ REVENUE LEAKAGE ANALYSIS:**\n\n{lead['website_roast']}")
                        st.markdown('</div>', unsafe_allow_html=True)
                
                with icol2:
                    st.markdown("#### ⚙️ Operations")
                    n_status = st.selectbox("Update Stage", ["New", "High Intel Ready", "Contacted", "Replied", "Closed"], index=["New", "High Intel Ready", "Contacted", "Replied", "Closed"].index(lead['status']) if lead['status'] in ["New", "High Intel Ready", "Contacted", "Replied", "Closed"] else 0, key=f"s_{lead['id']}")
                    if st.button("Commit Change", key=f"b_{lead['id']}"):
                        if update_lead_status(lead['id'], n_status):
                            st.toast("Intelligence Updated.")
                            st.rerun()
                    
                    st.link_button("🚀 Open Website", lead['website'])
                    if lead.get('contact_url'):
                        st.link_button("✉️ Contact Form", lead['contact_url'])

elif selected_tab == "Intelligence":
    st.markdown("### 🌎 Geographical Command")
    coords_data = load_coords()
    if coords_data:
        map_data = []
        if not df.empty and 'city' in df.columns:
            city_counts = df['city'].value_counts()
            top_cities = city_counts.head(100).to_dict()
            for c, count in top_cities.items():
                if c in coords_data:
                    map_data.append({
                        "lat": coords_data[c]["lat"], 
                        "lon": coords_data[c]["lon"], 
                        "name": f"{c}: {count}", 
                        "size": min(5000, count * 500)
                    })
        
        if map_data:
            df_map = pd.DataFrame(map_data)
            render_orbital_map(df_map)
        else:
            st.info("No location data available for the current leads.")
    else:
        st.error(f"Coordinates file missing or empty: {COORDS_FILE}. Please run lead generation first.")

elif selected_tab == "Showcase":
    st.markdown("### ✨ Authority Showcase: Premium Redesigns")
    st.markdown("These are the elite-tier redesign prototypes generated for your A-Tier targets.")
    
    if not df.empty:
        from preview_engine import generate_preview_metadata
        from portfolio_engine import generate_portfolio_html, save_portfolio
        
        top_leads = df.nlargest(9, 'opportunity_score')
        cols = st.columns(3)
        for i, (_, lead) in enumerate(top_leads.iterrows()):
            with cols[i % 3]:
                meta = generate_preview_metadata(lead)
                is_approved = lead.get('is_approved', False)
                opp_score = lead.get('opportunity_score', 0)
                is_a_tier = opp_score >= 75
                
                card_class = "elite-card" if is_a_tier else ""
                tier_label = f'<div style="font-size:0.6rem; color:#ffd700; font-weight:900; margin-bottom:5px; letter-spacing:1px;">⭐ ELITE HIGH-VALUE TARGET</div>' if is_a_tier else ""
                
                import streamlit.components.v1 as st_comp
                st.markdown(f"""
                <div class="lx-card {card_class}">
                    {tier_label}
                    <div style="font-size:0.55rem; color:var(--text-dim); font-weight:800; letter-spacing:1px;">{meta['niche'].upper()}</div>
                    <div style="font-size:1.2rem; font-weight:900; margin:10px 0; color:#fff;">{meta['business_name']}</div>
                    <div style="font-size:0.75rem; color:var(--text-dim); margin-bottom:10px; display:flex; align-items:center;">
                        <span style="margin-right:5px;">📍</span> {meta['city']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Render prototype in isolated component
                from generate_landing import generate_page
                prototype_html = generate_page(meta['business_name'], meta['niche'], meta['city'], lead_id=lead['id'], score=opp_score)
                st_comp.html(prototype_html, height=250, scrolling=True)
                
                st.markdown(f'<a href="{meta["preview_url"]}" target="_blank" style="display:block; width:100%; text-align:center; padding:12px; background:#fff; color:#000; border-radius:14px; text-decoration:none; font-weight:900; font-size:0.85rem; transition:0.3s; margin-top:10px;">View Full Case Study →</a>', unsafe_allow_html=True)
                
                approval_state = st.toggle("Human Approval", value=is_approved, key=f"app_s_{lead['id']}")
                if approval_state != is_approved:
                    endpoint = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead['id']}"
                    headers = get_headers()
                    try:
                        requests.patch(endpoint, headers=headers, json={"is_approved": approval_state})
                        st.success("Approved!" if approval_state else "Unapproved", icon="✅")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Sync error: {e}")
        
        st.divider()
        if st.button("🔨 Build Public Case Studies", width="stretch"):
            html = generate_portfolio_html(df)
            path = save_portfolio(html)
            st.success(f"Showcase generated at {path}")
            st.balloons()
    else:
        st.info("No leads available to showcase yet.")

elif selected_tab == "Settings":
    st.markdown("### ⚙️ OS Configuration")
    with st.expander("API Keys", expanded=True):
        st.text_input("Supabase URL", SUPABASE_URL, disabled=True)
        st.text_input("Supabase Key", "•" * 20, disabled=True)
    with st.expander("Agency Settings"):
        st.text_input("Agency Name", AGENCY_NAME)
        st.text_input("Target Domain", AGENCY_DOMAIN)

st.markdown("---")
st.markdown('</div>', unsafe_allow_html=True) # End main-content
