import os
import re
import sys
import requests
import base64
from dotenv import load_dotenv
from config import STATE
import template_router
import niche_images


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")            # anon key (for public reads)
SERVICE_ROLE_KEY = os.getenv("SERVICE_ROLE_KEY")  # service role (for writes)

# Use service role for writes; fall back to anon key if service role not set
_WRITE_KEY = SERVICE_ROLE_KEY or SUPABASE_KEY
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

def select_archetype(niche, score=0):
    """Select the best design archetype based on the niche and lead value."""
    niche_lower = niche.lower()
    
    # FORCED PREMIUM: A-Tier leads ALWAYS get high-authority dark/gold templates
    if score >= 75:
        # A-Tier leads get Gold Standard for maximum "elite" feel
        return "gold_standard.html"
    
    # Midnight Noir: Tech, Solar, Modern Trades, Engineering
    if any(word in niche_lower for word in ["solar", "tech", "electric", "security", "engineering", "ai", "digital"]):
        return "midnight_noir.html"
    
    # Gold Standard: Elite Professional, Legal, Health, High-End
    if any(word in niche_lower for word in ["law", "dentist", "medical", "luxury", "real estate", "attorney", "wealth", "beauty"]):
        return "gold_standard.html"
    
    # Alpine Vitality: Home Service, Outdoor, Fresh, Cleaning
    if any(word in niche_lower for word in ["landscap", "clean", "roof", "paint", "pool", "tree", "home", "pest"]):
        return "alpine_vitality.html"
    
    # Default to a robust middle-ground or use lead ID hash for variety
    return "midnight_noir.html"

