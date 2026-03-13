// Projection Cron Job (Daily MRR trajectory)
// Run via GitHub Actions or Cloud Scheduler
import fetch from 'node-fetch';

const SUPABASE_URL = process.env.SUPABASE_URL!;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY!;

async function runProjection(windowDays = 30) {
  console.log(`🚀 Running MRR Projection for last ${windowDays} days...`);
  
  const since = new Date(Date.now() - windowDays * 24 * 3600 * 1000).toISOString();
  
  // 1) Fetch leads with replies in window
  const endpoint = `${SUPABASE_URL}/rest/v1/leads?reply_at=gte.${since}&select=id,monthly_value,reply_status`;
  const res = await fetch(endpoint, {
    headers: { 'apikey': SUPABASE_KEY, 'Authorization': `Bearer ${SUPABASE_KEY}` }
  });
  
  const replies = await res.json() as any[];
  const replyCount = replies.length;
  
  // 2) Calculate average LTV/MRR from recent deals
  const averageMonthlyValue = replies.length 
    ? replies.reduce((s, r) => s + Number(r.monthly_value || 0), 0) / replies.length 
    : 499;

  // 3) Projection Logic: 30% reply -> 30% close rate
  const expected_clients = replyCount * 0.30;
  const expected_mrr = expected_clients * averageMonthlyValue;

  // 4) Store in Projections table
  await fetch(`${SUPABASE_URL}/rest/v1/projections`, {
    method: 'POST',
    headers: { 
        'apikey': SUPABASE_KEY, 
        'Authorization': `Bearer ${SUPABASE_KEY}`, 
        'Content-Type': 'application/json' 
    },
    body: JSON.stringify({ 
        window_days: windowDays, 
        replies: replyCount, 
        expected_clients, 
        expected_mrr 
    })
  });

  console.log('✅ Projection synchronized:', { replyCount, expected_clients, expected_mrr });
}

runProjection().catch(console.error);
