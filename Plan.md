# StartResearching — Squarespace Replacement Plan

For: Sherri (review before any domain/DNS change)
Project: `/Users/mikemastrangelo/Projects/StartResearching` (Astro 5, static)
Live site today: https://www.startresearching.com/ (Squarespace)

## 1. Goal

Replace Squarespace with a fast, free-hosted static site, keeping:
- Same URL: `https://www.startresearching.com/` (no change for visitors)
- Same sections: 10 Steps, Blog, Databases, DNA Testing, Records, Templates, GPS, etc.
- Same content: ~204 pages (from `sitemap.xml`) + blog RSS already staged in `tmp/`
- Etsy shop links unchanged

## 2. What exists now

- Astro scaffold builds clean (`npm run build` → `dist/`):
  - `/` , `/10-steps/` , `/blog/` , `/blog/welcome/`
- Nav mirrors live Squarespace menu (`src/components/Nav.astro`)
- Content collections: `src/content/blog/*.md`, `src/content/guides/*.md`
- Migration staging:
  - `content-inventory.txt` — 204 live URLs
  - `tmp/*.xml` — full blog RSS (~295KB)
  - `scripts/import-squarespace.mjs` — `npm run import:squarespace`
- Next: parse RSS → Markdown, preserve `/blog/<slug>` URLs for SEO

## 3. Will the URL still say startresearching.com? Yes.

All hosts below support **custom domains with free HTTPS**.
Visitors still see `https://www.startresearching.com/` — nothing changes in the address bar.

How it works:
1. We deploy `dist/` to the new host (e.g. `mikemas.github.io/StartResearching` or `startresearching.pages.dev` as a staging URL).
2. Sherri (or Mike) updates DNS once, at the current DNS provider:
   - Today: `www` → `ext-sq.squarespace.com` (198.49.23.144/145, 198.185.159.144/145), DNS via NSONE, registrar Tucows (via Squarespace Domains).
   - After: `www` → CNAME to new host (e.g. `username.github.io` or `pages.dev`), apex `startresearching.com` → A/ALIAS records from host docs.
3. Host auto-issues SSL (Let's Encrypt). Wait 5 min – 24 hr, verify `https://www.startresearching.com/` loads from new host.
4. Cancel/downgrade Squarespace only after verification. Rollback = flip DNS back to Squarespace.

Sherri action required: approve DNS change + provide registrar login (Squarespace Domains) at cutover time. No action needed until staging site is approved.

## 4. Free hosting options

| Host | Free tier | Custom domain + SSL | Pros | Cons |
|---|---|---|---|---|
| **Cloudflare Pages (recommended)** | Unlimited static bandwidth, 500 builds/mo, 20k files, no card | Yes, free | Fastest CDN, generous, easy rollback | Build queue is 1 at a time |
| **GitHub Pages** | 1GB site, ~100GB/mo bandwidth, 10 builds/hr, public repo free | Yes, free | Simplest (we already use GitHub `mikemas`), Actions deploy | Static only, private repo needs Pro |
| Azure Static Web Apps Free | 100GB bandwidth, 0.5GB/app, 2 domains | Yes, free | Auto GitHub Actions, PR previews | Hobby only, no SLA |
| Firebase Hosting (Spark) | 10GB storage, ~10GB/mo transfer | Yes, free | Good if already on Google | Daily 360MB cap |
| AWS Amplify | 12-mo free for new accts (1000 build-min, 5GB, 15GB/mo), then pay | Yes, free SSL | Full AWS power | Needs credit card, can bill |
| Netlify / Vercel Free | ~100GB bandwidth, 300 build-min | Yes, free | Nice previews | Stricter limits than Cloudflare |

Recommendation: **Cloudflare Pages** for production, **GitHub Pages** as zero-config alternative. Both keep `https://www.startresearching.com/`.

## 5. Cutover checklist (no downtime)

- [ ] Approve staging URL (e.g. `startresearching.pages.dev`)
- [ ] Finish RSS → Markdown import, check top 10 posts + images
- [ ] Add 301 redirects for old Squarespace paths (`/10-steps`, `/databases/*`, etc.)
- [ ] Lower DNS TTL to 5 min a day before cutover
- [ ] Point `www` CNAME + apex records to new host, enable HTTPS enforce
- [ ] Verify: homepage, blog post, guide, Etsy link, contact, sitemap.xml, robots.txt
- [ ] Keep Squarespace live 7–14 days, then downgrade

## 6. Costs / risks

- Hosting: $0 on any option above. Domain renewal stays as-is (Tucows, expires 2027-01-10).
- Risks: image URLs still on `images.squarespace-cdn.com` (hotlink OK short-term, should self-host later); SEO dip if slugs change (mitigated by preserving slugs + redirects).

## 7. Decision needed from Sherri

1. Approve this plan + staging preview?
2. Preferred host: Cloudflare Pages (recommended) or GitHub Pages?
3. OK to proceed with full blog import (205 posts) before DNS change?
