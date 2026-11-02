export const dynamic = 'force-static';

export function GET() {
  return new Response(JSON.stringify({
    linkset: [{
      anchor: 'https://docs.smartify.in/api/search',
      'service-desc': [{ href: 'https://docs.smartify.in/openapi.json', type: 'application/vnd.oai.openapi+json' }],
      'service-doc': [{ href: 'https://docs.smartify.in/llms.txt', type: 'text/plain' }],
    }],
  }), { headers: { 'Content-Type': 'application/linkset+json; profile="https://www.rfc-editor.org/info/rfc9727"' } });
}
