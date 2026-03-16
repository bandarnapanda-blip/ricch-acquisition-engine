# Save as antigravity_deal_score.py
# (Full expanded module — SERP checks, hiring signals, Streamlit app, retraining)

from __future__ import annotations
import os
import re
import json
import time
import logging
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import pathlib
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import tldextract
from dotenv import load_dotenv

# optional imports
try:
    from supabase import create_client
except Exception:
    create_client = None

try:
    from serpapi import GoogleSearch
except Exception:
    GoogleSearch = None

# sklearn for retraining
try:
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import roc_auc_score
except Exception:
    pd = None

# Playwright optional
PLAYWRIGHT_AVAILABLE = False
if os.getenv("PLAYWRIGHT_ENABLED") == "1":
    try:
        from playwright.sync_api import sync_playwright
        PLAYWRIGHT_AVAILABLE = True
    except Exception:
        PLAYWRIGHT_AVAILABLE = False

load_dotenv()

# ---------------------------
# Config
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("antigravity_deal_score")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

class SerpKeyManager:
    """Manages rotation of multiple SerpAPI keys to maximize free tier usage."""
    def __init__(self):
        self.keys: List[str] = []
        env_keys = os.getenv("SERPAPI_KEYS", "")
        if env_keys:
            self.keys = [k.strip() for k in env_keys.split(",") if k.strip()]
        elif (sk := os.getenv("SERPAPI_KEY")):
            self.keys = [sk]
        
        self.current_index = 0
        self.exhausted_keys = set()
        if self.keys:
            logger.info(f"SerpKeyManager: Localized {len(self.keys)} rotation keys.")

    def get_key(self) -> Optional[str]:
        if not self.keys:
            return None
        start_idx = self.current_index
        while True:
            k = self.keys[self.current_index]
            if k not in self.exhausted_keys:
                return k
            self.current_index = (self.current_index + 1) % len(self.keys)
            if self.current_index == start_idx:
                return None # All keys exhausted

    def mark_exhausted(self, key: str):
        if key in self.keys:
            self.exhausted_keys.add(key)
            logger.warning(f"SerpAPI Key exhausted: {key[:8]}... Moving to spare.")
            self.current_index = (self.current_index + 1) % len(self.keys)

serp_manager = SerpKeyManager()

WEIGHTS = {
    "financial": 0.30,
    "website": 0.20,
    "seo": 0.15,
    "growth": 0.15,
    "social": 0.10,
    "engagement": 0.10,
}

# folder for local previews
LOCAL_PREVIEW_DIR = pathlib.Path("digital_twins")
LOCAL_PREVIEW_DIR.mkdir(exist_ok=True)

# Supabase REST Wrapper (Hardened)
try:
    from database import db as supabase
except Exception as e:
    logger.warning(f"Supabase (REST) initialization failed: {e}. DB writes may skip.")
    supabase = None

# ---------------------------
# Data structures
# ---------------------------
@dataclass
class LeadSignals:
    url: str
    domain: str
    html_snippet: Optional[str] = None

    # financial
    google_ads: bool = False
    meta_pixel: bool = False
    tiktok_pixel: bool = False
    ecommerce_platform: Optional[str] = None

    # website
    mobile_viewport: bool = False
    has_viewport_meta: bool = False
    slow_load_estimate: Optional[float] = None
    insecure: bool = False
    outdated_theme_hint: bool = False

    # seo
    missing_schema: bool = True
    title_length: Optional[int] = None
    description_length: Optional[int] = None
    serp_rank: Optional[int] = None
    serp_keyword: Optional[str] = None

    # growth
    multiple_locations: int = 0
    hiring_detected: bool = False
    recent_news_detected: bool = False

    # social
    instagram_activity: Optional[int] = None
    facebook_activity: Optional[int] = None
    reviews_count: Optional[int] = None

    # scores
    financial_score: float = 0.0
    website_score: float = 0.0
    seo_score: float = 0.0
    growth_score: float = 0.0
    social_score: float = 0.0
    engagement_score: float = 0.0
    deal_score: float = 0.0

    raw: Optional[Dict[str, Any]] = None

# ---------------------------
# Helpers
# ---------------------------
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
REQUEST_HEADERS = {"User-Agent": USER_AGENT}

