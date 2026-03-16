import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import json
import time
from urllib.parse import urlparse
from google import genai
import whois
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GEMINI_KEYS = [k.strip() for k in os.getenv("GEMINI_API_KEYS", "").split(",") if k.strip()]
if not GEMINI_KEYS:
    GEMINI_KEYS = [os.getenv("GEMINI_API_KEY", "")]

# Billion-Dollar Niche LTV Matrix
NICHE_LTV = {
    "Solar Energy Installers": 15000,
    "Personal Injury Attorneys": 25000,
    "Luxury Home Remodeling": 35000,
    "HVAC & Climate Control": 6000,
    "Dental Implant Specialists": 12000,
    "Epoxy Garage Flooring": 4500,
    "Roofing Contractors": 18000,
    "Concrete & Paving": 9000,
    "Landscaping Design": 12000,
    "Pool & Spa Builders": 45000,
    "Kitchen & Bath Remodelers": 28000,
    "Default": 7500
}

def generate_ai_completion(prompt, attempt=0):
    """Generate AI response using requests fallback for SDK issues."""
    key = GEMINI_KEYS[attempt] if attempt < len(GEMINI_KEYS) else GEMINI_KEYS[0]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.5}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            raise Exception(f"API Error {res.status_code}: {res.text}")
    except Exception as e:
        if attempt < len(GEMINI_KEYS) - 1:
            return generate_ai_completion(prompt, attempt + 1)
        raise e

def calculate_revenue_loss(niche, audit):
    """Estimate monthly revenue leakage based on technical failures."""
    # Find exact or partial match for niche
    ltv = int(NICHE_LTV.get("Default", 7500))
    for k, v in NICHE_LTV.items():
        if k.lower() in niche.lower():
            ltv = int(v)
            break
            
    loss_factor = 0.0
    if not audit.get('mobile_friendly'): loss_factor += 0.30 # Modern mobile bounce is higher
    if audit.get('page_speed_score', 100) < 40: loss_factor += 0.20
    if audit.get('seo_score', 100) < 50: loss_factor += 0.25
    if audit.get('broken_layout_detected'): loss_factor += 0.40 # Professional trust loss
    
    # 3 leads/mo recovery target for high-ticket
    monthly_loss = int(ltv * 3 * loss_factor)
    return max(1000, monthly_loss)

def analyze_site(url):
    """Perform a deep technical audit of the lead website."""
    results = {
        "mobile_friendly": False,
        "page_speed_score": 50,
        "seo_score": 0,
        "tech_stack": [],
        "meta_description": "",
        "title": "",
        "has_ssl": False,
        "domain_age_years": 0,
        "broken_layout_detected": False,
        "missing_quote_form": True,
        "has_social_links": False
    }
    
    try:
        results["has_ssl"] = url.lower().startswith("https")
        
        # Domain Age Check
        try:
            domain = urlparse(url).netloc
            w = whois.whois(domain)
            creation_date = w.creation_date
            if isinstance(creation_date, list): creation_date = creation_date[0]
            if creation_date:
                results["domain_age_years"] = (datetime.now() - creation_date).days // 365
        except: pass

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        start_time = time.time()
        # Verify=False to catch even "bad" sites for analysis
        response = requests.get(url, headers=headers, timeout=12, verify=False) 
        load_time = time.time() - start_time
        
        results["page_speed_score"] = max(5, int(100 - (load_time * 12)))
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results["title"] = soup.title.string if soup.title else ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        results["meta_description"] = meta_desc['content'] if meta_desc else ""
        
        if soup.find('meta', attrs={'name': 'viewport'}):
            results["mobile_friendly"] = True
            
        # Granular SEO Audit
        seo_count = 0
        if results["title"]: seo_count += 20
        if results["meta_description"]: seo_count += 20
        if soup.find('h1'): seo_count += 20
        if soup.find('img', alt=True): seo_count += 20
        if results["has_ssl"]: seo_count += 20
        results["seo_score"] = seo_count
        
        # High-Value Signal: Quote Form
        content = response.text.lower()
        if any(x in content for x in ['form', 'quote', 'contact', 'input type="submit"']):
            results["missing_quote_form"] = False
            
        # High-Value Signal: Social Presence
        if any(x in content for x in ['facebook.com', 'instagram.com', 'linkedin.com']):
            results["has_social_links"] = True
            
        # Broken Layout Detection
        if not soup.find('link', rel='stylesheet') and not soup.find('style'):
            results["broken_layout_detected"] = True
        if not soup.find('body') or len(soup.get_text(strip=True)) < 300:
            results["broken_layout_detected"] = True
        
        # Tech Stack check
        tech_list = []
        if 'wp-content' in content: tech_list.append("WordPress")
        if 'wix.com' in content: tech_list.append("Wix")
        if 'squarespace' in content: tech_list.append("Squarespace")
        results["tech_stack"] = tech_list
        
        # --- PHASE 15: Intelligence & Wealth Signals ---
        try:
            from intelligence import analyze_lead_intelligence
            intel = analyze_lead_intelligence(url, response.text)
            results["intelligence"] = intel
            results["deal_score"] = intel.deal_score
        except Exception as e:
            print(f"Intelligence parse failed: {e}")
            results["deal_score"] = calculate_opportunity_score(results)
            
        return results
    except Exception as e:
        # Return partial data if possible
        print(f"Audit failure for {url}: {e}")
        return results # Return defaults instead of None to prevent 0 scores

