import os
import re
import sys
import requests
from dotenv import load_dotenv
from config import STATE

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
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
            "benefit_1": "Strategic Dominance",
            "desc_1": "We don't just process cases; we win them. Our tactical approach ensures the best possible outcome.",
            "benefit_2": "Expert Counsel",
            "desc_2": "Direct access to lead partners with decades of specialized experience in your field.",
            "benefit_3": "Confidentiality First",
            "desc_3": "Private, secure, and discreet handling of your most sensitive legal matters."
        })
    elif "solar" in niche_lower or "electric" in niche_lower:
        copy.update({
            "badge": "Energy Independence",
            "hook": "The future of power is here. Clean, efficient, and direct.",
            "benefit_1": "Zero-Down Options",
            "desc_1": "Switching to clean energy shouldn't break the bank. We offer flexible ownership paths for every home.",
            "benefit_2": "Tier-1 Hardware",
            "desc_2": "We only use high-efficiency panels and inverters backed by 25-year manufacturer warranties.",
            "benefit_3": "Grid-Ready Tech",
            "desc_3": "Seamless integration with local utilities and battery backup systems for total security."
        })
    elif "landscap" in niche_lower or "tree" in niche_lower:
        copy.update({
            "badge": "Master Craftsmanship",
            "hook": "Your vision, our architecture. Nature perfected.",
            "benefit_1": "Artistic Vision",
            "desc_1": "Our designers treat every lot as a canvas, creating unique outdoor living spaces that flow with your lifestyle.",
            "benefit_2": "Sustainable Growth",
            "desc_2": "We use native plants and smart irrigation to ensure a beautiful yard that's also climate-resistant.",
            "benefit_3": "Curb Appeal Boost",
            "desc_3": "Instantly increase your property value with high-authority landscaping from the pros."
        })
    
    return copy

