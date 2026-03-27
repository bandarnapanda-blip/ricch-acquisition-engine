# RI2CH AGENCY OS — ANTI-BAN & RISK PROTOCOL (UPDATED)
# File: .agent/rules/ANTI_BAN.md
# Read by: Silas + Sarah + Inbox Agent before every outreach session
# Updated: Multi-account + two-track system

---

## THE TWO TRACKS — UNDERSTAND THIS FIRST

Everything in this system runs on one of two tracks.
The rules are completely different for each.

TRACK 1 — COLD OUTREACH
  Who:    Businesses you scraped. They did not ask to hear from you.
  Tool:   Gmail SMTP via silas_accounts.py
  Rules:  Hard daily limits. Account rotation. Domain cooldowns.
          Anti-Ban rules apply in full. Treat these accounts like gold.

TRACK 2 — WARM OUTREACH
  Who:    Anyone who paid $47 for the audit report.
          Anyone who replied to a cold email positively.
          Anyone who hit the CTA on their shadow site.
          Anyone who filled in a form on any RI2CH page.
  Tool:   Dedicated warm Gmail account (SMTP_WARM_USER)
  Rules:  No daily sending limits. No Anti-Ban restrictions.
          They gave you their email voluntarily. Follow up freely.
          Still follow good email practice but no volume ceiling.

The warm account is completely separate from the cold accounts.
Mixing them is the biggest mistake you can make.
Never send cold outreach from the warm account.
Never send warm follow-ups from the cold accounts.

---

## THE ACCOUNT STRUCTURE

### Right Now (Month 1)

  Account 1 (cold):   Your existing Gmail
                      Niches: Law, Dental, Medical
                      Limit:  20/day (warming phase)

  Warm account:       Second Gmail dedicated to warm traffic
                      All $47 audit emails go here
                      All auto-close emails go here
                      All delivery and retainer emails go here
                      No daily limit

### Month 2 (add this)

  Account 2 (cold):   New Gmail, start warming now
                      Niches: Solar, Roofing, HVAC, Plumbing
                      Week 1: 5/day then Week 4: 40/day

### Month 3 (add this)

  Account 3 (cold):   New Gmail, start warming in Month 2
                      Niches: Wealth, Finance, Interior, Landscaping
                      Week 1: 5/day then Week 4: 40/day

### Month 3 Combined Capacity

  Account 1:   50/day (established)
  Account 2:   50/day (established)
  Account 3:   30/day (building)
  Total cold:  130/day
  Warm:        Unlimited

---

## DAILY LIMITS BY ACCOUNT AGE

Use this to set SMTP_ACCOUNT_X_DAILY_LIMIT in your .env

  Brand new week 1:    5 to 10 per day (personal emails only)
  Week 2:              10 to 20 per day (mix personal and first cold)
  Week 3:              20 to 30 per day (full cold begins)
  Week 4:              30 to 40 per day (established)
  Month 2 onwards:     40 to 50 per day (full operating capacity)

Never jump from week 1 straight to 50 per day.
The warmup is not optional. It is what keeps the account alive.

---

## THE NICHE ASSIGNMENT RULE

Each cold account targets different niches.
This is not just for organisation. It is protection.

If Account 1 and Account 2 both target Law leads in LA
and a firm receives emails from two different addresses
from what looks like the same agency —
they flag it. Both accounts get reported. Both burn.

Niche assignment prevents this completely.
One niche. One account. No overlap.

---

## SILAS — DAILY SENDING RULES

Before every send batch silas_accounts.py checks:

  1. Is this lead on the DNC list? Skip.
  2. Was this domain contacted today? Skip (24h cooldown).
  3. Which account covers this niche? Select it.
  4. Has that account hit its daily limit? Skip or use next account.
  5. Is the shadow site link Vex-verified? Must be HTTP 200.
  6. Total sends today (new plus follow-ups) under limit? Proceed.

Follow-up emails count toward the daily limit.
If Account 1 sends 15 new Step 1 emails
and 10 Step 2 follow-ups
= 25 total = at the limit for that account.

---

## CONTENT SAFETY RULES

These apply to ALL cold emails regardless of account.

Never use in subject lines:
  Free, Guaranteed, Act Now, Urgent, Winner, Special Offer,
  No Obligation, Risk Free, 100%, Make Money, $$$

Always include:
  Business name in sentence one
  City reference in the email
  One specific data point from Diamond (revenue leakage number)
  Unsubscribe line in footer
  Agency name and location in footer

Email structure for Step 1 cold email:
  Plain text only (no HTML, no images, no attachments)
  Maximum 150 words
  One link only (the shadow site URL)
  No tracking pixels in cold emails (adds to spam score)

---

