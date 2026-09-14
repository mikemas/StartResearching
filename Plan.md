# StartResearching — Squarespace Replacement Plan

For: Sherri (review before any domain/DNS change)
Project: `/Users/mikemastrangelo/Projects/StartResearching` (Astro 5, static) — https://github.com/mikemas/StartResearching
Live site today: https://www.startresearching.com/ (Squarespace)

Flow: test locally → test on a free staging URL → point the domain over only after approval.

## 1. Goal

**Full replacement of startresearching.com — every page and every functional block working before DNS cutover.** Not just content and look: comments, contact/job forms, ads, analytics, search, and social widgets must all work on the new site. Nothing launch-blocking may be skipped; any cut feature needs explicit sign-off. Section 6 is the launch gate.

Keeping:
- Same URL: `https://www.startresearching.com/` (no change for visitors — see FAQ)
- Same sections: 10 Steps, Blog, Databases, DNA Testing, Records, Templates, GPS, etc.
- Same content: ~204 pages (from `sitemap.xml`) + blog RSS already staged in `tmp/`
- Etsy shop links unchanged

## 2. Local Testing

Yes — you need a small local server, but not a real deployment. Chrome is the browser; Node.js is the server.

Prereqs (one time):
- Node.js 20+ installed (this machine has v26 via Homebrew)
- In the project folder, first time only: `npm install`

Run the dev site (live reload while editing):

```bash
npm run dev
```

Then open http://localhost:4321/ in Chrome. Stop with Ctrl+C.

Check the real production build (what visitors would get):

```bash
npm run build
npm run preview
```

Then open http://localhost:4321/ in Chrome. (Verified: `/` and `/blog/` return 200.)

Notes:
- The server must be running in the terminal while you browse locally.
- Don't just double-click files in `dist/` — links and assets assume a server, so use `npm run preview` instead.
- Nothing you do locally affects the live Squarespace site.

What to check locally: homepage loads, nav links work, `/10-steps/` guide renders, `/blog/` lists posts, a blog post renders, Etsy/Contact links present.

## 3. Test on Hosted Site (staging — before touching the domain)

No manual uploading. You `git push`, the host builds and publishes automatically.

Sign-ups needed:
- **GitHub Pages:** nothing new — repo already exists at https://github.com/mikemas/StartResearching (public, free Pages-eligible).
- **Cloudflare Pages:** free Cloudflare account (email signup, no credit card), then connect the repo.

Staging URLs (these are temporary preview addresses — the real domain still points to Squarespace until go-live):
- GitHub Pages: `https://mikemas.github.io/StartResearching/`
- Cloudflare Pages: `https://startresearching.pages.dev` (generated name)

Steps (GitHub Pages path):
1. Deploy workflow exists (`.github/workflows/deploy.yml`): every push to `main` builds with `PAGES_BASE=/StartResearching` and publishes `dist/`.
2. One-time: repo Settings → Pages → Source: GitHub Actions (or API-enable it).
3. Every push to `main` redeploys in ~1–2 min. Share the staging URL with Sherri for approval.

What to verify on staging: same checks as local (Section 2), plus phone/mobile layout, `sitemap.xml`/`robots.txt` present, and no Squarespace editor chrome leaking through.

## 4. Free hosting options

| Host | Free tier | Custom domain + SSL | Pros | Cons |
|---|---|---|---|---|
| **Cloudflare Pages (recommended)** | Unlimited static bandwidth, 500 builds/mo, 20k files, no card | Yes, free | Fastest CDN, generous, easy rollback | Build queue is 1 at a time |
| **GitHub Pages** | 1GB site, ~100GB/mo bandwidth, 10 builds/hr, public repo free | Yes, free | Simplest (repo already exists), Actions deploy | Static only, private repo needs Pro |
| Azure Static Web Apps Free | 100GB bandwidth, 0.5GB/app, 2 domains | Yes, free | Auto GitHub Actions, PR previews | Hobby only, no SLA |
| Firebase Hosting (Spark) | 10GB storage, ~10GB/mo transfer | Yes, free | Good if already on Google | Daily 360MB cap |
| AWS Amplify | 12-mo free for new accts (1000 build-min, 5GB, 15GB/mo), then pay | Yes, free SSL | Full AWS power | Needs credit card, can bill |
| Netlify / Vercel Free | ~100GB bandwidth, 300 build-min | Yes, free | Nice previews | Stricter limits than Cloudflare |

Recommendation: **Cloudflare Pages** for production, **GitHub Pages** as zero-config alternative. Both keep `https://www.startresearching.com/`.

## 5. Go-live checklist (only after staging is approved AND section 6 is all-Done)

- [x] Content import done (50 posts + 266 guide pages), top posts + images spot-checked
- [ ] Section 6 functionality gate all-Done (or explicit cuts signed off)
- [ ] Add redirects for old Squarespace paths (`/10-steps`, `/databases/*`, etc.)
- [ ] Lower DNS TTL to 5 min a day before cutover
- [ ] Point `www` CNAME + apex records to new host, enforce HTTPS
- [ ] Verify on the real domain: homepage, blog post, guide, Etsy link, contact, sitemap.xml, robots.txt
- [ ] Keep Squarespace live 7–14 days, then downgrade. Rollback = flip DNS back.

