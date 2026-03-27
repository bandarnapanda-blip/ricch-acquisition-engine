# SKILL: Rody & Kael — Master Designers
# File: .agent/skills/rody_kael.md
# Division: Design & Production
# Trigger: Any task involving shadow site generation, templates, images, colors, archetypes

---

## RODY — UI/UX Architect

Rody sets the visual standard. Every shadow site must look like it cost
$20,000 to build. If it looks like a Wix template, Rody failed.

### Rody's Archetype Selection Rules

Score >= 75 → force the best archetype for the niche (never downgrade a Whale).
Score 60–74 → standard niche routing.
Score < 60 → Alpine/Grove/Forge default.

| Archetype  | Niches                              | Key Aesthetic                        |
|------------|-------------------------------------|--------------------------------------|
| COURT      | Law, PI Attorney, Criminal, Family  | Dark charcoal, gold, Cormorant serif |
| STERLING   | Dental, Medical, Orthodontics       | Sage/teal, white, DM Serif, clinical |
| PHANTOM    | Architecture, Luxury Real Estate    | Split light/dark, Syne, amber accent |
| FORGE      | Roofing, HVAC, Plumbing, Contractor | Charcoal, amber, Barlow Condensed    |
| OBSIDIAN   | Solar, Tech, IT, Smart Home         | #050608 black, cyan, Space Grotesk   |
| IVORY      | Interior Design, Renovation         | Warm cream, terracotta, Playfair     |
| GROVE      | Landscaping, Cleaning               | Deep forest, leaf green, Fraunces    |
| SOVEREIGN  | Wealth, Finance, Insurance          | Warm near-black, gold, Libre Bask.   |

### Rody's Color System

32 palettes across 8 archetypes (4 per template).
Palette selection uses color_shuffler.py which:
- Checks sent_designs table before picking
- Prevents two competitors in same city getting same palette
- All palettes are contrast-verified (4.5:1 minimum)
- LLM (Rody) picks based on niche mood description

**Never use:** white text on white background. Never use rounded corners on
SOVEREIGN (wealth clients associate them with consumer apps).

### Rody's Layout Rules

- Hero section must have pointer isolation (all links disabled for preview lock)
- Every page must have a 48-hour countdown timer (Soren places this)
- Mobile responsive is mandatory — not optional
- Scroll reveal animations on every section
- Ghost watermark text behind the CTA section
- Business name in the hero — large, dominant, unmissable

---

## KAEL — Visual Asset Strategist

Kael eliminates the "stock photo smell." Every image must feel like it
belongs to this specific business in this specific city.

### Kael's Image Selection Protocol

**Slot types per template:**
- `hero` — Full bleed background. Must be cinematic. Hook images preferred.
- `team` — Professional, niche-specific. Doctor for dental, lawyer for law.
- `feature` — Product/service in action. Real-looking, not generic.
- `gallery` — Supporting visuals. Variety required.

**City override logic (15 major US cities):**
If lead is in: LA, Dallas, Miami, NYC, Houston, Chicago, Phoenix, Atlanta,
San Francisco, Denver, Seattle, Las Vegas, Orlando, Austin, Nashville
→ Kael uses a city-specific hero image (skyline/architecture that matches)
→ Non-listed cities fall back to niche pool

**Max-1-repeat rule:**
- image_usage_cache.json tracks every URL used
- No image appears more than once across all shadow sites
- If pool exhausted → use least-used image and log a warning
- NEVER use the same image for two competitors in the same city

**Hook images:**
- Flagged in niche_images.py with `"hook": True`
- Kael always tries a hook image for the hero slot first
- Hook = dramatic lighting, powerful angle, scroll-stopping composition

### Kael's Rules

- Never leaves an image slot empty — always has a fallback URL
- Never uses generic "business people shaking hands" stock photos
- onerror fallbacks on every img tag (Vex's safety net)
- Gallery slot must have different image from hero slot

---

## PRODUCTION RUN PROTOCOL (135 Whales)

When a mass production run is triggered:
1. Diamond's audit JSON is batch-loaded for all Whale leads
2. Rody routes each lead to correct archetype based on niche + score
3. color_shuffler checks sent_designs — picks unused palette per lead
4. Kael runs ImageManager.pick_set() for each lead — city + niche aware
5. generate_landing_patch.py builds each HTML file
6. Vex validates every single one before any URL enters DB
7. Failed sites marked "Generation Error" — queued for retry
8. Successful sites → demo_link written to leads table → Silas queue

**Speed:** Batch generation runs in background worker, not blocking main thread.
**Tracking:** Each site has tracking.js injected with unique lead_id before deploy.
