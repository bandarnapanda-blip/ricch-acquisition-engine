import os
import sys
import json
import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Add project root to path
sys.path.append('.')

from analyzer import analyze_site, generate_ai_audit, calculate_opportunity_score, calculate_revenue_loss
from find_leads import push_log, upsert_to_supabase

load_dotenv()

LEADS_DATA = {
    "Solar Energy Installers": {
        "Austin": [
            "https://180energy.net", "https://512solar.com", "https://albaenergy.com", "https://atma-energy.com",
            "https://goatxsolar.com", "https://awakesolar.com", "https://axis-solar.com", "https://axiumsolar.com",
            "https://bigsunsolar.com", "https://bluepawenergy.com", "https://www.boostelectric.tech/",
            "https://centraltexas.solar/", "https://www.centrica.com/", "https://chargeprotexas.com/",
            "https://www.cosmosolaris.com", "https://www.cronasolar.com/", "https://crsolar.com/",
            "https://www.solardawntodusk.com/", "https://mydividedsky.com/", "http://www.dkdenergy.com"
        ]
    },
    "Roofing Companies": {
        "Dallas": [
            "https://newviewroofing.com", "https://arringtonroofing.com", "https://alliedroofingtexas.com",
            "https://boldroofing.com", "https://bertroofing.com", "https://roofsdallas.com", "https://rockmoorroofing.com",
            "https://needhamroofing.com", "https://bluehammerroofing.com", "https://ecostar-remodeling.com",
            "https://daltexroofing.com", "https://scottexteriors.com", "https://paradigmroofs.com",
            "https://hprestoration.com", "https://peakroofingconstruction.com", "https://rowleyroofing.com",
            "https://stonemyersroofing.com", "https://kiddroofing.com", "https://eliteroofingandconstruction.com",
            "https://starrroofing.net"
        ]
    },
    "Pool Builders": {
        "Phoenix": [
            "https://www.dolphinpools.us/", "https://sunstatepools.com/", "https://phoenixpoolbuilders.net/",
            "https://rondopools.com/", "https://azvalleypools.com/", "https://thunderbirdpools.com/",
            "https://www.splashpoolsaz.com/", "https://oasisofthevalley.com/", "https://www.presidentialpools.com/",
            "https://www.shastapools.com/"
        ]
    }
}

def audit_single_lead(url, niche, city):
    print(f"  Probing {url}...")
    try:
        audit = analyze_site(url)
        if audit:
            opp_score = calculate_opportunity_score(audit, niche=niche)
            lead = {
                "website": url,
                "niche": niche,
                "city": city,
                "opportunity_score": opp_score,
                "mobile_score": 100 if audit.get("mobile_friendly") else 0,
                "speed_score": audit.get("page_speed_score", 0),
                "seo_score": audit.get("seo_score", 0),
                "revenue_loss": calculate_revenue_loss(niche, audit),
                "status": "Ready"
            }
            if opp_score >= 40:
                lead["website_roast"] = generate_ai_audit(url, audit, niche=niche)
                lead["status"] = "High Intel Ready"
            
            # Upsert IMMEDIATELY for resilience
            upsert_to_supabase([lead])
            return lead
    except Exception as e:
        print(f"    [ERROR] Failed to audit {url}: {e}")
    return None

def audit_bootstrapped():
    print("--- LIVE PER-LEAD BOOTSTRAP AUDIT START ---")
    all_leads_to_audit = []
    for niche, cities in LEADS_DATA.items():
        for city, urls in cities.items():
            for url in urls:
                all_leads_to_audit.append((url, niche, city))
    
    with ThreadPoolExecutor(max_workers=5) as executor: # Reduced workers to avoid Supabase rate limits
        futures = {executor.submit(audit_single_lead, url, niche, city): url for url, niche, city in all_leads_to_audit}
        for future in as_completed(futures):
            res = future.result()
            if res:
                print(f"    -> Audited & Upserted {res['website']} (Score: {res['opportunity_score']})")

if __name__ == "__main__":
    audit_bootstrapped()