def fetch_html(url: str, timeout: int = 12, render: bool = False) -> Optional[str]:
    try:
        if render and PLAYWRIGHT_AVAILABLE:
            logger.debug(f"Rendering via Playwright: {url}")
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent=USER_AGENT)
                page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
                html = page.content()
                browser.close()
                return html
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.warning(f"fetch_html failed for {url}: {e}")
        return None

def detect_ad_pixels(html: str) -> Dict[str, bool]:
    out = {"google_ads": False, "meta_pixel": False, "tiktok_pixel": False}
    if not html:
        return out
    lowered = html.lower()
    if "googletagmanager" in lowered or "gtag(" in lowered or "adsbygoogle" in lowered or "googlesyndication" in lowered:
        out["google_ads"] = True
    if "facebook.com/tr/" in lowered or "fbq(" in lowered or "pixel.facebook.com" in lowered:
        out["meta_pixel"] = True
    if "analytics.tiktok" in lowered or "tiktok.com/i18n" in lowered or "ttq(" in lowered or "ttq('" in lowered:
        out["tiktok_pixel"] = True
    return out

def detect_mobile_and_viewport(html: str) -> Dict[str, Any]:
    if not html:
        return {"has_viewport": False, "has_meta_viewport": False}
    soup = BeautifulSoup(html, "html.parser")
    viewport = soup.find("meta", attrs={"name": "viewport"})
    has_meta = bool(viewport)
    css_text = " ".join([t.get_text(separator=" ") for t in soup.find_all("style")])
    has_responsive_css = "@media" in css_text or "max-width" in css_text or "flex" in css_text
    return {"has_viewport": has_responsive_css, "has_meta_viewport": has_meta}

def detect_outdated_design(html: str) -> bool:
    if not html:
        return False
    lowered = html.lower()
    if "wordpress" in lowered and ("wp-content/themes/" in lowered or "wp-includes" in lowered):
        return True
    if "<table" in lowered and "<div" not in lowered[:5000]:
        return True
    if "<font" in lowered:
        return True
    return False

def detect_multiple_locations(html: str, url: str) -> int:
    count = 0
    if not html:
        return 0
    lowered = html.lower()
    if "/locations" in lowered or "our locations" in lowered or "locations" in lowered:
        matches = re.findall(r"\b[a-z]+,\s*[a-z]{2}\b", lowered)
        count = max(1, len(set(matches)))
    address_matches = re.findall(r"\baddress\b", lowered)
    if address_matches:
        count = max(count, len(address_matches))
    phones = re.findall(r"\(\d{3}\)\s*\d{3}[-\.\s]\d{4}", lowered)
    if phones:
        count = max(count, len(set(phones)))
    return count

def detect_seo_signals(html: str) -> Dict[str, Any]:
    if not html:
        return {"missing_schema": True, "title_length": None, "description_length": None}
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    desc = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else ""
    schema = bool(soup.find_all(attrs={"itemtype": True}) or soup.find("script", type="application/ld+json"))
    return {"missing_schema": not schema, "title_length": len(title), "description_length": len(desc)}

# ---------------------------
# SERP rank check (SerpAPI)
# ---------------------------
def serpapi_check_rank(domain: str, keyword: str, gl: str = "us") -> Optional[int]:
    """Check SERP rank with automatic key rotation on quota exhaustion."""
    if not GoogleSearch:
        logger.info("SerpAPI package missing; skipping SERP rank check")
        return None
        
    while True:
        key = serp_manager.get_key()
        if not key:
            logger.warning("All SerpAPI keys exhausted or none configured.")
            return None
            
        params = {"engine": "google", "q": keyword, "hl": "en", "gl": gl, "num": 100, "api_key": key}
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "error" in results:
                err = results["error"].lower()
                if any(x in err for x in ["quota", "limit", "plan", "credits"]):
                    serp_manager.mark_exhausted(key)
                    continue
                else:
                    logger.warning(f"SerpAPI returned error: {results['error']}")
                    return None
            
            organic = results.get("organic_results", [])
            for idx, r in enumerate(organic, start=1):
                link = r.get("link") or r.get("displayed_link") or r.get("serpapi_link")
                if link and domain in link:
                    return idx
            return None
        except Exception as e:
            logger.warning(f"serpapi_check_rank failed: {e}")
            return None

