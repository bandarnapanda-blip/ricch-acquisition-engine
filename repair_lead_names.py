import os
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from database import db
from analyzer import generate_ai_completion
from dotenv import load_dotenv

load_dotenv()

def extract_business_name(lead):
    url = lead.get('website')
    if not url: return None
    
    print(f"Repairing: {url}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else ""
        h1 = soup.find('h1').text if soup.find('h1') else ""
        
        prompt = f"""
        Extract the professional business name from this website metadata:
        URL: {url}
        Title: {title}
        H1: {h1}
        
        Rules:
        1. Only return the name, nothing else.
        2. If you are not 100% sure, guess based on the domain.
        3. Remove slogans or cities from the name if possible (e.g. "Bob's Plumbing NY" -> "Bob's Plumbing").
        """
        
        name = generate_ai_completion(prompt)
        # Clean up any AI artifacts
        name = name.strip('"').strip("'").strip()
        if len(name) > 60: name = name[:60] # Reasonable limit
        return name
    except Exception as e:
        print(f"  Error extracting name for {url}: {e}")
        # Fallback: domain name
        domain = urlparse(url).netloc.replace('www.', '').split('.')[0].capitalize()
        return domain

def main():
    leads = db.fetch_leads()
    placeholders = ["", "none", "unknown", "unknown business"]
    to_repair = [l for l in leads if not l.get('business_name') or l.get('business_name').lower() in placeholders]
    
    print(f"Identified {len(to_repair)} leads requiring name repair.")
    
    count = 0
    for lead in to_repair:
        name = extract_business_name(lead)
        if name:
            db.update_lead(lead['id'], {"business_name": name})
            print(f"  -> SUCCESS: {name}")
            count += 1
        
        # Rate limit protection for Gemini
        time.sleep(1)
        
        if count >= 50: # Batch of 50 for testing
            print("Batch limit reached.")
            break

    print(f"\nDone. Repaired {count} leads.")

if __name__ == "__main__":
    main()
