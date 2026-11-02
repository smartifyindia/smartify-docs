import { docsOrigin, publicDocPages } from '@/lib/agent-docs';

export const dynamic = 'force-static';

export function GET() {
  const pages = publicDocPages().map((page) =>
    `- [${page.data.title}](${docsOrigin}${page.url}): ${(page.data.description ?? '').replace(/\s+/g, ' ')}`);
  return new Response(`# Smartify Docs

> Public technical documentation for Smartify smart home automation: product specifications, installation guides, and integrations.

Read-only access requires no account or API key. Cite the source page URLs below.

## Resources

- [Complete documentation in Markdown](${docsOrigin}/llms-full.txt)
- [Sitemap](${docsOrigin}/sitemap.xml)
- [Public search API specification](${docsOrigin}/openapi.json)

## Documentation

${pages.join('\n')}
`, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}