def get_conversion_copy(niche):
    """Provide niche-specific creative hooks and benefits."""
    niche_lower = niche.lower()
    
    # Defaults
    copy = {
        "badge": "Elite Performance",
        "hook": "Industry-leading results, guaranteed.",
        "hero_line_1": "Elite",
        "hero_line_2": "Performance.",
        "niche_short": niche,
        "nav_1": "Services", "nav_2": "Case Studies", "nav_3": "The Firm",
        "year_founded": "2012",
        "years_experience": "12",
        "niche_tagline": "Uncompromising quality for every project.",
        "services_label": "Our Excellence",
        "principal_name": "Alexander Vance",
        "principal_title": "Managing Director",
        "brand_quote": "Every client deserves our absolute best.",
        "about_text": "We provide sophisticated solutions for complex challenges. Our reputation is built on a foundation of integrity and results.",
        "credential_1": "Certified Industry Leader",
        "credential_2": "Over 500 Successful Projects",
        "credential_3": "Award-Winning Service",
        "testimonial_text": "Professional, precise, and highly recommended.",
        "testimonial_author": "Robert Chen",
        "footer_tagline": "Excellence. Precision. Results.",
        "benefit_1": "Rapid Deployment",
        "desc_1": "We value your time. Our efficiency-first approach means we get the job done faster without sacrificing quality.",
        "benefit_2": "Max ROI",
        "desc_2": "Engineered for profitability. Every decision we make is aimed at increasing your bottom line.",
        "benefit_3": "White-Glove Service",
        "desc_3": "A dedicated project manager for every client. Zero stress, total transparency."
    }

    if "law" in niche_lower or "attorney" in niche_lower or "legal" in niche_lower:
        copy.update({
            "badge": "Preeminent Legal Support",
            "hook": "Uncompromising advocacy. Unparalleled results.",
            "hero_line_1": "Uncompromising",
            "hero_line_2": "Advocacy.",
            "niche_short": "Legal Support",
            "nav_1": "Practice Areas", "nav_2": "Our Attorneys", "nav_3": "Results",
            "year_founded": "2008",
            "years_experience": "16",
            "niche_tagline": "Fighting for maximum compensation.",
            "services_label": "Practice Areas",
            "principal_name": "James R. Santos",
            "principal_title": "Lead Attorney",
            "brand_quote": "Justice is not given; it is earned through precision.",
            "about_text": "With over a decade of high-stakes litigation experience, we defend your rights with total authority.",
            "credential_1": "California Bar Association Member",
            "credential_2": "Top 100 Trial Lawyers",
            "credential_3": "Million Dollar Advocates Forum",
            "testimonial_text": "The level of professionalism and care was outstanding. They turned a complex situation into a victory.",
            "testimonial_author": "Sarah Thompson",
            "footer_tagline": "Justice. Precision. Results.",
            "stat_1": "98%", "stat_1_label": "Case Success Rate",
            "stat_2": "2500+", "stat_2_label": "Clients Represented",
            "stat_3": "24/7", "stat_3_label": "Strategic Counsel",
            "service_1": "Personal Injury", "service_1_desc": "Aggressive representation for victims of negligence, securing maximum compensation for your recovery.",
            "service_2": "Corporate Litigation", "service_2_desc": "Sophisticated legal strategies for complex business disputes and high-stakes negotiations.",
            "service_3": "Elite Defense", "service_3_desc": "Protecting your reputation and assets with precise, high-authority criminal and civil defense.",
            "hero_image": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1600&q=80",
            "team_image": "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=1400&q=80"
        })
    elif "solar" in niche_lower or "electric" in niche_lower:
        copy.update({
            "badge": "Energy Independence",
            "hook": "The future of power is here. Clean, efficient, and direct.",
            "hero_line_1": "Clean Energy.",
            "hero_line_2": "Done Different.",
            "niche_short": "Solar Energy",
            "stat_1": "0$", "stat_1_label": "Upfront Costs",
            "stat_2": "25yr", "stat_2_label": "Warranty Guaranteed",
            "stat_3": "Tier-1", "stat_3_label": "Hardware Standards",
            "service_1": "Residential Solar", "service_1_desc": "Custom-engineered panel arrays designed for maximum energy harvest and long-term savings.",
            "service_2": "Battery Storage", "service_2_desc": "Grid-independent security with high-capacity backup systems for total power autonomy.",
            "service_3": "Commercial Energy", "service_3_desc": "Industrial-scale efficiency audits and solar deployment to slash corporate overhead.",
            "hero_image": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=1600&q=80",
            "team_image": "https://images.unsplash.com/photo-1624397640148-949b1732bb0a?w=1400&q=80"
        })
    elif "dental" in niche_lower or "implant" in niche_lower:
        copy.update({
            "badge": "Master Restorations",
            "hook": "Precision dentistry. Life-changing results.",
            "hero_line_1": "Precision.",
            "hero_line_2": "Redefined.",
            "niche_short": "Dentistry",
            "stat_1": "15k+", "stat_1_label": "Successful Procedures",
            "stat_2": "Advanced", "stat_2_label": "3D Imaging Tech",
            "stat_3": "Elite", "stat_3_label": "Patient Care",
            "service_1": "Dental Implants", "service_1_desc": "Permanent, high-durability tooth replacement using medical-grade titanium and aesthetic porcelain.",
            "service_2": "Cosmetic Veneers", "service_2_desc": "Total smile transformations handcrafted for natural brilliance and long-lasting confidence.",
            "service_3": "Full Arch Restoration", "service_3_desc": "Complex restorative solutions to return full function and aesthetic beauty in just one day.",
            "hero_image": "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=1600&q=80",
            "team_image": "https://images.unsplash.com/photo-1598256989800-fe5f95da9787?w=1400&q=80"
        })
    elif "landscap" in niche_lower or "tree" in niche_lower:
        copy.update({
            "badge": "Master Craftsmanship",
            "hook": "Your vision, our architecture. Nature perfected.",
            "hero_line_1": "Nature.",
            "hero_line_2": "Perfected.",
            "niche_short": "Landscaping",
            "stat_1": "100%", "stat_1_label": "Sustainable Design",
            "stat_2": "15yr+", "stat_2_label": "Local Experience",
            "stat_3": "Elite", "stat_3_label": "Curb Appeal",
            "service_1": "Architectural Design", "service_1_desc": "Bespoke outdoor living spaces that flow seamlessly with your property's natural topography.",
            "service_2": "Native Planting", "service_2_desc": "Drought-resistant, climate-optimized botanical selections for permanent, low-maintenance beauty.",
            "service_3": "Hardscape Engineering", "service_3_desc": "Precision stonework and structural elements that define your estate's outdoor character.",
            "hero_image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1600&q=80",
            "team_image": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=1400&q=80"
        })
    else:
        copy.update({
            "stat_1": "100%", "stat_1_label": "Satisfaction Rate",
            "stat_2": "Verified", "stat_2_label": "Top Performance",
            "stat_3": "A-Tier", "stat_3_label": "Quality Control",
            "service_1": "Primary Service", "service_1_desc": "High-authority execution of our core industry solutions, delivered with total precision.",
            "service_2": "Strategic Growth", "service_2_desc": "Optimizing every aspect of your project for maximum ROI and long-term durability.",
            "service_3": "Elite Support", "service_3_desc": "Dedicated consultation and white-glove service to ensure your total satisfaction.",
            "hero_image": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1600&q=80",
            "team_image": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1400&q=80"
        })
    
    return copy

