// Production Webhook Handler for Lead Replies
// Deploy to Vercel/Cloud Functions
import { serve } from "https://deno.land/std@0.131.0/http/server.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_KEY = Deno.env.get("SUPABASE_SERVICE_KEY")!;

async function supabaseUpdateLead(leadId: string, patch: Record<string, any>) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/leads?id=eq.${leadId}`, {
    method: "PATCH",
    headers: {
      "apikey": SUPABASE_KEY,
      "Authorization": `Bearer ${SUPABASE_KEY}`,
      "Content-Type": "application/json",
      "Prefer": "return=representation"
    },
    body: JSON.stringify(patch)
  });
  return res.json();
}

serve(async (req) => {
  try {
    const payload = await req.json();
    
    // Extract metadata from provider payload (SendGrid/Postmark/etc)
    const replyText = payload.text || payload.html || payload.body || "";
    const email = payload.from?.email || payload.sender || payload.envelope?.from;
    
    if (!email) {
        return new Response(JSON.stringify({ ok: false, message: "No email identified" }), { status: 400 });
    }

    // 1) Find lead by email
    const lookup = await fetch(`${SUPABASE_URL}/rest/v1/leads?website=ilike.*${encodeURIComponent(email.split('@')[0])}*&select=id`, {
      headers: {
        "apikey": SUPABASE_KEY,
        "Authorization": `Bearer ${SUPABASE_KEY}`
      }
    });
    
    const leads = await lookup.json();
    if (!Array.isArray(leads) || leads.length === 0) {
      return new Response(JSON.stringify({ ok: false, message: "Lead not found" }), { status: 404 });
    }
    const leadId = leads[0].id;

    // 2) Sentiment Analysis (Simplified for Edge)
    const positiveKeywords = ["interested", "yes", "let's", "sure", "book", "call", "hire"];
    const negativeKeywords = ["not interested", "no thanks", "unsubscribe", "stop", "busy"];

    const txt = replyText.toLowerCase();
    let sentiment = "other";
    if (positiveKeywords.some(k => txt.includes(k))) sentiment = "positive";
    else if (negativeKeywords.some(k => txt.includes(k))) sentiment = "negative";

    const patch = {
      reply_at: new Date().toISOString(),
      reply_text: replyText.substring(0, 1000),
      reply_source: "webhook",
      reply_status: sentiment,
      last_stage: "replied",
      status: "Replied"
    };

    await supabaseUpdateLead(leadId, patch);

    return new Response(JSON.stringify({ ok: true, sentiment }), { status: 200 });
  } catch (err) {
    console.error(err);
    return new Response(JSON.stringify({ ok: false, error: String(err) }), { status: 500 });
  }
});
