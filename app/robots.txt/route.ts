export const dynamic = 'force-static';

export function GET() {
  // Match smartify.in's published policy; this host serves public docs only.
  return new Response(`User-agent: *
Content-Signal: search=yes, ai-input=yes, ai-train=no
Allow: /

Sitemap: https://docs.smartify.in/sitemap.xml
`, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}
