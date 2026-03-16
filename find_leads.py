import re
import requests
import time
import random
import os
import argparse
import asyncio
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from config import CITIES, NICHES, STATE
from analyzer import analyze_site, generate_ai_audit, calculate_opportunity_score, calculate_revenue_loss
from antigravity_deal_score import SerpKeyManager

# Initialize SerpAPI Key Manager
serp_manager = SerpKeyManager()

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Warning: Supabase credentials not found in .env file. Falling back to CSV.")

OUTPUT_FILE = "leads.csv"
MAX_RESULTS_PER_QUERY = 10

DIRECTORY_DOMAINS = [
    'duckduckgo.com', 'yelp.com', 'angi.com', 'bbb.org', 'facebook.com',
    'homeadvisor.com', 'houzz.com', 'thumbtack.com', 'porch.com',
    'expertise.com', 'google.com', 'mapquest.com', 'yellowpages.com',
    'nextdoor.com', 'instagram.com', 'tiktok.com', 'twitter.com',
    'linkedin.com', 'pinterest.com', 'reddit.com', 'wikipedia.org'
]

# 10x Scaling: Query Expansion Templates
QUERY_TEMPLATES = [
    "{niche} in {city}",
    "best {niche} {city}",
    "{niche} contractors {city}",
    "{niche} companies {city}",
    "top rated {niche} in {city}"
]