def generate_page(business_name, niche, city, lead_id=None, score=0):
    """Generate a high-authority landing page from an archetype with variation logic."""
    # Use the new Template Router Brain for archetype, variant, and accent selection
    config = template_router.get_template_config(niche, city, lead_id or "preview")
    
    archetype = config["archetype"]
    variant = config["variant"]
    accent = config["accent"]
    
    template_name = f"{archetype}.html"
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    
    if not os.path.exists(template_path):
        template_path = os.path.join(TEMPLATE_DIR, "epoxy_template.html")
    
    # Read template with strict UTF-8
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()
    except UnicodeDecodeError:
        with open(template_path, 'r', encoding='latin-1') as f:
            html = f.read().encode('latin-1').decode('utf-8', errors='replace')
    
    copy = get_conversion_copy(niche)
    
    # 3. Get Niche-Specific Images
    niche_for_images = config.get("niche_matched", niche)
    assets = niche_images.get_images(niche_for_images)
    hero_url = assets["hero"]
    team_url = assets["team"]
    
    # Standard Placeholders
    html = html.replace("{{BUSINESS_NAME}}", str(business_name or "Your Business"))
    html = html.replace("{{NICHE}}", niche or "Your Industry")
    html = html.replace("{{CITY}}", city or "Your Area")
    html = html.replace("{{STATE}}", STATE or "")
    html = html.replace("{{ACCENT}}", accent)
    
    # Creative Engine Placeholders
    html = html.replace("{{BADGE}}", copy.get("badge", ""))
    html = html.replace("{{HOOK}}", copy.get("hook", ""))
    html = html.replace("{{HERO_LINE_1}}", copy.get("hero_line_1", "Elite"))
    html = html.replace("{{HERO_LINE_2}}", copy.get("hero_line_2", "Performance"))
    html = html.replace("{{NICHE_SHORT}}", copy.get("niche_short", niche or "Your Industry"))
    
    # Gold Standard Specifics
    html = html.replace("{{NAV_1}}", copy.get("nav_1", "Services"))
    html = html.replace("{{NAV_2}}", copy.get("nav_2", "Portfolio"))
    html = html.replace("{{NAV_3}}", copy.get("nav_3", "About"))
    html = html.replace("{{YEAR_FOUNDED}}", copy.get("year_founded", "2010"))
    html = html.replace("{{YEARS_EXPERIENCE}}", copy.get("years_experience", "10"))
    html = html.replace("{{NICHE_TAGLINE}}", copy.get("niche_tagline", ""))
    html = html.replace("{{SERVICES_LABEL}}", copy.get("services_label", "Our Services"))
    html = html.replace("{{PRINCIPAL_NAME}}", copy.get("principal_name", "Lead Professional"))
    html = html.replace("{{PRINCIPAL_TITLE}}", copy.get("principal_title", "Senior Partner"))
    html = html.replace("{{BRAND_QUOTE}}", copy.get("brand_quote", ""))
    html = html.replace("{{ABOUT_TEXT}}", copy.get("about_text", ""))
    html = html.replace("{{CREDENTIAL_1}}", copy.get("credential_1", "Verified Expert"))
    html = html.replace("{{CREDENTIAL_2}}", copy.get("credential_2", "Industry Certified"))
    html = html.replace("{{CREDENTIAL_3}}", copy.get("credential_3", "Client Focused"))
    html = html.replace("{{TESTIMONIAL_TEXT}}", copy.get("testimonial_text", ""))
    html = html.replace("{{TESTIMONIAL_AUTHOR}}", copy.get("testimonial_author", ""))
    html = html.replace("{{FOOTER_TAGLINE}}", copy.get("footer_tagline", ""))
    
    # Hero & Team Images
    html = html.replace("{{HERO_IMAGE_URL}}", hero_url)
    html = html.replace("{{TEAM_IMAGE_URL}}", team_url)
    
    # Dynamic Stats
    html = html.replace("{{STAT_1}}", copy.get("stat_1", "10+"))
    html = html.replace("{{STAT_1_LABEL}}", copy.get("stat_1_label", "Years Experience"))
    html = html.replace("{{STAT_2}}", copy.get("stat_2", "100%"))
    html = html.replace("{{STAT_2_LABEL}}", copy.get("stat_2_label", "Satisfaction"))
    html = html.replace("{{STAT_3}}", copy.get("stat_3", "24h"))
    html = html.replace("{{STAT_3_LABEL}}", copy.get("stat_3_label", "Deployment"))
    
    # Dynamic Services
    html = html.replace("{{SERVICE_1}}", copy.get("service_1", "Consulting"))
    html = html.replace("{{SERVICE_1_DESC}}", copy.get("service_1_desc", "Expert industry analysis and strategic planning."))
    html = html.replace("{{SERVICE_2}}", copy.get("service_2", "Execution"))
    html = html.replace("{{SERVICE_2_DESC}}", copy.get("service_2_desc", "High-fidelity production and technical delivery."))
    html = html.replace("{{SERVICE_3}}", copy.get("service_3", "Optimization"))
    html = html.replace("{{SERVICE_3_DESC}}", copy.get("service_3_desc", "Continuous performance monitoring and refinement."))

    # Legacy Benefit Placeholders (for older templates)
    html = html.replace("{{BENEFIT_1}}", copy.get("benefit_1", "Quality"))
    html = html.replace("{{DESC_1}}", copy.get("desc_1", "High standards in every project phase."))
    html = html.replace("{{BENEFIT_2}}", copy.get("benefit_2", "Speed"))
    html = html.replace("{{DESC_2}}", copy.get("desc_2", "Rapid delivery without quality loss."))
    html = html.replace("{{BENEFIT_3}}", copy.get("benefit_3", "ROI"))
    html = html.replace("{{DESC_3}}", copy.get("desc_3", "Maximum value for your investment."))
    
    # Tier Indicator (Elite Branding)
    tier_badge = '<div style="background:gold; color:black; padding:5px 15px; border-radius:50px; font-weight:bold; font-size:12px; display:inline-block; margin-bottom:10px;">ELITE A-TIER PARTNER</div>' if score >= 75 else ''
    html = html.replace("{{TIER_BADGE}}", tier_badge)

    # SECURE THE PREVIEW: Prevent clicks from routing to dashboard
    security_style = """
    <style>
        /* This disables all links from redirecting, keeping them trapped safely in the preview */
        a {
            pointer-events: none !important;
            cursor: default !important;
        }
        /* Add a custom cursor so it still feels like a real site */
        body {
            cursor: url('https://cdn-icons-png.flaticon.com/16/271/271228.png'), auto;
        }
    </style>
    """
    html = html.replace("</head>", f"{security_style}\n</head>")
    
    return html

