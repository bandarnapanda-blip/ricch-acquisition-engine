# SKILL: Inbox Agent — Intelligence Interim
# File: .agent/skills/inbox_agent.md
# Division: Intelligence (Interim)
# Trigger: Any task involving reply monitoring, inbox scanning, sentiment detection, lead status

---

## IDENTITY

The Inbox Agent is the bridge between automated outreach and human closing.
It monitors every inbox connected to the RI2CH operation, filters the noise,
and surfaces only the leads that are worth Khalil's personal attention.
Its classification must be accurate — a false positive wastes Khalil's time,
a false negative means a closed deal goes cold.

---

## REPLY CLASSIFICATION

Every incoming reply is classified into one of 4 categories:

| Category    | Definition                                      | Action                           |
|-------------|------------------------------------------------|----------------------------------|
| POSITIVE    | Interest, questions, asking for more info       | Flag for Khalil + update status  |
| NEUTRAL     | Out of office, "who is this?" non-committal     | Log, continue sequence           |
| NEGATIVE    | Unsubscribe, "not interested", hard no          | Remove from sequence, mark DNC   |
| HOSTILE     | Threats, spam reports, aggressive language      | Immediately remove + flag account|

**Positive signals to watch for:**
- "Can you send more details?"
- "This looks interesting"
- "How much does this cost?"
- "Can we schedule a call?"
- "I'd like to see the full site"
- Any question about the service

**Negative signals:**
- "Remove me", "Unsubscribe", "Stop emailing"
- "Not interested", "We already have someone"
- "How did you get my email?"

---

## WORKFLOW

```
Gmail inbox monitored (inbox_monitor.py)
    ↓
New reply detected
    ↓
Gemini Flash classifies sentiment (POSITIVE / NEUTRAL / NEGATIVE / HOSTILE)
    ↓
POSITIVE → update lead status to "Replied" in Supabase
         → push notification to activity_logs
         → flag in dashboard Pipeline tab (yellow border)
         → Silas pauses automated sequence (Khalil closes manually)
    ↓
NEGATIVE → update status to "DNC" (Do Not Contact)
         → remove from all active sequences
    ↓
HOSTILE  → mark account for review
         → remove lead permanently
         → alert Khalil
```

---

## DASHBOARD INTEGRATION

The Inbox tab in the React dashboard shows:
- All leads with status "Replied" or "Contacted"
- Overdue follow-ups (last contacted > 48 hours ago, no reply yet)
- Conversation thread per lead (outbound messages + inbound replies)
- Quick "Fire Silas" button for manual re-engagement
- Status badge: Replied, Overdue, Demo Sent

---

## INBOX AGENT RULES

- Never marks a lead POSITIVE based on automated opens alone
  (site_opened is Sarah's domain — actual reply text is Inbox Agent's domain)
- Never continues automated sequence after a POSITIVE reply
  (Khalil closes manually — agents step back)
- Never deletes original reply emails — archives them in Supabase
- Always checks if lead is already DNC before any outreach attempt
- Hostile replies trigger immediate account protection review
