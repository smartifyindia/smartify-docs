# Agent readiness

The Cloudflare Diagnostics hostname selector must be set to `docs.smartify.in`;
the apex site's results do not describe this Worker.

Implemented for this public, read-only documentation site:

- `/robots.txt` permits crawling and advertises the sitemap. Content Signals
  match the existing apex policy: search and AI input allowed, AI training denied.
  These are usage preferences, not authentication or enforcement.
- `/sitemap.xml` and `/llms.txt` derive their page lists from the Fumadocs source,
  excluding the `/docs` redirect, so content additions stay discoverable.
- `/llms-full.txt` serves processed Markdown compiled from the same MDX content
  as the browser pages, including each page's canonical source URL.
- HTTP Link headers advertise the sitemap, LLM index, and API catalog.
- `/.well-known/api-catalog` uses RFC 9727 Linkset JSON to advertise the existing
  public `/api/search` endpoint and its `/openapi.json` specification.
- CI exercises these endpoints against the production Next.js build.

Cloudflare already reported Markdown Negotiation and WebMCP as supported before
these changes. No zone-wide settings or authentication bypasses are required.

Not applicable: signup/auth.md, OAuth discovery/protected resources, outbound bot
signing, DNS agent discovery, A2A cards, agent Skills, or an MCP server card.
This host has no user registration, protected API, outbound agent, or MCP/A2A
server to advertise. It also has no checkout or paywall, so commerce/payment
protocols do not apply. Do not add placeholder endpoints just to raise a score.

Production changes go through the protected PR and Cloudflare Git pipeline in
[deployment.md](deployment.md). Re-scan the docs hostname after release; this beta
scanner's overall score includes protocols that are irrelevant to a docs site.

References:
- https://www.rfc-editor.org/rfc/rfc9727.html
- https://www.fumadocs.dev/blog/mdx-12