def upload_to_netlify(html_content: str, lead_id: str, business_name: str = "preview") -> str | None:
    """
    Deploy a single shadow site to Netlify and return the public URL.

    Strategy:
      - Create an in-memory ZIP containing exactly one file: index.html
      - Deploy via Netlify's Files API (not the deploy API — avoids ZIP root issues)
      - Each lead gets its own Netlify site so URLs are isolated
      - Returns: https://<site>.netlify.app
    """
    import io
    import zipfile
    
    token = os.getenv("NETLIFY_TOKEN")
    if not token:
        print("[ERROR] NETLIFY_TOKEN not set in environment.")
        return None

    # ── Sanitize business name for use as a subdomain ──
    clean_biz = re.sub(r'[^a-z0-9]+', '-', business_name.lower()).strip('-')
    slug = f"ri2ch-{clean_biz}-{str(lead_id)[:8]}"  # e.g. ri2ch-santos-law-00000042

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # ── Step 1: Create or retrieve the Netlify site ──
    site_id = _get_or_create_site(slug, headers)
    if not site_id:
        return None

    # ── Step 2: Build ZIP with index.html at root ──
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Explicitly encode as UTF-8 for the ZIP
        zf.writestr("index.html", html_content.encode('utf-8'))
        # FORCE HTML RENDERING: Add a _headers file for Netlify
        headers_content = "/*\n  Content-Type: text/html; charset=utf-8\n"
        zf.writestr("_headers", headers_content.encode('utf-8'))
    zip_bytes = zip_buffer.getvalue()

    # ── Step 3: Deploy the ZIP ──
    deploy_resp = requests.post(
        f"https://api.netlify.com/api/v1/sites/{site_id}/deploys",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/zip",
        },
        data=zip_bytes,
        timeout=30,
    )

    if deploy_resp.status_code not in [200, 201]:
        print(f"[ERROR] Netlify deploy failed: {deploy_resp.status_code} {deploy_resp.text}")
        return None

    deploy_data = deploy_resp.json()

    # ── Step 4: Return the live URL ──
    url = deploy_data.get("deploy_ssl_url") or deploy_data.get("url") or f"https://{slug}.netlify.app"
    print(f"[OK] Shadow site live: {url}")
    return url

