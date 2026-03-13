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

def generate_page(business_name, niche, city, template_name="epoxy_template.html"):
    """Generate a landing page from a template and return the HTML string."""
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    
    if not os.path.exists(template_path):
        print(f"Error: Template {template_name} not found.")
        return None
    
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Replace placeholders
    html = html.replace("{{BUSINESS_NAME}}", business_name)
    html = html.replace("{{NICHE}}", niche)
    html = html.replace("{{CITY}}", city)
    html = html.replace("{{STATE}}", STATE)
    
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
        if hasattr(e, 'response') and e.response:
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
    html = generate_page(business_name, niche, city)
    if not html:
        return
    
    # Try uploading to Supabase Storage first
    demo_link = None
    if SUPABASE_URL and SUPABASE_KEY:
        print("Uploading to Supabase Storage...")
        demo_link = upload_to_supabase_storage(html, filename)
        if demo_link:
            print(f"✅ Live at: {demo_link}")
            
            # Update the lead record if lead_id provided
            if lead_id:
                update_lead_demo_link(lead_id, demo_link)
                print(f"✅ Updated lead record with demo link.")
        else:
            print("⚠️ Upload failed. Saving locally instead.")
            save_locally(html, filename)
    else:
        print("No Supabase credentials. Saving locally.")
        save_locally(html, filename)
    
    print("\nDone! The landing page is ready to send.")

if __name__ == "__main__":
    main()
