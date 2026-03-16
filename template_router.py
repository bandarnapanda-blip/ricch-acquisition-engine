# template_router.py
# The brain of the Shadow Site variation system.
# Handles niche matching, variant selection, accent colors,
# duplicate prevention, and fallback logic.

import os
import random
import difflib
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

# ── MASTER NICHE ROUTING TABLE ──────────────────────────────────────────────
NICHE_ROUTES = {
    "Solar Energy Installers":      {"archetype": "midnight_noir", "variant": "B", "accent": "#00e5ff"},
    "Personal Injury Attorneys":    {"archetype": "gold_standard", "variant": "A", "accent": "#c9a84c"},
    "Luxury Home Remodeling":       {"archetype": "alpine_vitality","variant": "C", "accent": "#7a9e7e"},
    "HVAC and Climate Control":     {"archetype": "midnight_noir", "variant": "C", "accent": "#4fc3f7"},
    "Dental Implant Specialists":   {"archetype": "gold_standard", "variant": "B", "accent": "#5bbfb5"},
    "Epoxy Garage Flooring":        {"archetype": "midnight_noir", "variant": "A", "accent": "#f0a500"},
    "Roofing Contractors":          {"archetype": "midnight_noir", "variant": "C", "accent": "#e07b39"},
    "Concrete and Paving":          {"archetype": "midnight_noir", "variant": "B", "accent": "#8899aa"},
    "Landscaping Design":           {"archetype": "alpine_vitality","variant": "A", "accent": "#2d6a4f"},
    "Pool and Spa Builders":        {"archetype": "alpine_vitality","variant": "B", "accent": "#00b4d8"},
    "Kitchen and Bath Remodelers":  {"archetype": "alpine_vitality","variant": "C", "accent": "#c1715b"},
}

# All available variants per archetype for randomization
ARCHETYPE_VARIANTS = {
    "midnight_noir":  ["A", "B", "C"],
    "gold_standard":  ["A", "B", "C"],
    "alpine_vitality":["A", "B", "C"],
}

# Accent color pools per archetype — for randomized shifts
ACCENT_POOLS = {
    "midnight_noir":   ["#00e5ff", "#f0a500", "#e07b39", "#8899aa", "#4fc3f7", "#a78bfa"],
    "gold_standard":   ["#c9a84c", "#5bbfb5", "#e8d5a0", "#b8960c", "#d4a843"],
    "alpine_vitality": ["#2d6a4f", "#00b4d8", "#c1715b", "#7a9e7e", "#52b788"],
}

def match_niche(raw_niche: str) -> str:
    """
    Fuzzy-match an unknown niche string to the closest known niche.
    e.g. 'Plumbing' -> 'HVAC and Climate Control'
         'General Contractor' -> 'Roofing Contractors'
    """
    if not raw_niche:
        return "Roofing Contractors"  # safe default

    known = list(NICHE_ROUTES.keys())

    # Direct match first
    for k in known:
        if raw_niche.lower() == k.lower():
            return k

    # Fuzzy match
    matches = difflib.get_close_matches(raw_niche, known, n=1, cutoff=0.3)
    if matches:
        return matches[0]

    # Keyword fallback
    raw_lower = raw_niche.lower()
    keyword_map = {
        "plumb": "HVAC and Climate Control",
        "electric": "HVAC and Climate Control",
        "paint": "Luxury Home Remodeling",
        "floor": "Epoxy Garage Flooring",
        "tile": "Concrete and Paving",
        "fence": "Landscaping Design",
        "tree": "Landscaping Design",
        "lawn": "Landscaping Design",
        "window": "Luxury Home Remodeling",
        "door": "Luxury Home Remodeling",
        "garage": "Epoxy Garage Flooring",
        "driveway": "Concrete and Paving",
        "pool": "Pool and Spa Builders",
        "spa": "Pool and Spa Builders",
        "bath": "Kitchen and Bath Remodelers",
        "kitchen": "Kitchen and Bath Remodelers",
        "dental": "Dental Implant Specialists",
        "attorney": "Personal Injury Attorneys",
        "law": "Personal Injury Attorneys",
        "solar": "Solar Energy Installers",
        "roof": "Roofing Contractors",
        "concrete": "Concrete and Paving",
        "pav": "Concrete and Paving",
        "hvac": "HVAC and Climate Control",
        "heat": "HVAC and Climate Control",
        "cool": "HVAC and Climate Control",
        "air": "HVAC and Climate Control",
        "remodel": "Luxury Home Remodeling",
        "renovat": "Luxury Home Remodeling",
        "landscape": "Landscaping Design",
        "garden": "Landscaping Design",
        "epoxy": "Epoxy Garage Flooring",
    }
    for keyword, niche in keyword_map.items():
        if keyword in raw_lower:
            return niche

    # Last resort
    return "Roofing Contractors"


def _is_duplicate(niche: str, city: str, archetype: str, variant: str, accent: str) -> bool:
    """Check if this exact combination has been sent in this city already."""
    url = f"{SUPABASE_URL}/rest/v1/sent_designs?select=id&niche=eq.{niche}&city=eq.{city}&archetype=eq.{archetype}&variant=eq.{variant}&accent=eq.{accent}"
    try:
        resp = requests.get(url, headers=get_headers())
        if resp.status_code == 200:
            return len(resp.json()) > 0
        return False
    except Exception:
        return False  # if check fails, allow generation


def _record_design(niche: str, city: str, archetype: str, variant: str, accent: str, lead_id: str):
    """Record this design combination as sent."""
    url = f"{SUPABASE_URL}/rest/v1/sent_designs"
    payload = {
        "niche": niche,
        "city": city,
        "archetype": archetype,
        "variant": variant,
        "accent": accent,
        "lead_id": str(lead_id),
        "sent_at": datetime.utcnow().isoformat(),
    }
    try:
        requests.post(url, headers=get_headers(), json=payload)
    except Exception as e:
        print(f"[WARN] Could not record sent design: {e}")


def get_template_config(
    raw_niche: str,
    city: str,
    lead_id: str,
    force_archetype: str = None,
    force_variant: str = None,
    force_accent: str = None,
) -> dict:
    """
    Master routing function. Returns the full template config for a lead.

    Returns:
        {
            "archetype": "midnight_noir",
            "variant": "B",
            "accent": "#00e5ff",
            "niche_matched": "Solar Energy Installers",
            "template_key": "midnight_noir_B",
        }
    """
    # 1. Match niche
    niche = match_niche(raw_niche)
    base = NICHE_ROUTES[niche]

    archetype = force_archetype or base["archetype"]
    variant   = force_variant   or base["variant"]
    accent    = force_accent    or base["accent"]

    # 2. Check for duplicates — randomize if clash
    attempts = 0
    while _is_duplicate(niche, city, archetype, variant, accent) and attempts < 10:
        variant = random.choice(ARCHETYPE_VARIANTS[archetype])
        accent  = random.choice(ACCENT_POOLS[archetype])
        attempts += 1

    # 3. Record this combination
    _record_design(niche, city, archetype, variant, accent, lead_id)

    return {
        "archetype":     archetype,
        "variant":       variant,
        "accent":        accent,
        "niche_matched": niche,
        "template_key":  f"{archetype}_{variant}",
    }