# ---------------------------
# Hiring signals: Indeed + LinkedIn fallback
# ---------------------------
def indeed_hiring_signal(company_name: str, location: Optional[str] = None) -> bool:
    query = f"https://www.indeed.com/jobs?q={requests.utils.quote(company_name)}"
    if location:
        query += f"&l={requests.utils.quote(location)}"
    try:
        r = requests.get(query, headers=REQUEST_HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        count = soup.find("div", attrs={"id": "searchCountPages"})
        if count and re.search(r"\d+", count.get_text()):
            return True
        jobs = soup.find_all("a", attrs={"data-hide-spinner": True})
        return len(jobs) > 0
    except Exception as e:
        logger.warning(f"indeed_hiring_signal failed for {company_name}: {e}")
        return False

def linkedin_hiring_signal_via_serp(company_name: str) -> bool:
    """Detect hiring signals via SerpAPI with key rotation."""
    if not GoogleSearch:
        logger.info("SerpAPI not available for LinkedIn check; skipping")
        return False
        
    while True:
        key = serp_manager.get_key()
        if not key:
            return False
            
        q = f"{company_name} site:linkedin.com/jobs OR site:linkedin.com/company"
        params = {"engine": "google", "q": q, "num": 10, "api_key": key}
        try:
            search = GoogleSearch(params)
            res = search.get_dict()
            
            if "error" in res:
                err = res["error"].lower()
                if any(x in err for x in ["quota", "limit", "plan", "credits"]):
                    serp_manager.mark_exhausted(key)
                    continue
                return False
                
            organic = res.get("organic_results", [])
            return len(organic) > 0
        except Exception as e:
            logger.warning(f"linkedin_hiring_signal_via_serp failed: {e}")
            return False
    return False

# ---------------------------
# Scoring
# ---------------------------
def score_financial(signals: LeadSignals) -> float:
    score = 0
    if signals.google_ads:
        score += 50
    if signals.meta_pixel:
        score += 30
    if signals.tiktok_pixel:
        score += 20
    if signals.ecommerce_platform:
        score += 20
    return min(100.0, score)

def score_website(signals: LeadSignals) -> float:
    score = 0
    if signals.slow_load_estimate is not None and signals.slow_load_estimate > 4.0:
        score += 40
    if signals.outdated_theme_hint:
        score += 25
    if not signals.has_viewport_meta:
        score += 20
    if signals.insecure:
        score += 15
    return min(100.0, score)

def score_seo(signals: LeadSignals) -> float:
    score = 0
    if signals.missing_schema:
        score += 30
    if signals.title_length is not None and (signals.title_length < 10 or signals.title_length > 120):
        score += 20
    if signals.description_length is not None and (signals.description_length < 70 or signals.description_length > 320):
        score += 20
    if signals.serp_rank and isinstance(signals.serp_rank, int):
        if signals.serp_rank > 10:
            score += 30
        elif signals.serp_rank > 3:
            score += 10
    return min(100.0, score)

def score_growth(signals: LeadSignals) -> float:
    score = 0
    if signals.multiple_locations and signals.multiple_locations > 1:
        score += 40
    if signals.hiring_detected:
        score += 30
    if signals.recent_news_detected:
        score += 30
    return min(100.0, score)

def score_social(signals: LeadSignals) -> float:
    score = 0
    if signals.instagram_activity and signals.instagram_activity > 10:
        score += 40
    if signals.reviews_count and signals.reviews_count > 10:
        score += 30
    return min(100.0, score)

def score_engagement(signals: LeadSignals) -> float:
    return float(signals.engagement_score if signals.engagement_score else 0)

def compute_deal_score(signals: LeadSignals) -> float:
    signals.financial_score = score_financial(signals)
    signals.website_score = score_website(signals)
    signals.seo_score = score_seo(signals)
    signals.growth_score = score_growth(signals)
    signals.social_score = score_social(signals)
    signals.engagement_score = score_engagement(signals)

    score = (
        signals.financial_score * WEIGHTS["financial"]
        + signals.website_score * WEIGHTS["website"]
        + signals.seo_score * WEIGHTS["seo"]
        + signals.growth_score * WEIGHTS["growth"]
        + signals.social_score * WEIGHTS["social"]
        + signals.engagement_score * WEIGHTS["engagement"]
    )
    signals.deal_score = float(round(score, 2))
    return signals.deal_score

# ---------------------------
# DB write
# ---------------------------
def push_to_supabase(signals: LeadSignals) -> Optional[Dict[str, Any]]:
    if not supabase:
        logger.info("Supabase client not configured. Skipping DB write.")
        return None
    try:
        payload = {
            "domain": signals.domain,
            "url": signals.url,
            "deal_score": signals.deal_score,
            "signals": json.dumps(asdict(signals)),
            "tags": [recommend_outreach_action(signals)],
        }
        resp = supabase.table("leads").upsert(payload, on_conflict=["domain"]).execute()
        logger.info(f"Upserted lead {signals.domain} with score {signals.deal_score}")
        return resp
    except Exception as e:
        logger.warning(f"push_to_supabase failed: {e}")
        return None

def recommend_outreach_action(signals: LeadSignals) -> str:
    s = signals.deal_score
    if s >= 90:
        return "digital_twin_revenue_simulation"
    if 70 <= s < 90:
        return "mini_redesign_plus_report"
    if 50 <= s < 70:
        return "nurture/retarget"
    return "ignore"

# ---------------------------
# Phase 17 Preview: Local Digital Twin generator
# ---------------------------
def generate_preview_html(signals: LeadSignals) -> str:
    """Modern HTML preview for Digital Twin."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Digital Twin Preview - {signals.domain}</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Outfit', sans-serif; background: #0a0a0c; color: white; padding: 40px; line-height: 1.6; margin: 0; }}
            .card {{ background: #141417; padding: 40px; border-radius: 20px; max-width: 800px; margin: auto; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
            h1 {{ font-size: 2rem; font-weight: 900; margin-bottom: 20px; color: #ff4d94; text-transform: uppercase; }}
            .score-box {{ font-size: 3rem; font-weight: 900; background: rgba(255, 77, 148, 0.1); padding: 20px; border-radius: 15px; display: inline-block; margin: 20px 0; }}
            pre {{ background: #000; padding: 20px; border-radius: 10px; overflow-x: auto; color: #0f0; font-family: 'Courier New', monospace; font-size: 0.9rem; }}
            .action-btn {{ background: #ff4d94; color: white; padding: 15px 30px; border-radius: 50px; text-decoration: none; font-weight: 900; display: inline-block; margin-top: 30px; transition: transform 0.3s; }}
            .action-btn:hover {{ transform: scale(1.05); }}
            footer {{ text-align: center; margin-top: 30px; font-size: 0.85rem; color: #666; opacity: 0.5; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Digital Twin Preview: {signals.domain}</h1>
            <div class="score-box">DEAL SCORE: {signals.deal_score}</div>
            <p><b>Recommended Strategy:</b> {recommend_outreach_action(signals).replace('_', ' ').title()}</p>
            <hr style="opacity: 0.1; margin: 30px 0;">
            <h3>Intelligence Audit Stream</h3>
            <pre>{json.dumps(asdict(signals), indent=2)}</pre>
            <div style="text-align: center;">
                <a href="mailto:ri2ch.digital@gmail.com?subject=Digital Twin Strategy for {signals.domain}" class="action-btn">Initialize Full Digital Twin</a>
            </div>
            <footer>Generated at: {timestamp}</footer>
        </div>
    </body>
    </html>
    """
    return html

def save_preview_locally(signals: LeadSignals) -> str:
    """Save the HTML locally with timestamped filename."""
    safe_domain = re.sub(r"[^a-zA-Z0-9\-]", "-", signals.domain)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = LOCAL_PREVIEW_DIR / f"{safe_domain}_{timestamp}.html"
    html_content = generate_preview_html(signals)
    filename.write_text(html_content, encoding="utf-8")
    logger.info(f"Saved digital twin preview locally: {filename}")
    return str(filename)

# ---------------------------
# Pipeline
# ---------------------------
def analyze_url(url: str, render: bool = False, use_pagespeed: bool = False, keywords: Optional[List[str]] = None) -> Optional[LeadSignals]:
    html = fetch_html(url, render=render)
    domain = tldextract.extract(url).registered_domain or url
    signals = LeadSignals(url=url, domain=domain, raw={})
    signals.insecure = not url.lower().startswith("https://")

    ad_signals = detect_ad_pixels(html or "")
    signals.google_ads = ad_signals.get("google_ads", False)
    signals.meta_pixel = ad_signals.get("meta_pixel", False)
    signals.tiktok_pixel = ad_signals.get("tiktok_pixel", False)

    mv = detect_mobile_and_viewport(html or "")
    signals.has_viewport_meta = mv.get("has_meta_viewport", False)

    signals.outdated_theme_hint = detect_outdated_design(html or "")
    signals.multiple_locations = detect_multiple_locations(html or "", url)

    seo = detect_seo_signals(html or "")
    signals.missing_schema = seo.get("missing_schema", True)
    signals.title_length = seo.get("title_length")
    signals.description_length = seo.get("description_length")

    if keywords and SERPAPI_KEY and GoogleSearch:
        for kw in keywords:
            rank = serpapi_check_rank(signals.domain, kw)
            if rank:
                signals.serp_rank = rank
                signals.serp_keyword = kw
                break

    if use_pagespeed and PAGESPEED_API_KEY:
        try:
            ps = pagespeed_insights(url)
            perf = ps.get("lighthouseResult", {}).get("audits", {})
            lcp = perf.get("largest-contentful-paint", {}).get("numericValue")
            if lcp:
                signals.slow_load_estimate = float(lcp) / 1000.0
        except Exception:
            # Fallback to simple timing
            try:
                start = time.time()
                r = requests.get(url, headers=REQUEST_HEADERS, timeout=8)
                r.raise_for_status()
                elapsed = time.time() - start
                signals.slow_load_estimate = round(elapsed, 2)
            except Exception:
                signals.slow_load_estimate = None
    else:
        try:
            start = time.time()
            r = requests.get(url, headers=REQUEST_HEADERS, timeout=8)
            r.raise_for_status()
            elapsed = time.time() - start
            signals.slow_load_estimate = round(elapsed, 2)
        except Exception:
            signals.slow_load_estimate = None

    signals.hiring_detected = False
    try:
        company = signals.domain.split(".")[0]
        if indeed_hiring_signal(company):
            signals.hiring_detected = True
        else:
            if linkedin_hiring_signal_via_serp(company):
                signals.hiring_detected = True
    except Exception:
        pass

    compute_deal_score(signals)
    
    # generate local digital twin preview for high-value leads
    if recommend_outreach_action(signals) == "digital_twin_revenue_simulation":
        preview_path = save_preview_locally(signals)
        current_raw = signals.raw or {}
        current_raw["digital_twin_path"] = preview_path
        current_raw["preview_link"] = f"[View Digital Twin]({preview_path})"
        signals.raw = current_raw

    push_to_supabase(signals)
    return signals

def process_urls(urls: List[str], render: bool = False, use_pagespeed: bool = False, keywords: Optional[List[str]] = None) -> List[LeadSignals]:
    out = []
    for url in urls:
        logger.info(f"Processing {url}")
        s = analyze_url(url, render=render, use_pagespeed=use_pagespeed, keywords=keywords)
        if s:
            action = recommend_outreach_action(s)
            logger.info(f"{s.domain}: deal_score={s.deal_score} action={action}")
            # Attach clickable preview link for Streamlit
            if s.raw is not None and "digital_twin_path" in s.raw:
                s.raw["preview_link"] = f"[View Digital Twin]({s.raw['digital_twin_path']})"
            out.append(s)
        time.sleep(0.35)
    return out

# ---------------------------
# PageSpeed helper
# ---------------------------
def pagespeed_insights(url: str, strategy: str = "mobile") -> Optional[Dict[str, Any]]:
    if not PAGESPEED_API_KEY:
        return None
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {"url": url, "key": PAGESPEED_API_KEY, "strategy": strategy}
    try:
        r = requests.get(endpoint, params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.warning(f"pagespeed_insights failed for {url}: {e}")
        return None

# ---------------------------
# Retraining / optimize weights
# ---------------------------
def optimize_weights_from_supabase(table_name: str = "leads", label_column: str = "converted") -> Optional[Dict[str, float]]:
    global WEIGHTS
    if not pd:
        logger.warning("pandas/sklearn not installed; cannot optimize weights")
        return None
    if not supabase:
        logger.warning("Supabase client not configured; cannot fetch historical data")
        return None
    try:
        resp = supabase.table(table_name).select("domain, deal_score, signals, " + label_column).execute()
        rows = resp.get("data") if isinstance(resp, dict) else getattr(resp, "data", None)
        if not rows:
            logger.info("No historical rows fetched for retraining")
            return None
        df_local = pd.json_normalize(rows)
        df_signals = df_local["signals"].apply(lambda s: json.loads(s) if isinstance(s, str) else s)
        features = pd.json_normalize(df_signals)
        X = features[[c for c in features.columns if c in [
            "financial_score", "website_score", "seo_score", "growth_score", "social_score", "engagement_score"]]].fillna(0)
        y = df_local[label_column].astype(int)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        clf = RandomForestClassifier(n_estimators=200, random_state=42)
        clf.fit(X_train, y_train)
        preds = clf.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, preds)
        logger.info(f"Retraining AUC: {auc:.3f}")
        importances = clf.feature_importances_
        feature_names = X.columns.tolist()
        total = sum(importances)
        new_weights = {}
        mapping = dict(zip(feature_names, importances))
        for k in WEIGHTS.keys():
            key_name = k + "_score"
            val = mapping.get(key_name, 0.0)
            new_weights[k] = float(val / total) if total > 0 else WEIGHTS[k]
        s = sum(new_weights.values())
        if s > 0:
            for k in new_weights:
                new_weights[k] = round(new_weights[k] / s, 4)
        logger.info(f"New weights: {new_weights}")
        WEIGHTS = new_weights
        return new_weights
    except Exception as e:
        logger.warning(f"optimize_weights_from_supabase failed: {e}")
        return None

# ---------------------------
# Phase 16: Revenue Engine & Competitor Benchmarking
# ---------------------------

NICHE_METRICS = {
    "epoxy_flooring": {"avg_ticket": 4500, "conversion_rate": 0.03},
    "roofing": {"avg_ticket": 12000, "conversion_rate": 0.02},
    "hvac": {"avg_ticket": 6500, "conversion_rate": 0.05},
    "lawyer": {"avg_ticket": 8000, "conversion_rate": 0.04},
    "dentist": {"avg_ticket": 3500, "conversion_rate": 0.06},
    "highticket_coaching": {"avg_ticket": 5000, "conversion_rate": 0.02},
    "default": {"avg_ticket": 5000, "conversion_rate": 0.03},
}

class RevenueSimulator:
    @staticmethod
    def calculate_leakage(signals: LeadSignals, niche: str = "default") -> Dict[str, Any]:
        metrics = NICHE_METRICS.get(niche.lower().replace(" ", "_"), NICHE_METRICS["default"])
        avg_ticket = metrics["avg_ticket"]
        base_conv = metrics["conversion_rate"]
        
        # Estimate monthly traffic based on SERP rank (very rough heuristic)
        # Rank 1-3: 1000+, 4-10: 500, 11-50: 100, 50+: 20
        rank = signals.serp_rank or 50
        est_traffic = 1000 if rank <= 3 else (500 if rank <= 10 else (100 if rank <= 50 else 20))
        
        # Penalty factors based on signals
        penalty = 0.0
        if signals.slow_load_estimate and signals.slow_load_estimate > 4:
            penalty += 0.40 # 40% bounce rate increase
        if not signals.has_viewport_meta:
            penalty += 0.30 # 30% loss of mobile users
        if signals.outdated_theme_hint:
            penalty += 0.20 # 20% trust loss
            
        current_conv = base_conv * (1 - penalty)
        potential_conv = base_conv * 1.5 # Assume 50% lift with our redesign
        
        current_rev = est_traffic * current_conv * avg_ticket
        potential_rev = est_traffic * potential_conv * avg_ticket
        monthly_leak = potential_rev - current_rev
        annual_leak = monthly_leak * 12
        
        return {
            "est_traffic": est_traffic,
            "current_conversion": round(current_conv * 100, 2),
            "potential_conversion": round(potential_conv * 100, 2),
            "monthly_leakage": round(monthly_leak, 2),
            "annual_leakage": round(annual_leak, 2),
            "avg_ticket": avg_ticket
        }

class CompetitorBenchmarker:
    @staticmethod
    def get_benchmark(domain: str, signals: LeadSignals) -> Dict[str, Any]:
        # In a real scenario, we'd audit the Top 3 for comparison.
        # Here we use "Gold Standard" stats.
        benchmarks = {
            "speed_target": 1.2,
            "mobile_standard": "100% Responsive",
            "ad_adoption": "High (Google/Meta Active)",
            "schema_check": "Verified"
        }
        
        comparison = {
            "speed": "PASSED" if (signals.slow_load_estimate or 10) < benchmarks["speed_target"] else "FAILED",
            "mobile": "PASSED" if signals.has_viewport_meta else "FAILED",
            "ads": "ENABLED" if signals.google_ads or signals.meta_pixel else "DISABLED",
            "schema": "FOUND" if not signals.missing_schema else "MISSING"
        }
        
        return {"benchmarks": benchmarks, "comparison": comparison}

def generate_authority_page_html(domain: str, url: str, signals: LeadSignals, niche: str = "default") -> str:
    simulator = RevenueSimulator()
    leakage = simulator.calculate_leakage(signals, niche)
    benchmarker = CompetitorBenchmarker()
    bench = benchmarker.get_benchmark(domain, signals)
    
    title = f"Exclusive Revenue-Leak Audit: {domain}"
    annual_leak_fmt = f"${leakage['annual_leakage']:,.0f}"
    
    html_template = f"""
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root {{ --accent: #ff4d94; --bg: #0a0a0c; --card: #141417; --text: #ffffff; }}
        body {{ font-family: 'Outfit', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; margin: 0; padding: 40px 20px; }}
        .header {{ text-align: center; margin-bottom: 60px; }}
        .leak-badge {{ font-size: 4rem; font-weight: 900; color: var(--accent); margin: 20px 0; text-shadow: 0 0 20px rgba(255, 77, 148, 0.4); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; max-width: 1200px; margin: 0 auto; }}
        .card {{ background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); }}
        .cta {{ background: var(--accent); color: white; padding: 20px 40px; border-radius: 50px; text-decoration: none; font-weight: 900; display: inline-block; margin-top: 40px; transition: transform 0.3s; }}
        .cta:hover {{ transform: scale(1.05); }}
        h1, h2, h3 {{ color: #fff; text-transform: uppercase; letter-spacing: 2px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Revenue Loss Analysis</h1>
        <h3>Confidential Report for {domain}</h3>
        <div class="leak-badge">{annual_leak_fmt}</div>
        <p>Estimated Annual Revenue Leaking due to Website Inefficiencies</p>
    </div>

    <div class="grid">
        <div class="card">
            <h2>Financial Upside</h2>
            <p>Conversion Rate could jump from <b>{leakage['current_conversion']}%</b> to <b>{leakage['potential_conversion']}%</b>.</p>
            <p>Average Ticket Value: <b>${leakage['avg_ticket']:,.0f}</b></p>
        </div>
        <div class="card">
            <h2>Competitor Gap</h2>
            <p>Mobile Standard: {bench['comparison']['mobile']}</p>
            <p>Speed Benchmark: {bench['comparison']['speed']}</p>
            <p>Ad Infrastructure: {bench['comparison']['ads']}</p>
        </div>
        <div class="card">
            <h2>Technical Audit</h2>
            <ul>
                <li>Page Load: {signals.slow_load_estimate or 'Unknown'}s</li>
                <li>SERP Keyword: {signals.serp_keyword or 'Unranked'}</li>
                <li>Hiring Growth: {'Yes' if signals.hiring_detected else 'No'}</li>
            </ul>
        </div>
    </div>

    <div style="text-align:center; margin-top:60px;">
        <a href="mailto:ri2ch.digital@gmail.com?subject=Strategic Redesign for {domain}" class="cta">Plug the Leak Now</a>
    </div>
</body>
</html>
"""
    return html_template

# ---------------------------
# Streamlit authority app
# ---------------------------
def run_streamlit_app():
    try:
        import streamlit as st
    except Exception:
        logger.warning("streamlit not installed. Install with `pip install streamlit` to run the app.")
        return

    st.set_page_config(page_title="Antigravity Authority Reports", layout="wide")
    st.title("Antigravity — Authority Reports")

    if not supabase:
        st.warning("Supabase not configured. Using local session data if available.")

    st.sidebar.title("Filters")
    min_score_filter = st.sidebar.slider("Min deal score", 0, 100, 70)
    
    # Fetch leads
    leads_list = []
    if supabase:
        try:
            q = supabase.table("leads").select("id, domain, url, deal_score, signals, tags").order("deal_score", desc=True)
            resp = q.execute()
            leads_list = resp.data if hasattr(resp, 'data') else []
        except Exception as e:
            st.error(f"Failed to fetch leads: {e}")

    if not leads_list:
        st.info("No leads found. Run the pipeline first.")
        return

    filtered = [r for r in leads_list if r.get("deal_score", 0) >= min_score_filter]

    st.write(f"### {len(filtered)} leads matching filters")
    for lead_row in filtered:
        lead_signals = lead_row.get("signals")
        s_raw = json.loads(lead_signals) if isinstance(lead_signals, str) else lead_signals
        l_domain = lead_row.get("domain")
        l_url = lead_row.get("url")
        l_score = lead_row.get("deal_score")
        
        # Hydrate LeadSignals for internal functions
        ls_obj = LeadSignals(url=l_url, domain=l_domain)
        for key, val in s_raw.items():
            if hasattr(ls_obj, key):
                setattr(ls_obj, key, val)
        
        cols = st.columns([1, 2, 2])
        with cols[0]:
            st.markdown(f"**{l_domain}**\n\nscore: **{l_score}**")
            if st.button(f"Analyze Leakage {l_domain}", key=f"open_{l_domain}"):
                st.session_state["active_lead"] = l_domain
        with cols[1]:
            st.markdown("**Core Intelligence**")
            st.write({
                "Ads": "Detected" if s_raw.get("google_ads") or s_raw.get("meta_pixel") else "None",
                "Speed": f"{s_raw.get('slow_load_estimate')}s",
                "Rank": s_raw.get("serp_rank") or "N/A",
            })
        with cols[2]:
            st.markdown("**Phase 16 Actions**")
            if s_raw and "preview_link" in s_raw:
                st.markdown(s_raw["preview_link"], unsafe_allow_html=True)
                if s_raw.get("digital_twin_path"):
                    try:
                        with open(s_raw["digital_twin_path"], "r", encoding="utf-8") as f:
                            st.components.v1.html(f.read(), height=300, scrolling=True)
                    except Exception:
                        pass
            if st.button(f"Generate Revenue Leak Report", key=f"gen_{l_domain}"):
                page_html = generate_authority_page_html(l_domain, l_url, ls_obj)
                st.markdown("### Preview Generated")
                st.code(page_html[:1000] + "...")
                st.download_button("Download Authority Page (.html)", page_html, file_name=f"{l_domain}_audit.html")

    if "active_lead" in st.session_state:
        l_domain = st.session_state["active_lead"]
        chosen = next((x for x in leads_list if x.get("domain") == l_domain), None)
        if chosen:
            st.divider()
            st.header(f"Institutional Audit: {l_domain}")
            lead_s_raw = json.loads(chosen.get("signals")) if isinstance(chosen.get("signals"), str) else chosen.get("signals")
            
            ls_obj = LeadSignals(url=chosen.get('url'), domain=l_domain)
            for key, val in lead_s_raw.items():
                if hasattr(ls_obj, key):
                    setattr(ls_obj, key, val)
            
            sim = RevenueSimulator()
            leak = sim.calculate_leakage(ls_obj)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Monthly Revenue Leak", f"${leak['monthly_leakage']:,.2f}")
            c2.metric("Annual Recovery Potential", f"${leak['annual_leakage']:,.2f}")
            c3.metric("Conv. Lift Potential", f"+{round(leak['potential_conversion'] - leak['current_conversion'], 2)}%")

# CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Antigravity Deal Score pipeline + Streamlit app")
    parser.add_argument("--input", help="newline-delimited file with URLs", required=False)
    parser.add_argument("--render", action="store_true", help="use Playwright to render pages")
    parser.add_argument("--pagespeed", action="store_true", help="use Google PageSpeed Insights API")
    parser.add_argument("--keywords", help="comma-separated keywords to check SERP rank for", required=False)
    parser.add_argument("--app", action="store_true", help="run Streamlit app interface")
    args = parser.parse_args()

    if args.app:
        run_streamlit_app()
    else:
        if args.input:
            with open(args.input, "r", encoding="utf-8") as f:
                urls_list = [line.strip() for line in f if line.strip()]
        else:
            urls_list = ["https://example.com"]
        kws_list = args.keywords.split(",") if args.keywords else None
        results_list = process_urls(urls_list, render=args.render, use_pagespeed=args.pagespeed, keywords=kws_list)
        for rl in results_list:
            print(f"{rl.domain}: {rl.deal_score} -> {recommend_outreach_action(rl)}")
