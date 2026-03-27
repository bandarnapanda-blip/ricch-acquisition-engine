# RI2CH AGENCY OS — DIAMOND MAPS
import re
import time
import random
import os
import argparse
import requests
import urllib3
from urllib.parse import urlparse
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from config import CITIES, NICHES, STATE
from analyzer import (
    analyze_site,
    generate_ai_audit,
    calculate_opportunity_score,
    calculate_revenue_loss,
)

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
SUPABASE_URL        = os.getenv("SUPABASE_URL")
SUPABASE_KEY        = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[WARNING] Supabase credentials not found. Falling back to CSV.")

if not GOOGLE_MAPS_API_KEY:
    print("[WARNING] GOOGLE_MAPS_API_KEY not set. Add it to your .env file.")

OUTPUT_FILE = "leads_maps.csv"

# ── DIRECTORY BLACKLIST (same as find_leads.py) ───────────────────────────────
DIRECTORY_DOMAINS = [
    "yelp.com", "yellowpages.com", "angi.com", "angieslist.com",
    "thumbtack.com", "houzz.com", "homeadvisor.com", "bbb.org",
    "tripadvisor.com", "facebook.com", "instagram.com", "linkedin.com",
    "twitter.com", "maps.google.com", "google.com", "bing.com",
    "findlaw.com", "avvo.com", "justia.com", "lawyers.com",
    "healthgrades.com", "zocdoc.com", "vitals.com", "webmd.com",
]

def _is_directory(url: str) -> bool:
    """Returns True if the URL is a directory/aggregator site to skip."""
    if not url:
        return True
    domain = urlparse(url).netloc.lower().replace("www.", "")
    return any(d in domain for d in DIRECTORY_DOMAINS)


# ── GOOGLE PLACES API ─────────────────────────────────────────────────────────

def search_places(niche: str, city: str, limit: int = 20) -> list[dict]:
    """
    Searches Google Places API for businesses matching niche + city.
    Returns list of raw place dicts with name, website, address, phone.
    Uses Text Search API — most flexible for niche queries.
    """
    if not GOOGLE_MAPS_API_KEY:
        print(f"  [Maps] No API key — skipping Google Maps for {niche} in {city}")
        return []

    results   = []
    query     = f"{niche} in {city}"
    endpoint  = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    next_page = None

    print(f"  [Maps] Searching: '{query}'")

    while len(results) < limit:
        params = {
            "query": query,
            "key":   GOOGLE_MAPS_API_KEY,
            "type":  "establishment",
        }
        if next_page:
            params = {"pagetoken": next_page, "key": GOOGLE_MAPS_API_KEY}
            time.sleep(2)  # Google requires delay before using page token

        try:
            resp = requests.get(endpoint, params=params, timeout=15)
            data = resp.json()

            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                print(f"  [Maps] API error: {data.get('status')} — {data.get('error_message', '')}")
                break

            places = data.get("results", [])
            if not places:
                break

            for place in places:
                if len(results) >= limit:
                    break

                # Get full details including website and phone
                detail = get_place_details(place["place_id"])
                if detail:
                    results.append(detail)

            next_page = data.get("next_page_token")
            if not next_page:
                break

        except Exception as e:
            print(f"  [Maps] Request error: {e}")
            break

    print(f"  [Maps] Found {len(results)} places for '{query}'")
    return results


def get_place_details(place_id: str) -> dict | None:
    """
    Fetches full details for a place including website, phone, address.
    Returns a clean dict or None if no website found.
    """
    if not GOOGLE_MAPS_API_KEY:
        return None

    endpoint = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields":   "name,website,formatted_phone_number,formatted_address,url,rating,user_ratings_total",
        "key":      GOOGLE_MAPS_API_KEY,
    }

    try:
        resp = requests.get(endpoint, params=params, timeout=10)
        data = resp.json()

        if data.get("status") != "OK":
            return None

        result = data.get("result", {})
        website = result.get("website", "")

        # Skip if no website or it's a directory
        if not website or _is_directory(website):
            return None

        # Clean the website URL
        if not website.startswith("http"):
            website = "https://" + website

        return {
            "name":    result.get("name", ""),
            "website": website,
            "phone":   result.get("formatted_phone_number", ""),
            "address": result.get("formatted_address", ""),
            "maps_url":result.get("url", ""),
            "rating":  result.get("rating", 0),
            "reviews": result.get("user_ratings_total", 0),
        }

    except Exception as e:
        print(f"  [Maps] Detail fetch error for {place_id}: {e}")
        return None