def get_elite_template(business_name, niche, city):
    # Map niches to high-end architectural/business imagery
    image_map = {
        "Roofing": "https://images.unsplash.com/photo-1632758113409-e8550742d131?q=80&w=2000&auto=format&fit=crop",
        "Epoxy Garage": "https://images.unsplash.com/photo-1595846519845-68e298c2edd8?q=80&w=2000&auto=format&fit=crop",
        "Pool Builders": "https://images.unsplash.com/photo-1576013551627-11971f64baf1?q=80&w=2000&auto=format&fit=crop"
    }
    
    # Fallback premium image if niche isn't mapped
    bg_image = image_map.get(niche, "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2000&auto=format&fit=crop")

    elite_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{business_name} | Elite {niche}</title>
        <!-- Tailwind CSS for modern styling -->
        <script src="https://cdn.tailwindcss.com"></script>
        <!-- Premium Fonts -->
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;800&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; }}
            h1, h2, h3 {{ font-family: 'Playfair Display', serif; }}
            /* SECURE THE PREVIEW: Prevent clicks from routing to dashboard */
            a, button {{ 
                pointer-events: none !important;
                cursor: default !important;
            }}
            /* Add a custom cursor so it still feels like a real site */
            body {{
                cursor: url('https://cdn-icons-png.flaticon.com/16/271/271228.png'), auto;
            }}
        </style>
    </head>
    <body class="bg-zinc-50 text-zinc-900 antialiased selection:bg-black selection:text-white">
        
        <!-- Navigation -->
        <nav class="absolute w-full z-10 top-0 py-6 px-10 flex justify-between items-center text-white mix-blend-difference">
            <div class="text-2xl font-bold tracking-tighter uppercase">{business_name}.</div>
            <div class="space-x-8 text-sm tracking-widest uppercase hidden md:block">
                <span>Services</span>
                <span>Portfolio</span>
                <span>Contact</span>
            </div>
        </nav>

        <!-- Hero Section -->
        <section class="relative h-screen flex items-center justify-center overflow-hidden">
            <div class="absolute inset-0 z-0">
                <img src="{bg_image}" alt="{niche} in {city}" class="w-full h-full object-cover brightness-50">
            </div>
            <div class="relative z-10 text-center text-white px-4 max-w-5xl mx-auto mt-20">
                <p class="uppercase tracking-[0.3em] text-sm mb-6 text-zinc-300">The standard for {city}</p>
                <h1 class="text-6xl md:text-8xl font-extrabold leading-tight mb-8 drop-shadow-lg">
                    Redefining <br> <span class="text-transparent bg-clip-text bg-gradient-to-r from-zinc-200 to-zinc-500">{niche}</span>
                </h1>
                <p class="text-lg md:text-xl font-light max-w-2xl mx-auto mb-10 text-zinc-300">
                    Precision engineering meets flawless execution. Upgrade your property's value with {city}'s premier architectural and design firm.
                </p>
                <button class="bg-white text-black px-10 py-4 uppercase tracking-widest text-sm hover:bg-zinc-200 transition-all duration-300">
                    Request Private Consultation
                </button>
            </div>
        </section>

        <!-- Stats Section (Glassmorphism) -->
        <section class="relative -mt-20 z-20 max-w-6xl mx-auto px-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bg-white/90 backdrop-blur-md p-10 shadow-2xl border border-zinc-100">
                    <div class="text-4xl font-bold mb-2">10+</div>
                    <div class="text-xs uppercase tracking-widest text-zinc-500">Years Experience</div>
                </div>
                <div class="bg-white/90 backdrop-blur-md p-10 shadow-2xl border border-zinc-100">
                    <div class="text-4xl font-bold mb-2">100%</div>
                    <div class="text-xs uppercase tracking-widest text-zinc-500">Client Satisfaction</div>
                </div>
                <div class="bg-white/90 backdrop-blur-md p-10 shadow-2xl border border-zinc-100 bg-zinc-900 text-white">
                    <div class="text-4xl font-bold mb-2">24h</div>
                    <div class="text-xs uppercase tracking-widest text-zinc-400">Deploy Time</div>
                </div>
            </div>
        </section>

    </body>
    </html>
    """
    return elite_html

def generate_page(business_name, niche, city, lead_id=None, score=0):
    """Generate a high-authority landing page from an archetype."""
    if score >= 75:
        return get_elite_template(str(business_name or "Your Business"), niche or "Your Industry", city or "Your Area")

    template_name = select_archetype(niche, score)
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    
    if not os.path.exists(template_path):
        template_path = os.path.join(TEMPLATE_DIR, "epoxy_template.html")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    copy = get_conversion_copy(niche)
    
    # Standard Placeholders
    html = html.replace("{{BUSINESS_NAME}}", str(business_name or "Your Business"))
    html = html.replace("{{NICHE}}", niche or "Your Industry")
    html = html.replace("{{CITY}}", city or "Your Area")
    html = html.replace("{{STATE}}", STATE or "")
    
    # Creative Engine Placeholders
    html = html.replace("{{BADGE}}", copy["badge"])
    html = html.replace("{{HOOK}}", copy["hook"])
    html = html.replace("{{BENEFIT_1}}", copy["benefit_1"])
    html = html.replace("{{DESC_1}}", copy["desc_1"])
    html = html.replace("{{BENEFIT_2}}", copy["benefit_2"])
    html = html.replace("{{DESC_2}}", copy["desc_2"])
    html = html.replace("{{BENEFIT_3}}", copy["benefit_3"])
    html = html.replace("{{DESC_3}}", copy["desc_3"])
    
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

def upload_to_supabase_storage(html_content, filename):
    """Upload an HTML file to Supabase Storage and return the public URL."""
    bucket = "landing-pages"
    
    # Upload the file
    endpoint = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "text/html",
        "x-upsert": "true"
    }
    
    try:
        response = requests.post(endpoint, headers=headers, data=html_content.encode('utf-8'))
        response.raise_for_status()
        
        # Return the public URL
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
        return public_url
    except Exception as e:
        print(f"Error uploading to Supabase Storage: {e}")
        if hasattr(e, 'response') and getattr(e, 'response', None):
            print(f"Response: {e.response.text}")
        return None

def update_lead_demo_link(lead_id, demo_link):
    """Update the demo_link for a lead in Supabase."""
    endpoint = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}"
    try:
        response = requests.patch(endpoint, headers=get_headers(), json={"demo_link": demo_link})
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error updating demo_link: {e}")
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
    lead_id = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Create a safe filename
    safe_name = re.sub(r'[^a-zA-Z0-9]', '-', business_name.lower()).strip('-')
    filename = f"{safe_name}-{city.lower()}.html"
    
    print(f"Generating landing page for: {business_name}")
    print(f"  Niche: {niche}")
    print(f"  City:  {city}, {STATE}")
    
    # Generate the HTML
    html = generate_page(business_name, niche, city, lead_id)
    if not html:
        return
    
    # Try uploading to Supabase Storage first
    demo_link = None
    if SUPABASE_URL and SUPABASE_KEY:
        print("Uploading to Supabase Storage...")
        demo_link = upload_to_supabase_storage(html, filename)
        if demo_link:
            print(f"DONE Live at: {demo_link}")
            
            # Update the lead record if lead_id provided
            if lead_id:
                update_lead_demo_link(lead_id, demo_link)
                print(f"DONE Updated lead record with demo link.")
        else:
            print("WARNING Upload failed. Saving locally instead.")
            save_locally(html, filename)
    else:
        print("No Supabase credentials. Saving locally.")
        save_locally(html, filename)
    
    print("\nDone! The landing page is ready to send.")

if __name__ == "__main__":
    main()