def request_with_retry(method, url, **kwargs):
    """Wrapper for requests with exponential backoff to handle connection drops."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
            if attempt == max_retries - 1:
                print(f"  [ERROR] Request failed after {max_retries} attempts: {e}")
                raise
            wait = 2 ** attempt + random.uniform(0, 1)
            print(f"  [RETRY] Connection issue ({e}). Retrying in {wait:.1f}s...")
            time.sleep(wait)
    return None

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_contact_page(base_url):
    contact_url = None
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        common_paths = ['/contact', '/contact-us', '/about', '/about-us']
        for path in common_paths:
            test_url = urljoin(base_url, path)
            try:
                response = requests.get(test_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    return test_url
            except requests.RequestException:
                continue
                
        try:
            response = requests.get(base_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    text = a_tag.get_text().lower()
                    if 'contact' in text or 'contact' in href.lower():
                        full_url = urljoin(base_url, href)
                        if is_valid_url(full_url):
                            return full_url
        except requests.RequestException:
            pass
            
    except Exception as e:
        print(f"Error finding contact page for {base_url}: {e}")
        
    return contact_url


def scrape_query_playwright(query):
    """Scrape DuckDuckGo using Playwright for high resilience."""
    leads_urls = []
    print(f"  [STEALTH] Launching Playwright browser for \"{query}\"...")
    try:
        from playwright.sync_api import sync_playwright
        with Stealth().use_sync(sync_playwright()) as p:
            browser = p.chromium.launch(headless=True)
            
            # [STEALTH] Randomize Fingerprint
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ]
            resolutions = [
                {"width": 1920, "height": 1080},
                {"width": 1366, "height": 768},
                {"width": 1440, "height": 900}
            ]
            
            context = browser.new_context(
                user_agent=random.choice(user_agents),
                viewport=random.choice(resolutions)
            )
            page = context.new_page()
            
            # [STEALTH] Stealth is automatically applied by Stealth().use_sync()
            try:
                # High-Resilience Strategy: Use html.duckduckgo.com with Human-like delays
                encoded_query = query.replace(' ', '+')
                url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
                
                page.goto(url, timeout=30000, wait_until="networkidle")
                # [STEALTH] Human Jitter: Random scroll and mouse move
                for _ in range(random.randint(2, 4)):
                    page.mouse.move(random.randint(0, 1000), random.randint(0, 800))
                    page.mouse.wheel(0, random.randint(200, 600))
                    time.sleep(random.uniform(1, 4))
                
                time.sleep(random.uniform(3, 8)) # Mimic human "think time"
                
                # Extract links with specialized resilience
                leads_urls = []
                
                # Selector list based on subagent findings + Universal Fallback
                selectors = ['.result__a', 'h2 a', 'a.result__a', '.b_algo a', 'a[href^="http"]:not([href*="duckduckgo"]):not([href*="microsoft"])']
                
                for selector in selectors:
                    try:
                        results = page.locator(selector).all()
                        for r in results:
                            href = r.get_attribute('href')
                            if not href: continue
                            
                            # Handle DDG Redirects (uddg)
                            clean_url = href
                            if 'uddg=' in href:
                                import urllib.parse
                                parsed = urllib.parse.urlparse(href)
                                params = urllib.parse.parse_qs(parsed.query)
                                uddg_param = params.get('uddg', [''])[0]
                                if uddg_param:
                                    clean_url = urllib.parse.unquote(uddg_param)
                            
                            if clean_url and 'http' in clean_url and not any(d in clean_url for d in DIRECTORY_DOMAINS) and 'duckduckgo' not in clean_url:
                                leads_urls.append(clean_url)
                    except: continue
                    if len(leads_urls) >= MAX_RESULTS_PER_QUERY: break
                
                # If still nothing, try a super-aggressive universal grab
                if not leads_urls:
                    links = page.locator('a').all()
                    for link in links:
                        try:
                            href = link.get_attribute('href')
                            if href and 'http' in href and not any(d in href for d in DIRECTORY_DOMAINS) and 'duckduckgo' not in href:
                                leads_urls.append(href)
                        except: continue
                        if len(leads_urls) >= MAX_RESULTS_PER_QUERY: break
                    
            except Exception as e:
                # Check for CAPTCHA / Blocks
                page_content = page.content().lower() if 'page' in locals() else ""
                if "captcha" in page_content or "robot" in page_content or "too many requests" in page_content or "anomaly-modal" in page_content:
                    print(f"  [BLOCK] CAPTCHA or Rate Limit detected on DuckDuckGo. Initiating Emergency Backoff...")
                    push_log("Scraper", "CAPTCHA detected. Initiating 15-minute stealth backoff.")
                    time.sleep(900) # 15 minute backoff
                else:
                    print(f"  [ERROR] Playwright search failed: {e}")
            finally:
                browser.close()
    except Exception as outer_e:
        print(f"  [CRITICAL] Playwright standard initialization failed: {outer_e}")
        
    return list(set(leads_urls))

def scrape_query_brave(query):
    """Fallback: Scrape Brave Search for high authority results."""
    leads_urls = []
    print(f"  [BRAVE] Launching Brave search for \"{query}\"...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        url = f"https://search.brave.com/search?q={query.replace(' ', '+')}"
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Scrape Brave results
        results = soup.select('.result-header a, a.result-header')
        for r in results:
            href = r.get('href')
            if href and 'http' in href and not any(d in href for d in DIRECTORY_DOMAINS) and 'brave.com' not in href:
                leads_urls.append(href)
    except Exception as e:
        print(f"  [ERROR] Brave search failed: {e}")
    return list(set(leads_urls))

def scrape_query_bing(query):
    """Scrape Bing multi-page for high volume discovery."""
    leads_urls = []
    print(f"  [FALLBACK] Launching Bing search for \"{query}\"...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    
    # Industrial Scaling: Check first 3 pages
    for page_num in range(3):
        try:
            offset = page_num * 10 + 1
            url = f"https://www.bing.com/search?q={query.replace(' ', '+')}&first={offset}"
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract links with broad BeautifulSoup selectors
            results = soup.select('li.b_algo h2 a, .b_algo a, h2 a, .result__a, article a')
            for r in results:
                href = r.get('href')
                if href and 'http' in href and not any(d in href for d in DIRECTORY_DOMAINS) and not any(s in href for s in ['bing.com', 'microsoft.com', 'duckduckgo.com']):
                    leads_urls.append(href)
            
            # Final Fallback: Grab ANY external link that isn't a directory
            if not leads_urls:
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if 'http' in href and not any(d in href for d in DIRECTORY_DOMAINS) and not any(s in href for s in ['bing.com', 'microsoft.com', 'duckduckgo.com', 'facebook.com', 'twitter.com', 'instagram.com']):
                        leads_urls.append(href)

            if len(leads_urls) >= MAX_RESULTS_PER_QUERY * 3:
                break
            time.sleep(random.uniform(2, 4))
        except Exception as e:
            print(f"  [ERROR] Bing search (Page {page_num}) failed: {e}")
            break
            
    return list(set(leads_urls))

def scrape_query_serpapi(query):
    """Primary high-speed scraper using SerpAPI with key rotation."""
    leads_urls = []
    key = serp_manager.get_key()
    if not key:
        return []
        
    print(f"  [SERPAPI] Hunting for \"{query}\" using key ending in {key[-5:]}...")
    
    from serpapi import GoogleSearch
    try:
        search = GoogleSearch({
            "q": query,
            "api_key": key,
            "num": MAX_RESULTS_PER_QUERY
        })
        results = search.get_dict()
        
        if "error" in results:
            err = results["error"]
            if "Rate limit" in err or "quota" in err.lower():
                print(f"  [SERPAPI] Key exhausted. Rotating...")
                serp_manager.mark_exhausted(key)
                return scrape_query_serpapi(query) # Retry with new key
            else:
                print(f"  [SERPAPI] Error: {err}")
                return []
                
        for result in results.get("organic_results", []):
            link = result.get("link")
            if link and not any(d in link for d in DIRECTORY_DOMAINS):
                leads_urls.append(link)
                
    except Exception as e:
        print(f"  [SERPAPI] Unexpected error: {e}")
        
    return list(set(leads_urls))

def scrape_query(query, niche, city):
    """Scrape a single search query and return leads list."""
    leads = []
    
    # Try SerpAPI first (Premium/Fast)
    try:
        urls = scrape_query_serpapi(query)
        if urls:
            for url in urls:
                leads.append({"website": url, "contact_url": "", "city": city, "niche": niche})
            return leads
    except Exception as e:
        print(f"  [SERPAPI] Critical failure, falling back: {e}")

    # Try Playwright first
    try:
        urls = scrape_query_playwright(query)
        if urls:
            for url in urls:
                leads.append({"website": url, "contact_url": "", "city": city, "niche": niche})
            return leads
    except Exception:
        pass

    # Try Bing next
    try:
        urls = scrape_query_bing(query)
        if urls:
            for url in urls:
                leads.append({"website": url, "contact_url": "", "city": city, "niche": niche})
            return leads
    except Exception:
        pass

    # Try Brave Search as last high-authority fallback
    try:
        urls = scrape_query_brave(query)
        if urls:
            for url in urls:
                leads.append({"website": url, "contact_url": "", "city": city, "niche": niche})
            return leads
    except Exception:
        pass

    # Legacy DDG Fallback
    encoded_query = query.replace(' ', '+')
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }
    
    try:
        # Use randomness in the endpoint
        url = random.choice([
            f"https://html.duckduckgo.com/html/?q={encoded_query}",
            f"https://duckduckgo.com/html/?q={encoded_query}"
        ])
        
        response = requests.get(url, headers=headers, timeout=15)
        if "anomaly-modal" in response.text:
            print(f"  [WARNING] Captured by CAPTCHA. Retrying with different fingerprint...")
            push_log("Scraper", "CAPTCHA detected on DDG HTML fallback. Fingerprint rotation active.")
            # Drastic Backoff for HTML fallback
            time.sleep(random.uniform(30, 60))
            headers["User-Agent"] = random.choice(user_agents)
            response = requests.get(url, headers=headers, timeout=15)
        
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try multiple patterns for DuckDuckGo links
        # Pattern 1: result__a (Standard DDG HTML)
        org_links = soup.find_all('a', class_='result__a')
        if not org_links:
            # Pattern 2: result__url
            org_links = soup.find_all('a', class_='result__url')
        if not org_links:
            # Pattern 3: Any link that looks like a search result
            org_links = [a for a in soup.find_all('a', href=True) if '/l/?kh=' in a['href'] or 'uddg=' in a['href']]
        
        if not org_links:
            # Pattern 4: Fallback for different DOM
            org_links = soup.select('div.links_main a.result__a')
        
        print(f"  Debug: Found {len(org_links)} raw links on search page.")
        
        parsed_urls = set()
        for a_tag in org_links:
            if len(leads) >= MAX_RESULTS_PER_QUERY:
                break
                
            href = a_tag.get('href', '')
            if not href:
                continue
            
            clean_url = href
            # Extract from redirect
            if 'uddg=' in href:
                import urllib.parse
                parsed = urllib.parse.urlparse(href)
                params = urllib.parse.parse_qs(parsed.query)
                uddg_param = params.get('uddg', [''])[0]
                if uddg_param:
                    clean_url = urllib.parse.unquote(uddg_param)
            
            if not clean_url.startswith('http'):
                if clean_url.startswith('//'):
                    clean_url = 'https:' + clean_url
                elif not any(x in clean_url for x in ['duckduckgo', 'google', 'bing']):
                    clean_url = 'https://' + clean_url.strip('/')
                else:
                    continue
            
            if any(domain in clean_url for domain in DIRECTORY_DOMAINS):
                continue
                
            domain = urlparse(clean_url).netloc
            if not domain:
                continue
            if domain in parsed_urls:
                continue
                
            parsed_urls.add(domain)
            print(f"  Found: {clean_url}")
            leads.append({
                "website": clean_url,
                "contact_url": "",
                "city": city,
                "niche": niche
            })
            
    except requests.RequestException as e:
        print(f"  Error scraping search engine: {e}")

    return leads

def push_log(service, message):
    """Push a log entry to Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    endpoint = f"{SUPABASE_URL}/rest/v1/activity_logs"
    try:
        request_with_retry("POST", endpoint, headers=headers, json={"service_name": service, "message": message}, timeout=10)
    except Exception as e:
        print(f"Log Error: {e}")