# ── CONTACT PAGE DISCOVERY (mirrors find_leads.py) ───────────────────────────

def get_contact_page(website: str) -> str:
    """
    Tries to find the contact page URL for a business website.
    Mirrors the get_contact_page logic from find_leads.py.
    """
    common_paths = [
        "/contact", "/contact-us", "/about", "/about-us",
        "/reach-us", "/get-in-touch", "/connect",
    ]

    base = website.rstrip("/")

    for path in common_paths:
        url = base + path
        try:
            resp = requests.head(url, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                return url
        except:
            continue

    return website  # fallback to homepage


# ── SUPABASE UPSERT (matches find_leads.py exactly) ──────────────────────────

def upsert_to_supabase(lead: dict) -> bool:
    """
    Upserts a lead to Supabase leads table.
    Writes exactly the same columns as find_leads.py.
    Uses website as the unique key (same as original).
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False

    endpoint = f"{SUPABASE_URL}/rest/v1/leads"
    headers = {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "resolution=merge-duplicates",
    }

    try:
        resp = requests.post(endpoint, json=lead, headers=headers, timeout=15)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"  [DB] Upsert failed for {lead.get('website')}: {e}")
        return False


def save_to_csv(lead: dict):
    """CSV fallback when Supabase is unavailable."""
    import csv
    file_exists = os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=lead.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(lead)


# ── CORE LEAD PROCESSOR (matches find_leads.py post-scrape workflow) ──────────

def process_lead(place: dict, niche: str, city: str, dry_run: bool = False) -> bool:
    """
    Full post-discovery pipeline — mirrors find_leads.py exactly:
    1. Find contact page
    2. Analyze site (Diamond's Technical Audit)
    3. Calculate opportunity score + revenue loss
    4. Generate AI roast if score >= 40
    5. Upsert to Supabase

    Returns True if lead was successfully saved.
    """
    website = place.get("website", "")
    name    = place.get("name", "")

    if not website:
        return False

    print(f"\n  [Diamond] Processing: {name} — {website}")

    # Step 1: Contact page discovery
    contact_url = get_contact_page(website)

    # Step 2: Site analysis
    try:
        site_data = analyze_site(website)
    except Exception as e:
        print(f"  [Diamond] analyze_site failed: {e}")
        site_data = {}

    # Step 3: Scoring
    try:
        opportunity_score = calculate_opportunity_score(site_data, niche=niche)
        revenue_loss = calculate_revenue_loss(niche, site_data)

        # Extract individual scores for the DB record
        mobile_score = 100 if site_data.get("mobile_friendly") else 0
        speed_score  = site_data.get("page_speed_score", 0)
        seo_score    = site_data.get("seo_score", 0)

    except Exception as e:
        print(f"  [Diamond] Scoring failed: {e}")
        opportunity_score = 0
        revenue_loss      = 0

    # Step 4: AI Roast (only if score >= 40 — same threshold as find_leads.py)
    website_roast = ""
    if opportunity_score >= 40:
        try:
            website_roast = generate_ai_audit(website, site_data, niche=niche)
        except Exception as e:
            print(f"  [Diamond] AI roast failed: {e}")

    # Step 5: Build lead record (same columns as find_leads.py)
    status = "High Intel Ready" if opportunity_score >= 75 else "New"

    lead = {
        "website":          website,
        "contact_url":      contact_url,
        "niche":            niche,
        "city":             city,
        "opportunity_score":opportunity_score,
        "website_score":    opportunity_score,  # legacy sync
        "mobile_score":     mobile_score,
        "speed_score":      speed_score,
        "seo_score":        seo_score,
        "website_roast":    website_roast,
        "revenue_loss":     revenue_loss,
        "status":           status,
        # Bonus fields from Google Maps (not in find_leads.py — extra intel)
        "business_name":    name,
        "phone":            place.get("phone", ""),
    }

    if dry_run:
        print(f"  [DRY RUN] Would save: {name} | Score: {opportunity_score} | ${revenue_loss:,}/mo")
        return True

    # Save to Supabase
    saved = upsert_to_supabase(lead)
    if not saved:
        save_to_csv(lead)
        print(f"  [CSV] Saved to {OUTPUT_FILE} (Supabase unavailable)")
    else:
        whale = "[WHALE]" if opportunity_score >= 75 else ""
        print(f"  [+] Saved: {name} | Score: {opportunity_score} | ${revenue_loss:,}/mo {whale}")

    return saved


# ── FALLBACK TO find_leads.py ─────────────────────────────────────────────────

def fallback_to_duckduckgo(niche: str, city: str, limit: int):
    """
    If Google Maps returns zero results for a niche/city combo,
    falls back to the original find_leads.py DuckDuckGo scraper.
    Ensures zero leads are missed.
    """
    print(f"  [Fallback] Google Maps found nothing for '{niche}' in '{city}'")
    print(f"  [Fallback] Triggering find_leads.py for this combo...")
    try:
        import subprocess
        import sys
        subprocess.run(
            [sys.executable, "find_leads.py",
             "--niche", niche,
             "--city", city,
             "--limit", str(limit)],
            timeout=300,
        )
    except Exception as e:
        print(f"  [Fallback] find_leads.py failed: {e}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def run(niche: str, city: str, limit: int = 20, dry_run: bool = False):
    """
    Main execution for a single niche + city combination.
    Mirrors find_leads.py --niche --city --limit interface exactly.
    """
    print(f"\n{'='*55}")
    print(f"  [Diamond Maps] {niche.upper()} — {city}")
    print(f"  Limit: {limit} | Dry Run: {dry_run}")
    print(f"{'='*55}")

    # Search Google Maps
    places = search_places(niche, city, limit)

    if not places:
        # Fallback to DuckDuckGo if Maps returns nothing
        fallback_to_duckduckgo(niche, city, limit)
        return

    saved_count = 0
    for place in places:
        success = process_lead(place, niche, city, dry_run)
        if success:
            saved_count += 1
        # Respectful delay between leads
        time.sleep(random.uniform(1.5, 3.0))

    print(f"\n  [Done] {saved_count}/{len(places)} leads saved for {niche} in {city}")


def run_mass_sweep(limit_per_combo: int = 20, dry_run: bool = False):
    """
    Industrial mass sweep — iterates through all NICHES × CITIES
    from config.py. Same behaviour as running find_leads.py with no args.
    """
    total = len(NICHES) * len(CITIES)
    done  = 0

    print(f"\n[Diamond Maps] Mass Sweep Starting")
    print(f"  {len(NICHES)} niches × {len(CITIES)} cities = {total} combinations")
    print(f"  Limit per combo: {limit_per_combo}\n")

    for niche in NICHES:
        for city in CITIES:
            done += 1
            print(f"\n[{done}/{total}] Processing: {niche} — {city}")
            run(niche, city, limit_per_combo, dry_run)
            # Delay between combos to respect API rate limits
            time.sleep(random.uniform(2.0, 4.0))

    print(f"\n[Diamond Maps] Mass Sweep Complete — {total} combinations processed")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Diamond Maps — Google Places lead scraper for RI2CH Agency OS"
    )
    parser.add_argument("--niche",   type=str, help="Business niche to search")
    parser.add_argument("--city",    type=str, help="Target city")
    parser.add_argument("--limit",   type=int, default=20, help="Max leads per combo")
    parser.add_argument("--dry-run", action="store_true", help="Find leads but don't save")
    args = parser.parse_args()

    if args.niche and args.city:
        # Targeted hunt
        run(args.niche, args.city, args.limit, args.dry_run)
    else:
        # Mass industrial sweep
        run_mass_sweep(args.limit, args.dry_run)
