import asyncio
import os
import random
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from config import AGENCY_NAME, AGENCY_EMAIL

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

OUR_NAME = AGENCY_NAME
OUR_EMAIL = AGENCY_EMAIL

# Follow-up pitches (different angle from initial)
FOLLOWUP_PITCHES = [
    "Hey, just following up on my earlier message. I actually built a free prototype of a faster version of your site — I'd love to send you the link if you're open to it. No strings attached!",
    "Hi again! I wanted to circle back real quick. I noticed a few things on your website that might be hurting your Google rankings. I put together a quick demo showing how it could look with some updates. Want me to send it over?",
    "Hello! I reached out a few days ago about your website. Just wanted to make sure it didn't end up in spam! I built a custom mockup for your business for free. Let me know if you'd like to see it."
]

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

def fetch_stale_leads():
    """Fetch leads that were contacted more than 3 days ago but never replied."""
    # Query leads that are 'Contacted' — the age check is done client-side
    # because Supabase REST API date filtering is complex
    endpoint = f"{SUPABASE_URL}/rest/v1/leads?status=eq.Contacted&select=*"
    try:
        response = requests.get(endpoint, headers=get_headers())
        response.raise_for_status()
        leads = response.json()
        
        # Filter for leads older than 3 days
        from datetime import datetime, timezone, timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=3)
        
        stale = []
        for lead in leads:
            created = lead.get("created_at", "")
            if created:
                try:
                    lead_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    if lead_date < cutoff:
                        stale.append(lead)
                except:
                    pass
        return stale
    except Exception as e:
        print(f"Error fetching stale leads: {e}")
        return []

def update_status(lead_id, status):
    endpoint = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}"
    try:
        response = requests.patch(endpoint, headers=get_headers(), json={"status": status})
        response.raise_for_status()
    except Exception as e:
        print(f"Error updating status: {e}")

async def submit_followup(page, contact_url, pitch):
    """Submit a follow-up pitch via the contact form."""
    try:
        await page.goto(contact_url, timeout=20000, wait_until='domcontentloaded')
        
        inputs = await page.locator("input, textarea").all()
        inputs_filled = False
        
        for element in inputs:
            type_attr = await element.get_attribute("type")
            name_attr = (await element.get_attribute("name") or "").lower()
            id_attr = (await element.get_attribute("id") or "").lower()
            placeholder = (await element.get_attribute("placeholder") or "").lower()
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            
            if type_attr in ["hidden", "submit", "button"]:
                continue
                
            identifying_text = f"{name_attr} {id_attr} {placeholder}"
            
            if "name" in identifying_text or "first" in identifying_text:
                await element.fill(OUR_NAME)
                inputs_filled = True
            elif "email" in identifying_text:
                await element.fill(OUR_EMAIL)
                inputs_filled = True
            elif "phone" in identifying_text:
                await element.fill("555-019-2834")
            elif tag_name == "textarea" or "message" in identifying_text or "comments" in identifying_text:
                await element.fill(pitch)
                inputs_filled = True
        
        if inputs_filled:
            submit_buttons = await page.locator('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Send")').all()
            if submit_buttons:
                await submit_buttons[0].click()
                await page.wait_for_timeout(3000)
                return True
                
    except Exception as e:
        print(f"  => Error submitting follow-up: {e}")
    
    return False

async def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Supabase credentials not found.")
        return
    
    print("=" * 60)
    print("  THE NUDGE - Follow-Up Bot")
    print("  Finding leads contacted 3+ days ago with no reply...")
    print("=" * 60)
    
    stale_leads = fetch_stale_leads()
    print(f"\nFound {len(stale_leads)} stale leads to follow up on.")
    
    if not stale_leads:
        print("Nothing to nudge. All caught up!")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        success_count = 0
        try:
            for lead in stale_leads:
                contact_url = lead.get("contact_url", "")
                website = lead.get("website", "")
                lead_id = lead.get("id")
                domain = urlparse(website).netloc.replace("www.", "")
                
                if not contact_url:
                    continue
                
                pitch = random.choice(FOLLOWUP_PITCHES)
                print(f"\nNudging: {domain}")
                
                success = await submit_followup(page, contact_url, pitch)
                
                if success:
                    print(f"  => SUCCESS! Follow-up sent to {domain}")
                    update_status(lead_id, "FollowedUp")
                    success_count += 1
                else:
                    print(f"  => FAILED to send follow-up to {domain}")
                
                await page.wait_for_timeout(random.randint(5000, 15000))
        finally:
            await browser.close()
    
    print(f"\n{'=' * 60}")
    print(f"  NUDGE COMPLETE: {success_count}/{len(stale_leads)} follow-ups sent")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    asyncio.run(main())