def upsert_to_supabase(leads):
    """Upsert all leads to Supabase via REST API."""
    print(f"\nUpserting {len(leads)} leads to Supabase...")
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    success = 0
    for lead in leads:
        payload = {
            "website": lead["website"],
            "contact_url": lead.get("contact_url", ""),
            "niche": lead["niche"],
            "city": lead["city"],
            "opportunity_score": lead.get("opportunity_score", 0),
            "website_score": lead.get("opportunity_score", 0), # Map to existing column
            "mobile_score": lead.get("mobile_score", 0),
            "speed_score": lead.get("speed_score", 0),
            "seo_score": lead.get("seo_score", 0),
            "website_roast": lead.get("website_roast", ""),
            "revenue_loss": lead.get("revenue_loss", 0),
            "status": lead.get("status", "New")
        }
        
        # Check for existence
        check_url = f"{SUPABASE_URL}/rest/v1/leads?website=eq.{lead['website']}"
        try:
            check_res = request_with_retry("GET", check_url, headers=headers)
            if check_res and check_res.json():
                lead_id = check_res.json()[0]['id']
                update_url = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}"
                request_with_retry("PATCH", update_url, headers=headers, json=payload)
            else:
                endpoint = f"{SUPABASE_URL}/rest/v1/leads"
                request_with_retry("POST", endpoint, headers=headers, json=payload)
            success += 1
        except Exception as e:
            print(f"  FAILED to save {lead['website']}: {e}")
    print(f"  Successfully processed {success}/{len(leads)} leads.")

