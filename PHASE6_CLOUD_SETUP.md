# ☁️ Phase 6: Cloud Automation (Paused)

**Status:** Deferred until budget is available for a $5/mo VPS.

When you are ready to completely automate your lead generation engine (so it runs 24/7 without your laptop being open), follow these steps:

## Option 1: Cheap VPS (Recommended)
1. Go to **DigitalOcean**, **Hetzner**, or **Linode** and rent a basic Linux server (Ubuntu) for about $4-$6/month.
2. SSH into the server and install Python and Playwright.
3. Clone your `static-armstrong` repository onto the server.
4. Copy your `.env` file to the server.
5. Set up **Cron Jobs** (`crontab -e`) to run your scripts automatically:
   - Run `find_leads.py` every day at 8:00 AM.
   - Run `auto_submit.py` every day at 10:00 AM.
   - Run `inbox_monitor.py` every hour.
   - Run `follow_up.py` every day at 2:00 PM.

## Why not Supabase Edge Functions?
Your scripts use **Playwright** (which requires a real browser environment) to bypass complex contact forms. Serverless edge functions (like Supabase or Vercel) generally cannot run full browser instances reliably without significant configuration or paid third-party APIs (like Browserless.io). 

A cheap VPS gives you a full virtual computer to run headless Chrome via Playwright flawlessly.

---

*When you have the budget, just tell Antigravity:*
**"I'm ready for Phase 6. Let's set up the VPS."** 
*and we will walk through the server setup together.*
