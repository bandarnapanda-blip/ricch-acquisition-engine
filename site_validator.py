"""
================================================================================
  RI2CH AGENCY OS — VEX: ZERO-404 SITE VALIDATOR
  FILE: site_validator.py
  DROP IN: Your Antigravity root folder (same level as generate_landing.py)
  AGENT:   Vex (Technical QA Inspector) — Division 4
================================================================================
"""

import re
import time
import base64
import logging
import os
import requests
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger("vex")
logging.basicConfig(level=logging.INFO, format="[Vex] %(message)s")


# ─── CONFIG ───────────────────────────────────────────────────────────────────

NETLIFY_POLL_INTERVALS = [3, 5, 5, 5, 5, 5, 5, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
GITHUB_POLL_INTERVALS  = [5, 8, 8, 8, 8, 10, 10, 10, 10, 10,
                           10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
                           10, 10, 10, 10, 10, 10, 10, 10, 10, 10]

NETLIFY_FAKE_200 = [
    "Not found",
    "netlify-404",
    "Page Not Found",
    "No site found",
    "page-not-found",
]

MIN_REAL_BYTES = 5_000
MIN_UPLOAD_BYTES = 8_000   # Pre-flight threshold


# ─── RESULT ───────────────────────────────────────────────────────────────────

@dataclass
class DeployResult:
    success: bool
    url: Optional[str] = None
    channel: str = ""
    reason: str = ""
    warnings: list = field(default_factory=list)
    attempts: int = 0
    elapsed: float = 0.0


# ══════════════════════════════════════════════════════════════════════════════
#  LAYER 1 — HTML PRE-FLIGHT
# ══════════════════════════════════════════════════════════════════════════════

class PreFlight:
    BLOCKED_PATTERNS = [
        (r"\{\{[A-Z_]{2,}\}\}",  "Unfilled placeholder: {}"),
        (r"\{\{[a-z_]{2,}\}\}",  "Unfilled placeholder: {}"),
        (r"Traceback \(most",     "Python traceback leaked into HTML"),
        (r"TemplateNotFound",     "Jinja2 template error in HTML"),
        (r"KeyError:",            "Python KeyError in HTML"),
        (r"NoneType",             "Python NoneType in HTML"),
    ]
    REQUIRED_TAGS = ["</body>", "</html>", "<title>"]

    @classmethod
    def check(cls, html: str, business_name: str, city: str) -> tuple[list, list]:
        errors, warnings = [], []
        size = len(html.encode("utf-8"))
        if size < MIN_UPLOAD_BYTES:
            errors.append(f"HTML too small ({size:,} bytes) - template render likely failed")
        elif size > 5_000_000:
            warnings.append(f"HTML very large ({size // 1024}KB) - check for runaway loops")
        for tag in cls.REQUIRED_TAGS:
            if tag not in html:
                errors.append(f"Missing required HTML tag: {tag}")
        for pattern, msg in cls.BLOCKED_PATTERNS:
            for match in list(set(re.findall(pattern, html)))[:3]:
                errors.append(msg.format(match))
        if business_name and len(business_name) > 2:
            if business_name.lower() not in html.lower():
                errors.append(f"Business name '{business_name}' not injected - placeholder failed")
        if city and city.lower() not in html.lower():
            warnings.append(f"City '{city}' not found in HTML")
        return errors, warnings


# ══════════════════════════════════════════════════════════════════════════════
#  LAYER 2 — CHANNEL POLLERS
# ══════════════════════════════════════════════════════════════════════════════

def _poll_url(url: str, business_name: str, intervals: list, fake_200_signatures: list = None, label: str = "") -> tuple[bool, int]:
    fake_sigs = fake_200_signatures or []
    attempts = 0
    total_waited = 0
    for wait in intervals:
        time.sleep(wait)
        total_waited += wait
        attempts += 1
        try:
            resp = requests.get(url, timeout=20, allow_redirects=True)
            if resp.status_code == 404:
                logger.info(f"  {label}[{attempts}] 404 - not live yet ({total_waited}s)...")
                continue
            if resp.status_code != 200:
                logger.info(f"  {label}[{attempts}] HTTP {resp.status_code} - waiting...")
                continue
            content = resp.text
            if any(sig in content for sig in fake_sigs):
                logger.info(f"  {label}[{attempts}] Fake 200 (CDN not propagated) - waiting...")
                continue
            if len(content) < MIN_REAL_BYTES:
                logger.info(f"  {label}[{attempts}] 200 but only {len(content)} bytes - stale...")
                continue
            if business_name and business_name.lower() not in content.lower():
                logger.info(f"  {label}[{attempts}] 200 but stale content (biz name missing)...")
                continue
            logger.info(f"  {label}[{attempts}] [LIVE] Verified ({total_waited}s)")
            return True, attempts
        except Exception as e:
            logger.info(f"  {label}[{attempts}] Connection error: {e}")
    return False, attempts


# ══════════════════════════════════════════════════════════════════════════════
#  LAYER 3 — CONTENT AUDIT
# ══════════════════════════════════════════════════════════════════════════════

def _audit_content(url: str, business_name: str) -> tuple[bool, list]:
    issues = []
    try:
        resp = requests.get(url, timeout=20)
        html = resp.text
        leaks = list(set(re.findall(r"\{\{[A-Za-z_]+\}\}", html)))
        if leaks: issues.append(f"Leaked placeholders: {leaks[:5]}")
        title = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
        if not title or not title.group(1).strip(): issues.append("Empty or missing <title>")
        if business_name and business_name.lower() not in html.lower(): issues.append("Business name missing from live page")
        if "Traceback (most recent call last)" in html: issues.append("Python traceback on live page")
        if len(html) < 3000: issues.append(f"Live page too small ({len(html)} bytes)")
    except Exception as e:
        issues.append(f"Audit request failed: {e}")
    critical = [i for i in issues if any(kw in i for kw in ["Traceback", "missing from live", "Leaked", "too small"])]
    return len(critical) == 0, issues


# ══════════════════════════════════════════════════════════════════════════════
#  MASTER FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def validate_and_deploy(
    html: str, filename: str, lead_id: str, business_name: str, niche: str, city: str,
    db=None, upload_netlify_fn=None, upload_github_fn=None, save_db_fn=None
) -> Optional[str]:
    start = time.time()
    skip_netlify = os.getenv("SKIP_NETLIFY", "False").lower() == "true"
    print(f"\n{'='*60}\n  [Vex] Validating: {business_name}\n{'='*60}")

    print(f"\n[Vex] Layer 1 - HTML Pre-Flight")
    errors, warnings = PreFlight.check(html, business_name, city)
    for w in warnings: print(f"  [WARN] {w}")
    for e in errors: print(f"  [ERR] {e}")
    if errors:
        _mark_error(db, lead_id, business_name, f"Pre-flight: {errors[0]}")
        return None
    print(f"  [OK] Passed ({len(html):,} bytes)")

    db_preview_url = None
    if save_db_fn:
        try:
            db_preview_url = save_db_fn(html, lead_id)
            if db_preview_url: print(f"  [DB] Preview saved -> {db_preview_url}")
        except Exception as e: print(f"  [DB] Preview save failed: {e}")

    # Channel 1: Netlify
    if not skip_netlify and upload_netlify_fn:
        print(f"\n[Vex] Channel 1 - Netlify Deploy")
        try:
            netlify_url = upload_netlify_fn(html, lead_id, business_name)
            if netlify_url:
                print(f"  Upload: {netlify_url}\n  Polling...")
                live, att = _poll_url(netlify_url, business_name, NETLIFY_POLL_INTERVALS, NETLIFY_FAKE_200, "Netlify ")
                if live:
                    print(f"\n[Vex] Layer 3 - Content Audit (Netlify)")
                    passed, issues = _audit_content(netlify_url, business_name)
                    for issue in issues: print(f"  [WARN] {issue}")
                    if passed:
                        _log_success(db, lead_id, business_name, niche, netlify_url, "netlify", time.time()-start)
                        return netlify_url
        except Exception as e: print(f"  Netlify Error: {e}")

    # Channel 2: GitHub
    print(f"\n[Vex] Channel 2 - GitHub Deploy")
    github_url = None
    if upload_github_fn:
        try:
            github_url = upload_github_fn(html, filename)
        except Exception as e: print(f"  GitHub Error: {e}")
    
    if not github_url:
        github_url = _upload_to_github_direct(html, filename)

    if github_url:
        print(f"  Upload: {github_url}\n  Polling...")
        live, att = _poll_url(github_url, business_name, GITHUB_POLL_INTERVALS, [], "GitHub ")
        if live:
            print(f"\n[Vex] Layer 3 - Content Audit (GitHub)")
            passed, issues = _audit_content(github_url, business_name)
            for issue in issues: print(f"  [WARN] {issue}")
            if passed:
                _log_success(db, lead_id, business_name, niche, github_url, "github", time.time()-start)
                return github_url

    # Channel 3: Supabase
    if db_preview_url:
        _log_success(db, lead_id, business_name, niche, db_preview_url, "supabase", time.time()-start)
        print(f"\n  [FALLBACK] -> Supabase preview")
        return db_preview_url

    return None