def calculate_opportunity_score(audit, niche="Default"):
    """Calculate Tiered Opportunity (A/B/C)."""
    if not audit: return 0
    
    raw_score = 0
    # Technical Debt Pillars
    if not audit.get('mobile_friendly'): raw_score += 30
    if not audit.get('has_ssl'): raw_score += 20
    if audit.get('broken_layout_detected'): raw_score += 25
    if audit.get('missing_quote_form'): raw_score += 15
    if audit.get('page_speed_score', 100) < 40: raw_score += 10
    
    # Authority Bonus
    if audit.get('domain_age_years', 0) >= 5: raw_score += 10
    
    return min(100, raw_score)

def get_tier(score):
    if score >= 75: return "A-Tier (High Value Rebuild)"
    if score >= 45: return "B-Tier (Growth Opportunity)"
    return "C-Tier (Low Priority)"

def generate_ai_audit(url, audit, niche="Default"):
    """Generate high-stakes executive audit bullet points."""
    loss = calculate_revenue_loss(niche, audit)
    score = calculate_opportunity_score(audit, niche)
    tier = get_tier(score)
    
    prompt = f"""
    ROLE: Senior Revenue Consultant at Ri2ch Growth Lab.
    TARGET: CEO of a {niche} business.
    SITE: {url}
    EST. MONTHLY LOSS: ${loss:,}
    OPPORTUNITY TIER: {tier}

    DATA POINTS:
    - Mobile: {"FAIL" if not audit['mobile_friendly'] else "PASS"}
    - Speed: {audit['page_speed_score']}/100
    - Quote Funnel: {"MISSING" if audit['missing_quote_form'] else "EXISTING"}
    - Layout: {"BROKEN/OUTDATED" if audit['broken_layout_detected'] else "STABLE"}

    TASK:
    Write 3 blunt executive bullets. Each bullet MUST link a technical failure 
    directly to the ${loss:,}/mo revenue drain. Create extreme professional urgency.
    NO FLUFF. NO PROMPTING TEXT. JUST THE BULLETS.
    """
    
    try:
        return generate_ai_completion(prompt)
    except Exception as e:
        print(f"AI Audit generation failed: {e}")
        return f"Revenue Audit on Standby. Est Leakage: ${loss:,}/mo. Opportunity: {tier}."

if __name__ == "__main__":
    test_url = "https://losangelesepoxy.com/"
    print(f"Auditing {test_url}...")
    audit = analyze_site(test_url)
    print(f"Intel Tier: {get_tier(calculate_opportunity_score(audit))}")
    print(f"AI Audit Preview:\n{generate_ai_audit(test_url, audit)}")