def _get_or_create_site(name: str, headers: dict) -> str | None:
    """Get existing Netlify site by name or create a new one."""
    # Try to find existing site
    try:
        list_resp = requests.get(
            "https://api.netlify.com/api/v1/sites",
            headers=headers,
            params={"filter": "all", "per_page": 100},
            timeout=15,
        )
        if list_resp.ok:
            for site in list_resp.json():
                if site.get("name") == name:
                    return site["id"]

        # Create new site
        create_resp = requests.post(
            "https://api.netlify.com/api/v1/sites",
            headers=headers,
            json={"name": name},
            timeout=15,
        )
        if create_resp.status_code in [200, 201]:
            return create_resp.json()["id"]

        print(f"[ERROR] Could not create Netlify site '{name}': {create_resp.status_code} {create_resp.text}")
    except Exception as e:
        print(f"[ERROR] Netlify site management failed: {e}")
    return None

def upload_to_github(html_content, filename):
    """Upload HTML content directly to GitHub via the Content API."""
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")
    if not token or not repo:
        print("Error: GITHUB_TOKEN or GITHUB_REPO not set in environment.")
        return None
        
    branch = "main"
    # Ensure file is saved in the demo/ folder in the repo
    url = f"https://api.github.com/repos/{repo}/contents/demo/{filename}"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Check if file exists to get SHA
    existing = requests.get(url, headers=headers)
    sha = existing.json().get("sha") if existing.status_code == 200 else None
    
    content_encoded = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    
    payload = {
        "message": f"Deploy shadow site {filename}",
        "content": content_encoded,
        "branch": branch
    }
    if sha:
        payload["sha"] = sha
        
    response = requests.put(url, json=payload, headers=headers)
    
    if response.status_code in [200, 201]:
        # Return the public GitHub Pages URL
        try:
            owner, repo_name = repo.split('/')
            return f"https://{owner}.github.io/{repo_name}/demo/{filename}"
        except ValueError:
            print(f"Error: Invalid GITHUB_REPO format '{repo}'. Expected 'owner/repo'.")
            return None
    
    print(f"Error uploading to GitHub: {response.status_code} - {response.text}")
    return None

