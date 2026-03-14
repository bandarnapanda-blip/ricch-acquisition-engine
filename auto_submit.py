import asyncio
import os
import random
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import requests
from openai import AsyncOpenAI
from dotenv import load_dotenv
from config import AGENCY_NAME, AGENCY_EMAIL

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Outreach identity
OUR_NAME = "Ri2ch Growth Lab"
OUR_EMAIL = AGENCY_EMAIL

def push_log(service, message):
    """Push a log entry to Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    endpoint = f"{SUPABASE_URL}/rest/v1/activity_logs"
    try:
        requests.post(endpoint, headers=headers, json={"service_name": service, "message": message}, timeout=5)
    except Exception as e:
        print(f"Log Error: {e}")

# High-Stakes Authority Pitches
def get_fallback_pitch(domain, niche="business", loss="significant", preview_url=""):
    pitches = [
        f"I've been analyzing the web infrastructure for {niche} companies in your area and noticed {domain} is leaking an estimated ${loss}/mo in revenue due to technical gaps. I've already hand-built a high-performance prototype for you to stop the bleed. You can view the redesign here: {preview_url} - Would you be opposed to a 10-minute walk-through?",
        f"While auditing local {niche} sites, I found that {domain} is likely losing you around ${loss} every month in untapped high-ticket leads. I've built a technical proof-of-concept to fix this exact leakage. See the live demo I built for you: {preview_url} - Is it okay if I send over the full audit details?",
        f"I specialize in revenue recovery for the {niche} industry. My audit of {domain} shows an estimated monthly loss of ${loss} due to conversion hooks missing from your current site. I've already built a prototype to recover this: {preview_url} - Would you like to see the revenue breakdown?"
    ]
    return random.choice(pitches)

async def generate_ai_pitch(website_text, domain, niche="Default", loss=5000, preview_url=""):
    api_keys_str = os.environ.get("GEMINI_API_KEYS")
    if not api_keys_str:
        return get_fallback_pitch(domain, niche, f"{loss:,}", preview_url)
        
    api_keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]
    random.shuffle(api_keys)
        
    try:
        pitch_prompt_template = f"""
        ROLE: Senior Revenue Consultant at Ri2ch Growth Lab.
        TARGET: CEO of {domain} ({niche}).
        DATA: Site is leaking ${loss:,}/mo.
        PREVIEW: I've already built their redesign here: {preview_url}
        
        WEBSITE CONTEXT:
        {website_text[:1200]}
        
        TASK:
        Write a blunt, high-authority pitch for a contact form.
        1. Link technical debt to the ${loss:,}/mo revenue bleed.
        2. Specifically mention they can see the solution I already built for them at: {preview_url}
        3. BREVITY: Under 60 words. No "fluff".
        4. CTA: Ask if they want the full technical audit breakdown.
        """
        
        for api_key in api_keys:
            client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            try:
                # Get Pitch
                response = await client.chat.completions.create(
                    model="gemini-1.5-flash",
                    messages=[{"role": "user", "content": pitch_prompt_template}],
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                err_msg = str(e).lower()
                if "429" in err_msg or "rate" in err_msg or "quota" in err_msg:
                    print(f"  => Key ending in ...{api_key[-4:]} limited, trying next...")
                    await asyncio.sleep(2) 
                    continue
                else:
                    print(f"  => API error with key ...{api_key[-4:]}: {e}")
                    continue
            
        print("  => AI generation failed, all keys exhausted or errored. Using fallback.")
        return get_fallback_pitch(domain, niche, f"{loss:,}", preview_url)
    except Exception as e:
        print(f"  => Critical AI generation failure: {e}")
        return get_fallback_pitch(domain, niche, f"{loss:,}", preview_url)

async def auto_submit_form(page, contact_url, pitch):
    try:
        await page.goto(contact_url, timeout=20000, wait_until='domcontentloaded')
        
        # Simple form filler heuristic
        inputs_filled = False
        # Find all inputs
        inputs = await page.locator("input, textarea").all()
        for element in inputs:
            type_attr = await element.get_attribute("type")
            name_attr = (await element.get_attribute("name") or "").lower()
            id_attr = (await element.get_attribute("id") or "").lower()
            placeholder = (await element.get_attribute("placeholder") or "").lower()
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            
            if type_attr in ["hidden", "submit", "button"]:
                continue
                
            identifying_text = f"{name_attr} {id_attr} {placeholder}"
            
            # Skip common honeypot field names
            if any(hp in identifying_text for hp in ["hp_", "honey", "website_url", "alt_email"]):
                continue
                
            # Skip if element is not visible
            is_visible = await element.is_visible()
            if not is_visible:
                continue
                
            if type_attr in ["checkbox", "radio"]:
                # Many forms have a mandatory consent checkbox, let's try to click it if it's there
                try: await element.click()
                except: pass
                continue
                
            if "name" in identifying_text or "first" in identifying_text:
                await element.fill(OUR_NAME)
                inputs_filled = True
            elif "email" in identifying_text:
                await element.fill(OUR_EMAIL)
                inputs_filled = True
            elif "phone" in identifying_text:
                await element.fill("555-019-2834") # Dummy phone if required
            elif tag_name == "textarea" or "message" in identifying_text or "comments" in identifying_text:
                await element.fill(pitch)
                inputs_filled = True
                
        if inputs_filled:
            # Try to find and click submit
            await page.wait_for_timeout(2000) # Give scripts a moment to enable buttons
            submit_buttons = await page.locator('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Send"), .ff-btn-submit').all()
            
            for btn in submit_buttons:
                if await btn.is_visible():
                    print("  => Attempting to submit form...")
                    # If button is disabled, try to wait briefly
                    for _ in range(3):
                        if await btn.is_disabled():
                            await page.wait_for_timeout(1000)
                        else:
                            break
                    
                    try:
                        await btn.click(timeout=5000)
                        await page.wait_for_timeout(3000) # Wait for success message
                        return True
                    except:
                        # Try force click if standard click fails
                        try:
                            await btn.click(force=True, timeout=2000)
                            return True
                        except:
                            continue
                
    except Exception as e:
        print(f"  => Error filling form: {e}")
        
    return False

async def process_lead(semaphore, context, lead, headers):
    """Worker function to process a single lead."""
    async with semaphore:
        website = lead.get("website", "")
        contact_url = lead.get("contact_url", "")
        lead_id = lead.get("id")
        
        if not contact_url:
            return False
            
        domain = urlparse(website).netloc.replace("www.", "")
        print(f"[{domain}] Initiating Submission...")
        
        page = await context.new_page()
        try:
            # Get homepage text for AI context
            text_content = ""
            try:
                probe_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                response = requests.get(website, headers=probe_headers, timeout=12)
                soup = BeautifulSoup(response.text, 'html.parser')
                text_content = ' '.join([p.text for p in soup.find_all(['p', 'h1', 'h2', 'h3'])])
            except Exception as req_err:
                print(f"[{domain}] Warning: Homepage text scrape failed: {req_err}")
            
            # Generate pitch
            niche = lead.get("niche", "Default")
            loss = lead.get("revenue_loss", 5000)
            
            from preview_engine import generate_preview_metadata
            preview_meta = generate_preview_metadata(lead)
            preview_url = preview_meta.get("public_preview_url", "")
            
            pitch = await generate_ai_pitch(text_content, domain, niche=niche, loss=loss, preview_url=preview_url)
            
            # Submit form
            success = await auto_submit_form(page, contact_url, pitch)
            
            if success:
                print(f"[{domain}] SUCCESS!")
                push_log("Outreach", f"Submission Success: {domain} contacted successfully.")
                
                # Update status in Supabase
                try:
                    patch_endpoint = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}"
                    requests.patch(patch_endpoint, headers=headers, json={"status": "Contacted"})
                except: pass
                return True
            else:
                print(f"[{domain}] FAILED auto-submit.")
                return False
                
        except Exception as e:
            print(f"[{domain}] Error: {e}")
            return False
        finally:
            await page.close()
            # Random delay for stealth
            await asyncio.sleep(random.randint(5, 10))

async def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Supabase credentials not found.")
        return
        
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    print("Fetching uncontacted leads...")
    try:
        # Fetch High Intel leads first
        intel_endpoint = f"{SUPABASE_URL}/rest/v1/leads?status=eq.High%20Intel%20Ready&select=*"
        res = requests.get(intel_endpoint, headers=headers)
        leads = res.json() if res.status_code == 200 else []
        
        hp_endpoint = f"{SUPABASE_URL}/rest/v1/leads?status=eq.High%20Priority&select=*"
        res = requests.get(hp_endpoint, headers=headers)
        leads += res.json() if res.status_code == 200 else []
        
        new_endpoint = f"{SUPABASE_URL}/rest/v1/leads?status=eq.New&select=*"
        res = requests.get(new_endpoint, headers=headers)
        leads += res.json() if res.status_code == 200 else []
    except Exception as e:
        print(f"Fetch failed: {e}")
        return
        
    if not leads:
        print("No new leads.")
        return
    
    # Industrial Scaling: Parallel Processing
    CONCURRENCY_LIMIT = 10
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    print(f"Processing {len(leads)} leads with {CONCURRENCY_LIMIT} parallel workers...")
    push_log("Outreach", f"Initiating 10x Parallel Outreach for {len(leads)} leads.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        tasks = [process_lead(semaphore, context, lead, headers) for lead in leads[:50]] # Limit batch size
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for r in results if r)
        print(f"Finished! Successfully contacted {success_count} businesses.")
        push_log("Outreach", f"Mission Complete: {success_count} submissions successful.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
