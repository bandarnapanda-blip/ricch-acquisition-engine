import os
import requests
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from auto_submit import generate_ai_pitch, auto_submit_form, push_log
from preview_engine import generate_preview_metadata
import asyncio
from playwright.async_api import async_playwright

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SEQUENCE_STAGES = [
    {"stage": "audit_sent", "delay_days": 0, "type": "Initial Audit"},
    {"stage": "demo_sent", "delay_days": 3, "type": "Instant Demo Preview"},
    {"stage": "case_study_sent", "delay_days": 7, "type": "Industry Case Study"},
    {"stage": "tip_sent", "delay_days": 12, "type": "High-Value Technical Tip"},
    {"stage": "final_sent", "delay_days": 20, "type": "Final Resource Packet"}
]

async def process_nurture_sequences():
    print("🚀 Nurture Engine: Checking for follow-up opportunities...")
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # We only nurture "Contacted" leads
    endpoint = f"{SUPABASE_URL}/rest/v1/leads?status=eq.Contacted&select=*"
    try:
        response = requests.get(endpoint, headers=headers)
        leads = response.json()
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for lead in leads:
            last_stage = lead.get('last_stage', 'scraped')
            last_update = datetime.fromisoformat(lead['updated_at'].replace('Z', '+00:00'))
            
            # Find current stage index
            current_idx = -1
            for i, s in enumerate(SEQUENCE_STAGES):
                if s['stage'] == last_stage:
                    current_idx = i
                    break
            
            next_idx = current_idx + 1
            if next_idx >= len(SEQUENCE_STAGES):
                continue # Sequence finished
                
            next_stage = SEQUENCE_STAGES[next_idx]
            wait_time = timedelta(days=next_stage['delay_days'])
            
            if datetime.now(last_update.tzinfo) >= last_update + wait_time:
                print(f"  -> Advancing {lead['website']} to {next_stage['stage']}...")
                
                # Logic to generate niche-specific follow-up pitch
                if next_stage['stage'] == "demo_sent":
                    meta = generate_preview_metadata(lead)
                    pitch = f"Hi, I noticed you haven't seen the redesign prototype I built for {lead['website']} yet. You can view it here: {meta['preview_url']} - Is this something you'd like to discuss?"
                else:
                    pitch = f"Quick follow up regarding the revenue audit for {lead['website']}. Here is a {next_stage['type']} I prepared for you."
                
                if lead.get('contact_url'):
                    success = await auto_submit_form(page, lead['contact_url'], pitch)
                    if success:
                        # Update lead
                        patch_url = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead['id']}"
                        requests.patch(patch_url, headers=headers, json={"last_stage": next_stage['stage']})
                        push_log("Nurture", f"Follow-up {next_stage['stage']} sent to {lead['website']}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(process_nurture_sequences())
