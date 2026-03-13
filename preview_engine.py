import os
import json
from urllib.parse import quote_plus
from config import AGENCY_DOMAIN

# Shadow Site Themes
THEMES = {
    "Modern Professional": {
        "primary_color": "#00e5ff",
        "secondary_color": "#161922"
    },
    "High-Ticket Luxury": {
        "primary_color": "#ff4d94",
        "secondary_color": "#0a0b10"
    },
    "Rugged Industrial": {
        "primary_color": "#ffcc00",
        "secondary_color": "#1a1a1a"
    }
}

def generate_preview_metadata(lead):
    """Generate the JSON metadata required to render a Shadow Site preview."""
    niche = lead.get('niche', 'High-Ticket Business')
    city = lead.get('city', 'United States')
    website = lead.get('website', '')
    domain = website.replace('https://','').replace('http://','').replace('www.','').strip('/')
    
    # Select theme based on niche
    theme_key = "Modern Professional"
    if "Epoxy" in niche or "Concrete" in niche or "Construction" in niche or "Roofing" in niche:
        theme_key = "Rugged Industrial"
    elif "Attorneys" in niche or "Luxury" in niche or "Dental" in niche:
        theme_key = "High-Ticket Luxury"
        
    theme = THEMES[theme_key]
    
    metadata = {
        "lead_id": lead.get('id'),
        "business_name": domain.split('.')[0].replace('-', ' ').title(),
        "niche": niche,
        "city": city,
        "theme": theme,
        "headline": f"The New Standard of {niche} in {city}",
        "subheadline": f"Modernizing {domain} for Maximum Lead Acquisition.",
        "features": [
            "Instant Quote Funnel",
            "Mobile-First Optimization",
            "Before/After Revenue Gallery"
        ],
    }
    # Internal dashboard link (relative)
    metadata["preview_url"] = f"/?preview_id={lead.get('id', 'default')}"
    # External outreach link (absolute)
    metadata["public_preview_url"] = f"https://{AGENCY_DOMAIN}/?preview_id={lead.get('id', 'default')}"
    return metadata

def render_shadow_site_html(meta):
    """Generates a premium, responsive HTML redesign prototype."""
    theme = meta['theme']
    primary = theme['primary_color']
    secondary = theme['secondary_color']
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{meta['business_name']} | New Standard</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;700;900&display=swap');
            body, html {{
                margin: 0; padding: 0;
                font-family: 'Outfit', sans-serif;
                background: {secondary};
                color: #fff;
                overflow-x: hidden;
            }}
            .hero {{
                height: 80vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                padding: 40px;
                background: linear-gradient(to bottom, rgba(0,0,0,0.5), {secondary}), 
                            url('https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80');
                background-size: cover;
                background-position: center;
            }}
            .hero h1 {{
                font-size: 4.5rem;
                font-weight: 900;
                margin: 0;
                line-height: 1;
                letter-spacing: -2px;
                text-transform: uppercase;
                color: {primary};
            }}
            .hero p {{
                font-size: 1.5rem;
                opacity: 0.8;
                max-width: 700px;
                margin: 20px 0 40px 0;
            }}
            .btn {{
                padding: 20px 50px;
                background: {primary};
                color: {secondary};
                text-decoration: none;
                font-weight: 900;
                border-radius: 50px;
                font-size: 1.2rem;
                box-shadow: 0 10px 30px {primary}44;
                transition: transform 0.3s;
            }}
            .btn:hover {{ transform: scale(1.05); }}
            
            .features-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 40px;
                padding: 100px 5%;
                background: #fff;
                color: #000;
            }}
            .feature-card {{
                padding: 40px;
                border: 1px solid #eee;
                border-radius: 30px;
            }}
            .feature-card h3 {{ font-size: 1.5rem; margin-top: 0; color: {primary}; }}
            
            .cta-section {{
                padding: 150px 5%;
                text-align: center;
                background: {secondary};
            }}
            
            .badge {{
                display: inline-block;
                padding: 8px 16px;
                background: {primary}22;
                color: {primary};
                border-radius: 20px;
                font-weight: 800;
                font-size: 0.8rem;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <section class="hero">
            <div class="badge">{meta['niche'].upper()} RECOVERY ENGINE</div>
            <h1>{meta['business_name']}</h1>
            <p>{meta['subheadline']}</p>
            <a href="#" class="btn">SECURE YOUR QUOTE</a>
        </section>
        
        <section class="features-grid">
            {"".join([f'<div class="feature-card"><h3>{f}</h3><p>Optimized for high-conversion traffic in {meta["city"]}.</p></div>' for f in meta['features']])}
        </section>
        
        <section class="cta-section">
            <h2 style="font-size: 3rem; font-weight: 900;">Stop Losing Revenue</h2>
            <p style="opacity: 0.6; margin-bottom: 40px;">This is a live simulation of your technical recovery site.</p>
            <a href="#" class="btn" style="background: #fff; color: #000;">DEMO FULL SYSTEM</a>
        </section>
    </body>
    </html>
    """
    return html

def get_demo_link(lead_id):
    """Generates a public simulation link based on the agency domain."""
    return f"https://{AGENCY_DOMAIN}/?preview_id={lead_id}"

if __name__ == "__main__":
    test_lead = {
        "id": "test-123",
        "website": "https://mike-epoxy.com",
        "niche": "Epoxy Garage Flooring",
        "city": "Beverly Hills"
    }
    print(json.dumps(generate_preview_metadata(test_lead), indent=2))
