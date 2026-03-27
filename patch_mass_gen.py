with open("c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\mass_generate_shadow_sites.py", "r", encoding="utf-8") as f:
    code = f.read()

import re

old_main = re.search(r"def main\(\):.*?(?=if __name__ ==)", code, re.DOTALL).group(0)

new_main = """def main():
    LIMIT = 50 # Production burst
    MIN_SCORE = 75
    
    # Only fetch leads that are audited and need shadow sites to reduce payload
    leads = db.fetch_leads({"opportunity_score": "gte.75"})
    
    # Filter for leads that don't have a live demo_link yet
    ready_leads = [l for l in leads if not l.get('demo_link') and l.get('opportunity_score', 0) >= MIN_SCORE]
    
    print(f"AESTHETIC EXCELLENCE: Queuing {len(ready_leads)} Whales for V15.1 production burst.")
    import sys
    sys.stdout.flush()
    
    count = 0
    for lead in ready_leads:
        if generate_for_lead(lead):
            count += 1
        if count >= LIMIT: 
            break
        import time
        time.sleep(3) # Heavy jitter for DB stability

    print(f"\\nPhase Complete. Deployed {count} premium shadow sites.")
    sys.stdout.flush()

"""

code = code.replace(old_main, new_main)

with open("c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\mass_generate_shadow_sites.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Patched mass_generate_shadow_sites.py successfully.")