## 6. Functionality gate — all rows must be Done or explicitly cut before launch

Audited from the live site (comments are Squarespace-native, forms post to Squarespace,
ads are AdSense + Media.net). Visual/content parity alone is NOT sufficient.

| # | Feature | Live implementation | Replacement | Status |
|---|---|---|---|---|
| 1 | Blog comments (50 posts) | Squarespace native (Disqus shortname empty) | Disqus free embed below each post | Built — activates when Sherri's shortname goes in `src/config.ts` |
| 2 | Contact form (name/email/message + address + phone → her email) | Squarespace backend | Identical UI, POST to Formspree | Built — activates on Formspree ID + her email confirmation |
| 3 | Job-submit form (jobs post) | Same backend | Same Formspree form, flagged subject | Built — same activation |
| 4 | Ads | AdSense `ca-pub-8442952758105071` (Auto Ads + responsive units) + Media.net `8CUEF9XKU` | Same IDs, matching placements + Auto Ads script | Built — Sherri must approve new domain in both dashboards |
| 5 | FB widget + follower count | FB Page plugin (live data) | Already live-data | Done |
| 6 | Donate page body | Static text (importer saved empty stub) | Re-import real body | Done (Donate Now button needs her Stripe payment link in `src/config.ts`) |
| 7 | Analytics | GA4 `G-Z559SPN1JF` | Same ID (works immediately) | Done |
| 8 | Social share buttons | Hidden by her own CSS | Stay hidden (faithful) | Done |
| 9 | Search, Etsy links, sitemap/robots | — | Done | Done |

- [x] Content import done (50 posts + 266 guide pages), top posts + images spot-checked
- [ ] Add redirects for old Squarespace paths (`/10-steps`, `/databases/*`, etc.)
- [ ] Lower DNS TTL to 5 min a day before cutover
- [ ] Point `www` CNAME + apex records to new host, enforce HTTPS
- [ ] Verify on the real domain: homepage, blog post, guide, Etsy link, contact, sitemap.xml, robots.txt
- [ ] Keep Squarespace live 7–14 days, then downgrade. Rollback = flip DNS back.

## 7. FAQ

**Will the URL still say https://www.startresearching.com/? Yes.**
All hosts above support custom domains with free HTTPS. Visitors see the same address — nothing changes in the address bar.

**How does the domain switch work?**
1. We deploy to a staging URL first (Section 3).
2. Once approved, the DNS records are updated once at the current DNS provider. Today: `www` → `ext-sq.squarespace.com` (DNS via NSONE, registrar Tucows through Squarespace Domains). After: `www` → CNAME to the new host, apex → host records.
3. The host auto-issues SSL. Propagation takes 5 min – 24 hr.

**What does Sherri need to do?**
Approve the staging preview, then at cutover time provide registrar/DNS access (Squarespace Domains login). Before that, three sign-ups she owns: Disqus shortname (for comments), Formspree email confirmation (contact/job forms), and domain approval in AdSense + Media.net dashboards (or ads serve blank).

**Do we keep paying Squarespace?**
Keep it until the new site is verified on the real domain, then downgrade/cancel hosting. Domain renewal itself stays as-is (Tucows, expires 2027-01-10).

**What about images?**
All 346 images are self-hosted in `public/images/` — zero dependence on Squarespace. Includes gallery lazy-load fix (`data-src` → `src`) and srcset cleanup.

**Will Google rankings break?**
Mitigated by preserving `/blog/<slug>` URLs plus redirects for changed paths. Staging review includes checking top posts.

## 8. Decision needed from Sherri

1. Approve this plan + staging preview?
2. Preferred host: Cloudflare Pages (recommended) or GitHub Pages?
3. OK to proceed with full blog import before any DNS change?

## Appendix A — Build status

Moved here from the old "What exists now" section; will be removed when done.

- [x] Astro 5 scaffold builds clean (`npm run build` → `dist/`): `/`, `/10-steps/`, `/blog/`, `/blog/welcome/`
- [x] Nav mirrors live Squarespace menu (`src/components/Nav.astro`)
- [x] Content collections wired (`src/content/blog/*.md`, `src/content/guides/*.md`)
- [x] `content-inventory.txt` — 204 live URLs from `sitemap.xml`
- [x] Blog RSS staged in `tmp/*.xml` (~295KB) via `npm run import:squarespace`
- [x] Local preview verified (`npm run preview`, 200 on `/` and `/blog/`)
- [x] GitHub repo created: https://github.com/mikemas/StartResearching
- [x] Parse RSS → Markdown posts, preserve slugs (50 published posts imported)
- [x] Add Pages deploy workflow + staging URL (Pages enabled, https://mikemas.github.io/StartResearching/ deploying)
- [x] Images self-hosted (346 files in `public/images/`, render sweep: 0 escaped tags on all pages)
- [ ] Redirects for old Squarespace paths
- [ ] Staging review + Sherri approval
- [ ] DNS cutover, verify, downgrade Squarespace