def save_preview_to_db(html_content: str, lead_id: str) -> str | None:
    """
    Save the generated HTML directly into the leads table (preview_html column).
    Returns the public Edge Function URL for this preview.
    """
    if not SUPABASE_URL or not _WRITE_KEY:
        print("[ERROR] SUPABASE_URL or key not set in environment.")
        return None

    endpoint = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}"

    headers = {
        "apikey": _WRITE_KEY,
        "Authorization": f"Bearer {_WRITE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    # Deep encoding check: ensure we are sending raw UTF-8 strings
    try:
        # Convert to bytes and back to string to ensure pure UTF-8 normalization
        clean_html = html_content.encode('utf-8').decode('utf-8')
    except UnicodeError:
        # If mangled, force a clean UTF-8 representation
        clean_html = html_content.encode('utf-8', errors='replace').decode('utf-8')

    payload = {"preview_html": clean_html}

    try:
        response = requests.patch(endpoint, json=payload, headers=headers, timeout=15)
        response.raise_for_status()

        # Build the public Edge Function URL
        # Extract project ref from SUPABASE_URL
        project_ref = SUPABASE_URL.replace("https://", "").split(".")[0]
        preview_url = f"https://{project_ref}.supabase.co/functions/v1/preview?id={lead_id}"

        print(f"[OK] Preview saved for lead {lead_id}: {preview_url}")
        return preview_url

    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] DB save failed for lead {lead_id}: {e} | {e.response.text}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error saving preview for lead {lead_id}: {e}")
        return None

def upload_to_supabase_storage(html_content: str, filename: str, lead_id: str = None, business_name: str = "preview") -> str | None:
    """
    Drop-in replacement. Routes all uploads to Netlify instead of Supabase Storage.
    """
    _id = lead_id or filename.replace("preview_", "").replace(".html", "").strip()
    return upload_to_netlify(html_content, _id, business_name)

def update_lead_demo_link(lead_id, demo_link):
    """Update the demo_link and status for a lead in Supabase."""
    endpoint = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}"
    try:
        data = {
            "demo_link": demo_link,
            "status": "Shadow Site Ready"
        }
        response = requests.patch(endpoint, headers=get_headers(), json=data)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error updating demo_link/status: {e}")
        return False

def save_locally(html_content, filename):
    """Fallback: save HTML to local output directory."""
    output_dir = os.path.join(os.path.dirname(__file__), "generated_pages")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Saved locally: {filepath}")
    return filepath

def main():
    if len(sys.argv) < 4:
        print("Usage: python generate_landing.py <business_name> <niche> <city> [lead_id]")
        print('Example: python generate_landing.py "DFW Classic Coatings" "Epoxy Garage Flooring" "Frisco"')
        return
    
    business_name = sys.argv[1]
    niche = sys.argv[2]
    city = sys.argv[3]
    lead_id = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "None" else None
    slug_arg = sys.argv[5] if len(sys.argv) > 5 else None
    score_arg = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    
    # Create a safe filename (slug)
    if slug_arg:
        filename = f"{slug_arg}.html"
    else:
        # Fallback slug logic
        clean_name = re.sub(r'[^a-z0-9]', '-', business_name.lower())
        clean_city = re.sub(r'[^a-z0-9]', '-', city.lower())
        safe_name = re.sub(r'-+', '-', clean_name).strip('-')
        safe_city = re.sub(r'-+', '-', clean_city).strip('-')
        filename = f"{safe_name}-{safe_city}.html"
    
    print(f"Generating landing page for: {business_name}")
    print(f"  Niche: {niche}")
    print(f"  City:  {city}")
    
    # Generate the HTML
    html = generate_page(business_name, niche, city, lead_id, score_arg)
    if not html:
        return
    
    # 4. Save Locally
    OUTPUT_DIR = "demo"
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"DONE: Shadow Site saved to {filepath}")
    
    # 5. Deployment Channel 1: Netlify (Isolated Site Strategy)
    deployed_url = upload_to_netlify(html, lead_id or "preview", business_name)
    if deployed_url:
        print(f"Netlify Deployment Successful: {deployed_url}")
    
    # 5. Deployment Channel 2: GitHub (Redundant Backup)
    if not deployed_url:
        github_url = upload_to_github(html, filename)
        if github_url:
            print(f"GitHub API Upload Successful: {github_url}")
            deployed_url = github_url
    
    # Always save to DB as a secondary preview bridge
    if lead_id:
        db_preview = save_preview_to_db(html, lead_id)
        if not deployed_url:
            deployed_url = db_preview
    
    # 6. Update Database
    if lead_id and deployed_url:
        if update_lead_demo_link(lead_id, deployed_url):
            print(f"DONE Updated lead {lead_id} with Link: {deployed_url}")
    
    print("\nDone! The landing page is ready to send.")

if __name__ == "__main__":
    main()