## SEQUENCE TIMING RULES

  Step 1:   Day 0
  Step 2:   Day 3 minimum (not Day 2)
  Step 3:   Day 6 minimum
  Step 4:   Day 10 minimum
  Step 5:   Day 15 minimum (breakup email)

Never two steps to same lead within 48 hours.
After Step 5 with no reply move to DNC automatically.
Do not restart a sequence on a non-responding lead.

---

## SARAH — HEALTH MONITORING

Sarah checks these numbers after every send batch.

  Bounce rate:       Must stay under 2%
  Spam complaints:   Must stay under 0.1%
  Delivery rate:     Should be above 85%

If bounce rate hits 2%:
  Stop sending from that account immediately
  Clean the lead list and remove all hard bounces
  Wait 48 hours before resuming at half volume

If spam complaints hit 0.1%:
  Stop sending immediately
  Review last 20 subject lines
  Check SPF and DKIM configuration
  Wait 48 hours before resuming

---

## EMERGENCY PROTOCOL

Signs an account is being flagged:
  Delivery rate drops below 60%
  Gmail shows security warning in account
  Reply rate drops to near zero despite correct sends

What to do:
  1. Stop cold sends from that account immediately
  2. Switch that niche to another account temporarily
  3. For 72 hours send only personal emails from the flagged account
  4. After 72 hours resume cold sends at 10 per day maximum
  5. Rebuild over 2 weeks back to full limit

What NOT to do:
  Do not create a new account on same IP immediately
  Do not blast from a new domain right away
  Do not ignore it and keep sending — you will lose the account permanently

---

## DNC TABLE — INBOX AGENT RESPONSIBILITY

Any reply containing these phrases triggers immediate DNC:
  remove me, unsubscribe, stop emailing, not interested,
  wrong person, do not contact, take me off, spam

On detection:
  Inbox Agent marks lead status as DNC in Supabase
  Silas checks DNC before every send
  Lead never contacted again from any account
  Log entry written to activity_logs

CAN-SPAM fine for ignoring unsubscribe: up to $50,120 per violation.

---

## THE WARM ACCOUNT RULES

No daily limit but still follow these:

  Never send bulk identical emails to warm contacts
  Personalise every warm email with their business name
  Space follow-ups sensibly (not 3 emails in one day)
  If a warm contact asks to stop add to DNC immediately
  All $47 audit emails from warm account only
  All payment confirmations from warm account only
  All delivery emails from warm account only
  All retainer offers from warm account only
  All monthly reports from warm account only

---

## DAILY CAPACITY AND REVENUE PROJECTION

  Now 1 cold account:     20 cold per day + unlimited warm
  Month 2 two cold:       100 cold per day + unlimited warm
  Month 3 three cold:     130 cold per day + unlimited warm

  Cold emails x 30 days x 3% reply rate = monthly replies
  Month 1:  20 per day = 600 per month = 18 replies = 3 closes = $4,500
  Month 2: 100 per day = 3,000 per month = 90 replies = 14 closes = $21,000
  Month 3: 130 per day = 3,900 per month = 117 replies = 19 closes = $28,500

Plus warm channel closes on top of every one of those numbers.

---

## .env CONFIGURATION TEMPLATE

  # Cold Account 1 (your existing Gmail)
  SMTP_ACCOUNT_1_USER=your-existing@gmail.com
  SMTP_ACCOUNT_1_PASS=xxxx-xxxx-xxxx-xxxx
  SMTP_ACCOUNT_1_NICHES=Law,Dental,Medical
  SMTP_ACCOUNT_1_DAILY_LIMIT=20

  # Cold Account 2 (create and start warming now)
  SMTP_ACCOUNT_2_USER=new-cold@gmail.com
  SMTP_ACCOUNT_2_PASS=xxxx-xxxx-xxxx-xxxx
  SMTP_ACCOUNT_2_NICHES=Solar,Roofing,HVAC,Plumbing
  SMTP_ACCOUNT_2_DAILY_LIMIT=5

  # Warm Account (create now, dedicated to inbound)
  SMTP_WARM_USER=warm-outreach@gmail.com
  SMTP_WARM_PASS=xxxx-xxxx-xxxx-xxxx

  # Legacy fallback (keeps existing code working)
  SMTP_USER=your-existing@gmail.com
  SMTP_PASS=xxxx-xxxx-xxxx-xxxx

---

## INTEGRATION

Replace direct smtplib calls with:
  auto_close.py        use send_warm_email()
  payment_webhook.py   use send_warm_email()
  retainer.py          use send_warm_email()
  audit_report.py      use send_warm_email()
  silas_sequences.py   use send_cold_email()

Import:
  from silas_accounts import send_cold_email, send_warm_email, print_daily_status

Add to Briefing:
  from silas_accounts import get_daily_status
  print_daily_status()
