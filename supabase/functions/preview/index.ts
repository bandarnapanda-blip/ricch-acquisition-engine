// supabase/functions/preview/index.ts
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE_KEY = Deno.env.get("PROXY_SERVICE_ROLE_KEY")!;

Deno.serve(async (req) => {
  const url = new URL(req.url);
  const id = url.searchParams.get("id");
  if (!id) return new Response("Missing ID", { status: 400 });

  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/leads?id=eq.${id}&select=preview_html`, {
      headers: { "apikey": SERVICE_ROLE_KEY, "Authorization": `Bearer ${SERVICE_ROLE_KEY}` }
    });
    const rows = await res.json();
    if (!rows?.[0]?.preview_html) return new Response("Not Found", { status: 404 });

    // THE HAIL MARY: Barebones response with NO extra security headers that might trigger a sandbox
    return new Response(rows[0].preview_html, {
      headers: {
        "Content-Type": "text/html",
        "X-Content-Type-Options": "nosniff"
      }
    });
  } catch (e) {
    return new Response(String(e), { status: 500 });
  }
});
