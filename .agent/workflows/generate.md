# WORKFLOW: /generate
# File: .agent/workflows/generate.md
# Trigger: User triggers shadow site generation for one or more leads

---

The correct generation sequence. Never skip steps.
Never call upload_to_netlify() or upload_to_github() directly.
Always go through validate_and_deploy().

---

## SINGLE LEAD GENERATION

```
1. Diamond provides audit JSON for the lead
   (opportunity_score, revenue_loss, niche, city, mobile_score etc.)

2. template_router.py selects archetype based on niche + score
   - Score >= 75 → best archetype for niche
   - Score 60–74 → standard niche routing
   - Score < 60  → Forge/Grove/Alpine default

3. color_shuffler.apply_variant() selects palette
   - Checks sent_designs table — no repeats in same city
   - LLM (Rody) picks based on mood description
   - Returns (html_with_css_vars, palette_name)

4. generate_landing_patch.generate_page() builds the HTML
   - Leo's copy injected per niche
   - Kael's images selected via ImageManager.pick_set()
   - All {{PLACEHOLDERS}} replaced
   - tracking.js injected with lead_id

5. validate_and_deploy() — Vex's Zero-404 Protocol
   - Layer 1: HTML pre-flight (blocks if errors found)
   - Layer 2: Netlify deploy + polling (90s max)
             → GitHub Pages fallback (4min max)
             → Supabase tertiary (instant)
   - Layer 3: Content audit on live page
   - Returns verified URL or None

6. If URL returned:
   - update_lead_demo_link(lead_id, url) → writes to leads table
   - post_deploy_log() → writes to activity_logs
   - color_shuffler.log_palette_used() → prevents future repeats
   - lead status → "Shadow Site Ready"

7. If None returned:
   - lead status → "Generation Error"
   - task queued for retry in tasks table
   - Silas blocked for this lead
```

---

## BATCH GENERATION (135 Whales)

```
1. Query Supabase: SELECT all leads WHERE opportunity_score >= 75
   AND status NOT IN ('Shadow Site Ready', 'Contacted', 'Replied', 'Closed')

2. For each lead → run steps 1–7 above in background worker

3. Rate limiting: 1 Netlify deploy per 3 seconds (avoid API limits)

4. Progress logged to activity_logs after each site

5. On completion: push summary to dashboard
   - Sites generated: X
   - Sites failed: Y
   - Retry queued: Y
```

---

# WORKFLOW: /outreach
# Trigger: User triggers Silas email campaign

---

## OUTREACH SEQUENCE

```
1. Query leads WHERE status = "Shadow Site Ready"
   AND demo_link IS NOT NULL
   AND demo_link != ""

2. Vex double-check: ping demo_link → confirm still returns HTTP 200
   (Sites can go stale — always re-verify before email send)

3. Diamond data retrieved: revenue_loss, opportunity_score, niche, city

4. payments.py generates fresh Paystack link for Step 2 follow-up
   - Never generate payment link for Step 1 (too aggressive)
   - Step 1 is the Trojan Horse only

5. Silas selects email variant:
   - Step 1 template based on niche + archetype
   - Subject line A/B variant selected

6. Sarah compliance check:
   - Spam score verified
   - Sending account bounce rate < 2%
   - Lead not in DNC list
   - Same domain not emailed in last 48h

7. Send via SMTP:
   - Max 40 per Gmail account per day
   - 90 second minimum delay between sends
   - Rotate accounts when limit reached

8. On send:
   - Update lead status → "Contacted"
   - Write pitch_sent = True
   - Log to activity_logs
   - Schedule Step 2 check at +48h

9. At +48h:
   - Sarah checks site_events for this lead_id
   - If cta_reached or scroll_75 → use OPENED variant for Step 2
   - If no events → use UNOPENED variant for Step 2
   - Continue until Step 5 (breakup) or positive reply detected

10. On positive reply (Inbox Agent):
    - Silas sequence paused
    - Lead flagged for Khalil manual close
    - Paystack link delivered in reply
```