def save_to_csv(leads):
    """Fallback: save leads to a local CSV."""
    import csv
    print(f"\nSaving {len(leads)} leads to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        # Update fieldnames to include new signals
        fieldnames = ["website", "contact_url", "city", "niche", "opportunity_score", "revenue_loss", "missing_quote_form"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(leads)

def main():
    parser = argparse.ArgumentParser(description='The Hound - Lead Scanner')
    parser.add_argument('--niche', type=str, help='Niche to target')
    parser.add_argument('--city', type=str, help='City to target')
    parser.add_argument('--limit', type=int, default=10, help='Max results per query')
    args = parser.parse_args()

    global MAX_RESULTS_PER_QUERY
    MAX_RESULTS_PER_QUERY = args.limit

    active_niches = [args.niche] if args.niche else NICHES
    active_cities = [args.city] if args.city else CITIES

    print("=" * 60)
    print("  THE HOUND - $1B+ Acquisition Engine")
    print(f"  Niches: {', '.join(active_niches)}")
    print(f"  Cities: {len(active_cities)} Hubs Active")
    print("=" * 60)
    
    push_log("Scraper", f"Initialization: Hunting across {len(active_cities)} cities for {len(active_niches)} niches.")
    
    all_leads = []
    
    for niche in active_niches:
        for city in active_cities:
            query_leads = []
            # 10x Scaling: Rotate through expanded queries
            for template in QUERY_TEMPLATES:
                query = template.format(niche=niche, city=city)
                print(f"\n[INDUSTRIAL HUNT] \"{query}\"")
                
                new_leads = scrape_query(query, niche, city)
                if not new_leads:
                    continue
                
                print(f"  Found {len(new_leads)} potential businesses.")
                
                # Audit each lead immediately after scraping a query to show real-time progress
                for lead in new_leads:
                    # Deduplicate before auditing
                    if lead['website'] in [l['website'] for l in query_leads]:
                        continue
                        
                    print(f"  Probing {lead['website']}...")
                    contact_url = get_contact_page(lead["website"])
                    if contact_url:
                        lead["contact_url"] = contact_url
                    
                    # Advanced Analysis
                    audit = analyze_site(lead["website"])
                    if audit:
                        lead.update(audit)
                        opp_score = calculate_opportunity_score(audit, niche=niche)
                        lead["opportunity_score"] = opp_score
                        lead["mobile_score"] = 100 if audit["mobile_friendly"] else 0
                        lead["speed_score"] = audit["page_speed_score"]
                        lead["seo_score"] = audit["seo_score"]
                        lead["revenue_loss"] = calculate_revenue_loss(niche, audit)
                        
                        if opp_score >= 40:
                            from analyzer import get_tier
                            tier = get_tier(opp_score)
                            print(f"    -> !! {tier} (score: {opp_score}) -- Generating CEO Audit...")
                            lead["website_roast"] = generate_ai_audit(lead["website"], audit, niche=niche)
                            lead["status"] = "High Intel Ready"
                        else:
                            print(f"    -> Opportunity Score: {opp_score}")
                    
                    # 10x Scaling: Upsert IMMEDIATELY to show results in dashboard
                    if SUPABASE_URL and SUPABASE_KEY:
                        upsert_to_supabase([lead])
                    else:
                        save_to_csv([lead])
                        
                    query_leads.append(lead)
                    time.sleep(random.uniform(1.0, 2.5)) 

            all_leads.extend(query_leads)
            time.sleep(random.uniform(2, 5))

            time.sleep(random.uniform(3, 7))

            query_delay = random.uniform(3, 7)
            time.sleep(query_delay)
    
    print(f"\n{'=' * 60}")
    print(f"  HUNT COMPLETE: {len(all_leads)} total leads")
    print(f"{'=' * 60}")
    
    print("\nDone! The Billion-Dollar Engine has finished its cycle.")

if __name__ == "__main__":
    main()
