# Ri2ch Digital: Autonomous Lead Generation Handoff

Welcome to your new autonomous agency engine. Here is how your "employees" operate and what you need to do to turn those leads into $10,000.

## The Workflow

### 1. Daily Lead Generation (The Hound)
**What it does:** Scrapes search engines for local businesses in a specific niche (e.g., Epoxy Flooring) and finds their contact URLs.
**How to run it:**
```bash
# Make sure you are in the project folder and venv is active
python find_leads.py
```
* **Output:** Generates `leads.csv` with a fresh batch of targets.
* **To change targets:** Open `find_leads.py` and modify `SEARCH_QUERY` (e.g., to "Roofing Companies in Dallas, Texas").

### 2. Autonomous Pitching (The Pen & The Ghost)
**What it does:** Reads `leads.csv`, visits their sites to scrape content, uses AI to write a highly targeted pitch about their website, and physically fills out their contact form.
**How to run it:**
```bash
# Note: Ensure you set SET OPENAI_API_KEY=your-key if you want the customized AI pitches, otherwise it will use high-converting fallback pitches.
python auto_submit.py
```
* **Output:** Safely adds contacted leads to `contacted_leads.csv` so you never double-pitch the same business accidentally.

---

## The Hand-off Protocol (CEO's Job)

As the CEO and Closing Specialist, you have the most high-leverage job: closing the warm leads.

1. **Monitor the Inbox:** Check `ri2ch.digital@gmail.com` daily for responses to the contact form submissions.
2. **Review Positive Replies:** If a business owner says "Sure, I'd love to see the prototype link," you have successfully hooked them through the Trojan Horse funnel.
3. **Dispatch The Architect (Antigravity):** When you get a bite, tell me (Antigravity) immediately: *"A lead [Business Name] is interested. Build a modern, high-converting React/NextJS landing page tailored for Epoxy Flooring."*
4. **Deliver & Close:** Once I build their custom prototype, you send them the link. Because they can literally *see* the finished product, the trust barrier is gone, making it incredibly easy to close a high-ticket development deal. 

**Pro-Tip:** Start small (5-10 leads a day) to ensure the system is tuned correctly. Once you secure your first deal, you can seamlessly scale this up to 50+ a day.
