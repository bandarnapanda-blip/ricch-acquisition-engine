import os
import time
import random
import requests
import asyncio
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth
from google import genai
from database import db
from config import STATE, AGENCY_NAME, AGENCY_EMAIL
import generate_landing
import analyzer

# AI Initialization
GEMINI_KEYS = [k.strip() for k in os.getenv("GEMINI_API_KEYS", "").split(",") if k.strip()]
if not GEMINI_KEYS:
    GEMINI_KEYS = [os.getenv("GEMINI_API_KEY", "")]

def get_ai_client(index=0):
    key = GEMINI_KEYS[index % len(GEMINI_KEYS)] if GEMINI_KEYS else None
    if not key:
        return None
    return genai.Client(api_key=key)

# ─── TASK: SCRAPE ───
def task_scrape_leads(niche, city):
    """Heavy lift: Search web for niche targets in city."""
    db.push_log("Worker/Scraper", f"Starting industrial hunt for {niche} in {city}")
    
    # Logic extracted from find_leads.py
    from find_leads import scrape_query, QUERY_TEMPLATES
    
    all_leads = []
    for template in QUERY_TEMPLATES[:3]: # Scale to first 3 queries for speed
        query = template.format(niche=niche, city=city)
        leads = scrape_query(query, niche, city)
        all_leads.extend(leads)
        time.sleep(random.uniform(2, 5))
    
    # Save to DB
    new_count = 0
    for lead in all_leads:
        # Avoid duplicate websites for the same city
        res = db.upsert_lead(lead)
        if res:
            new_count += 1
            
    db.push_log("Worker/Scraper", f"Finished hunt. Identified {len(all_leads)} leads ({new_count} new).")
    return {"status": "success", "found": len(all_leads), "new": new_count}

# ─── TASK: AUDIT ───
def task_audit_lead(lead_id):
    """Heavy lift: Technical audit, revenue loss, and opportunity scoring."""
    leads = db.fetch_leads({"id": f"eq.{lead_id}"})
    if not leads:
        return {"status": "error", "message": "Lead not found"}
    
    lead = leads[0]
    website = str(lead.get('website', ''))
    if not website:
        return {"status": "error", "message": "No website URL"}
    
    db.push_log("Worker/Audit", f"Running deep intelligence audit for {lead.get('website')}")
    
    try:
        # Technical Audit
        audit_results = analyzer.analyze_site(website)
        
        # Scoring
        opp_score = analyzer.calculate_opportunity_score(audit_results)
        revenue_loss = analyzer.calculate_revenue_loss(lead.get('niche', 'Default'), audit_results)
        
        # AI Roast/Audit Generation
        client = get_ai_client()
        audit_roast = "Audit failed"
        if client:
            prompt = f"Role: Senior Revenue Engineer. Analyze this website audit for {website} ({lead.get('niche')}). Audit data: {audit_results}. Write a 3-sentence blunt summary of why they are losing money and how a redesign fixes it."
            response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            audit_roast = str(response.text or "Audit analysis incomplete.").strip()

        # Update Lead
        update_data = {
            "opportunity_score": opp_score,
            "revenue_loss": revenue_loss,
            "website_roast": audit_roast,
            "speed_score": audit_results.get('page_speed_score', 0),
            "seo_score": audit_results.get('seo_score', 0),
            "status": "High Intel Ready" if opp_score >= 50 else "New"
        }
        db.update_lead(lead_id, update_data)
        
        return {"status": "success", "score": opp_score}
    except Exception as e:
        db.push_log("Worker/Audit", f"CRITICAL FAILURE for {website}: {e}")
        return {"status": "failed", "error": str(e)}

# ─── TASK: REDESIGN (GENERATE LANDING) ───
def task_generate_redesign(lead_id):
    """Heavy lift: Build the premium prototype."""
    leads = db.fetch_leads({"id": f"eq.{lead_id}"})
    if not leads: return {"status": "error", "message": "Lead not found"}
    
    lead = leads[0]
    website = str(lead.get('website') or "Company")
    db.push_log("Worker/Architect", f"Forging elite redesign for {website}")
    
    try:
        from generate_landing import generate_page, upload_to_supabase_storage
        
        # Safe Business Name Extraction
        clean_name = website.replace('http://','').replace('https://','').replace('www.','').split('.')[0]
        if not clean_name: clean_name = "Elite Business"

        html = generate_page(
            business_name=str(clean_name),
            niche=str(lead.get('niche') or "Premium Service"),
            city=str(lead.get('city') or "Your Location"),
            lead_id=lead_id,
            score=int(lead.get('opportunity_score') or 0)
        )
        
        # Safe Filename
        safe_name = f"demo-{lead_id}.html"
        demo_url = upload_to_supabase_storage(html, safe_name)
        
        if demo_url:
            db.update_lead(lead_id, {"demo_link": demo_url})
            return {"status": "success", "url": demo_url}
        else:
            return {"status": "failed", "message": "Upload failed"}
            
    except Exception as e:
        db.push_log("Worker/Architect", f"Redesign failed for {website}: {e}")
        return {"status": "failed", "error": str(e)}

# ─── TASK: OUTREACH ───
async def task_send_outreach(lead_id):
    """Heavy lift: Playwright auto-submission."""
    leads = db.fetch_leads({"id": f"eq.{lead_id}"})
    if not leads: return {"status": "error"}
    
    lead = leads[0]
    if not lead.get('contact_url'):
        return {"status": "error", "message": "No contact form URL"}
    
    db.push_log("Worker/Nurture", f"Initializing stealth outreach for {lead.get('website')}")
    
    try:
        from auto_submit import generate_ai_pitch, auto_submit_form
        from playwright.async_api import async_playwright
        
        pitch = await generate_ai_pitch(
            website_text=lead.get('website_roast', ''),
            domain=lead.get('website', ''),
            niche=lead.get('niche', 'Business'),
            loss=lead.get('revenue_loss', 0),
            preview_url=lead.get('demo_link', '')
        )
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            stealth = await page.goto(lead['contact_url'])
            
            # The auto_submit_form logic
            success = await auto_submit_form(page, lead['contact_url'], pitch)
            await browser.close()
            
            if success:
                db.update_lead(lead_id, {"status": "Contacted"})
                return {"status": "success"}
                
        return {"status": "failed"}
    except Exception as e:
        db.push_log("Worker/Nurture", f"Outreach failed: {e}")
        return {"status": "failed", "error": str(e)}