def _mark_error(db, lead_id: str, business_name: str, reason: str):
    msg = f"Vex BLOCKED - {business_name}: {reason}"
    print(f"\n  [DB] {msg}")
    try:
        if db:
            db.push_log("Vex", msg)
            db.update_lead(lead_id, {"status": "Generation Error"})
    except: pass

def _log_success(db, lead_id: str, business_name: str, niche: str, url: str, channel: str, elapsed: float):
    msg = f"Vex VERIFIED - {business_name} via {channel} in {elapsed:.1f}s"
    try:
        if db:
            db.push_log("Vex", msg)
            # CRITICAL FIX: Commit the winning URL to the lead record
            db.update_lead(lead_id, {
                "demo_link": url,
                "status": "Demo Ready",
                "last_generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })
    except Exception as e:
        print(f"  [DB ERR] Failed to save demo_link: {e}")

def _upload_to_github_direct(html: str, filename: str) -> Optional[str]:
    token, repo = os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_REPO")
    if not token or not repo: return None
    url = f"https://api.github.com/repos/{repo}/contents/demo/{filename}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    try:
        existing = requests.get(url, headers=headers)
        sha = existing.json().get("sha") if existing.status_code == 200 else None
        payload = {"message": f"Deploy {filename}", "content": base64.b64encode(html.encode("utf-8")).decode("utf-8"), "branch": "main"}
        if sha: payload["sha"] = sha
        resp = requests.put(url, json=payload, headers=headers, timeout=30)
        if resp.status_code in [200, 201]:
            owner, repo_name = repo.split("/")
            return f"https://{owner}.github.io/{repo_name}/demo/{filename}"
    except: pass
    return None

if __name__ == "__main__":
    print("Vex ready.")
