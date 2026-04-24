# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev          # Next.js dev server at localhost:3000
npm run build        # next build only (do NOT add OpenNext here — causes infinite recursion)
npm run cf:build     # Full Cloudflare bundle: next build + @opennextjs/cloudflare
npm run preview      # cf:build + wrangler pages dev (local Cloudflare Worker preview)
npm run deploy       # cf:build + wrangler deploy → docs.smartify.in
python3 generate_docs.py  # Regenerate all MDX from products.json + copy images
```

## Architecture

**Stack:** Next.js 15 · Fumadocs 14 · Tailwind 3 · `@opennextjs/cloudflare` 1.x · Cloudflare Workers

### Content pipeline

All MDX under `content/docs/` is **generated** — never edit it by hand.

1. `smartify-product-catalog/products.json` is the single source of truth
2. `generate_docs.py` reads it and writes all MDX pages + `meta.json` files
3. It also copies product PNGs from `smartify-product-catalog/images/` → `public/images/`
4. Run whenever `products.json` changes: `python3 generate_docs.py`

### Content structure

```
content/docs/
  index.mdx               # top-level welcome page
  getting-started/        # intro guide
  switches/               # TAC series (13 products)
  panels/                 # TOQ + large touch panels (11)
  retrofit/               # relays, dimmers, shutter (9)
  sensors/                # contact, motion, mmWave, vibration (5)
  gateways/               # wired, Matter, VRV, DALI (5)
  ir-blasters/            # WiFi IR + RF variants (3)
  led-controllers/        # CV-RGB+CCT, CC-CCT (2)
```

Each folder has `index.mdx` (category overview + install guide), per-product `.mdx` files, and `meta.json` (controls sidebar order).

### Key files

| File | Purpose |
|---|---|
| `source.config.ts` | Fumadocs MDX config — defines `docs` collection |
| `lib/source.ts` | Fumadocs `loader()` — the `source` object used everywhere |
| `app/docs/[[...slug]]/page.tsx` | Dynamic MDX renderer + per-page SEO metadata |
| `app/api/search/route.ts` | Server-side full-text search (Fumadocs advanced index) |
| `app/layout.tsx` | Root layout — Inter font, global SEO, RootProvider |
| `app/globals.css` | Tailwind + Fumadocs CSS var overrides (teal accent) |
| `generate_docs.py` | Content generator (see above) |
| `wrangler.jsonc` | Cloudflare Worker config — `main: .open-next/worker.js` |
| `open-next.config.ts` | Default OpenNext Cloudflare config |

### TypeScript quirk

Fumadocs 14 doesn't expose `description` / `structuredData` on the base page type. Cast with:
```ts
const data = page.data as unknown as { title: string; description?: string; toc: unknown; ... };
```

## Deployment

Deployed as a **Cloudflare Worker** (not Pages) via OpenNext:
- Account: `Abhi@smartify.in` (`b9f8db8151b55e4e33b0190fd0805f38`)
- `wrangler.jsonc`: `main: .open-next/worker.js`, assets binding at `.open-next/assets`
- Custom domain: `docs.smartify.in`
- `npm run build` must stay as `next build` only — `cf:build` calls it internally

## generate_docs.py gotchas

- MDX frontmatter descriptions containing `:` must be double-quoted → use `yaml_str(s)` helper
- `<` and `>` in MDX table cells must be escaped → use `mdx_safe(s)` helper
- `PRODUCTS_JSON` and `IMAGES_SRC` use absolute paths — update if the product catalog moves
- `CATEGORY_MAP` maps `products.json` category strings → folder slugs. Add entries here when new product categories are introduced.

## Design system

- Primary: `#0FABBB` teal — mapped to `--primary` and `--color-fd-primary` HSL vars in `app/globals.css`
- Font: Inter with weights 300/400/500/600/700 (via `next/font/google`)
- Logo: `public/logo.png` — copied from `../smartify-website/public/images/logo.png`; used in `app/docs/layout.tsx`
- Favicon: `public/favicon.ico` — copied from `../smartify-website/public/favicon.ico`
- Dark mode: `.dark {}` block in `app/globals.css` overrides all Fumadocs `--color-fd-*` CSS variables
- Image handling: `mdx-components.tsx` `img` handler supports both `string` URLs and Next.js `StaticImport` objects (fumadocs-mdx processes local images as StaticImport); never return `null` for non-string src
