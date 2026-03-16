import os
import sys
import json
from analyzer import analyze_site
from intelligence import get_outreach_recommendation

def verify_intel_engine():
    test_urls = [
        "https://www.google.com",
        "https://www.shopify.com",
    ]
    
    print("--- INTELLIGENCE ENGINE VERIFICATION ---")
    
    for url in test_urls:
        print(f"\nAuditing: {url}")
        try:
            results = analyze_site(url)
            
            deal_score = results.get('deal_score', 0)
            intel = results.get('intelligence')
            
            print(f"Deal Probability: {deal_score}%")
            if intel:
                print(f"Signals: Ads={intel.google_ads}, Meta={intel.meta_pixel}, Locations={intel.multiple_locations}")
                print(f"Scores: Financial={intel.financial_score}, Website={intel.website_score}")
            
            recommendation = get_outreach_recommendation(deal_score)
            print(f"Recommendation: {recommendation}")
        except Exception as e:
            print(f"Failed to audit {url}: {e}")

if __name__ == "__main__":
    verify_intel_engine()
