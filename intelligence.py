import os
import re
import json
import time
import logging
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

import requests
from bs4 import BeautifulSoup
import tldextract
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG & WEIGHTS ---
WEIGHTS = {
    "financial": 0.30,
    "website": 0.20,
    "seo": 0.15,
    "growth": 0.15,
    "social": 0.10,
    "engagement": 0.10,
}

logger = logging.getLogger("intelligence")

@dataclass
class LeadSignals:
    url: str
    domain: str
    
    # Financial signals
    google_ads: bool = False
    meta_pixel: bool = False
    tiktok_pixel: bool = False
    
    # Website signals
    has_viewport: bool = False
    slow_load_estimate: Optional[float] = None
    outdated_theme: bool = False
    insecure: bool = False
    
    # SEO / Growth signals
    missing_schema: bool = False
    multiple_locations: int = 0
    hiring_detected: bool = False
    
    # Scores
    financial_score: float = 0.0
    website_score: float = 0.0
    seo_score: float = 0.0
    growth_score: float = 0.0
    deal_score: float = 0.0

def detect_ad_pixels(html: str) -> Dict[str, bool]:
    out = {"google_ads": False, "meta_pixel": False, "tiktok_pixel": False}
    if not html: return out
    low = html.lower()
    if "googletagmanager" in low or "gtag(" in low or "adsbygoogle" in low: out["google_ads"] = True
    if "facebook.com/tr/" in low or "fbq(" in low: out["meta_pixel"] = True
    if "analytics.tiktok" in low or "ttq(" in low: out["tiktok_pixel"] = True
    return out

def detect_multiple_locations(html: str) -> int:
    if not html: return 0
    low = html.lower()
    # Simple city-state pattern hunt
    matches = re.findall(r"\b[a-z]+,\s*[a-z]{2}\b", low)
    unique_cities = set(matches)
    return len(unique_cities)

def compute_deal_score(signals: LeadSignals) -> float:
    # Financial Score (0-100)
    fs = 0
    if signals.google_ads: fs += 50
    if signals.meta_pixel: fs += 30
    if signals.tiktok_pixel: fs += 20
    signals.financial_score = float(fs)

    # Website Score (0-100) - Higher = Worse site = Higher opportunity
    ws = 0
    if signals.slow_load_estimate is not None and signals.slow_load_estimate > 4.0: ws += 40
    if signals.outdated_theme: ws += 30
    if not signals.has_viewport: ws += 30
    signals.website_score = float(ws)

    # SEO & Growth (0-100)
    ss = 30 if signals.missing_schema else 0
    gs = min(100, signals.multiple_locations * 20 + (30 if signals.hiring_detected else 0))
    
    signals.seo_score = float(ss)
    signals.growth_score = float(gs)

    # Weighted Sum
    total = (
        signals.financial_score * WEIGHTS["financial"] +
        signals.website_score * WEIGHTS["website"] +
        signals.seo_score * WEIGHTS["seo"] +
        signals.growth_score * WEIGHTS["growth"]
    )
    
    signals.deal_score = float(round(float(total), 2))
    return signals.deal_score

def analyze_lead_intelligence(url: str, html: Optional[str] = None) -> LeadSignals:
    """Core entry point for lead intelligence analysis."""
    domain = tldextract.extract(url).registered_domain or url
    
    # If HTML not provided, try a quick fetch
    if not html:
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            html = r.text
        except:
            html = ""

    signals = LeadSignals(url=url, domain=domain)
    
    # Detect Ad Pixels
    ads = detect_ad_pixels(html)
    signals.google_ads = ads["google_ads"]
    signals.meta_pixel = ads["meta_pixel"]
    signals.tiktok_pixel = ads["tiktok_pixel"]
    
    # Website Quality
    soup = BeautifulSoup(html, "html.parser")
    signals.has_viewport = bool(soup.find("meta", attrs={"name": "viewport"}))
    signals.missing_schema = not bool(soup.find("script", type="application/ld+json"))
    signals.insecure = not url.startswith("https://")
    
    # Outdated UI hints
    low = html.lower()
    if "<font" in low or "wordpress" in low and "wp-content/themes" in low:
        signals.outdated_theme = True
        
    # Locations
    signals.multiple_locations = detect_multiple_locations(html)
    
    # Compute Score
    compute_deal_score(signals)
    
    return signals

def get_outreach_recommendation(deal_score: float) -> str:
    if deal_score >= 90: return "DIAMOND: Digital Twin + Revenue Simulation"
    if deal_score >= 70: return "GOLD: Mini Redesign + Micro Report"
    if deal_score >= 50: return "SILVER: Nurture & SEO Audit"
    return "IGNORE: Low Probability"
