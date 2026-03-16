import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.7.1"

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!

serve(async (req) => {
  const url = new URL(req.url)
  const slug = url.pathname.split('/').pop()?.replace('.html', '')

  if (!slug) {
    return new Response("Missing slug", { status: 400 })
  }

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
  const filename = `${slug}.html`
  const bucket = 'landing-pages'

  const { data, error } = await supabase.storage
    .from(bucket)
    .download(filename)

  if (error || !data) {
    return new Response("Site not found", { status: 404 })
  }

  return new Response(data, {
    headers: { 
      "Content-Type": "text/html; charset=utf-8",
      "Access-Control-Allow-Origin": "*"
    }
  })
})
