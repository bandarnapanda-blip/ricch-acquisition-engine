from playwright.sync_api import sync_playwright
from find_leads import scrape_query_playwright, scrape_query_bing, scrape_query_brave
import json

def diagnose():
    query = "Dental Implant Specialists in Newport Beach"
    print(f"[Diagnostic] Probing: {query}")
    
    print(f"DEBUG: sync_playwright from top-level: {sync_playwright}")

    print("\n--- Testing Playwright (DDG) ---")
    try:
        pw_leads = scrape_query_playwright(query)
        print(f"Playwright Found: {len(pw_leads)}")
    except Exception as e:
        print(f"Playwright Error: {e}")

    # ... rest of the script
if __name__ == "__main__":
    diagnose()
