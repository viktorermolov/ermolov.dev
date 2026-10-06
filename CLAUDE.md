# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
hugo server                                   # local dev server with live reload (http://localhost:1313)
hugo --environment production --destination /tmp/ermolov-site
python3 scripts/check_site.py /tmp/ermolov-site   # generated HTML, links, structured data, project pages, SEO
node --check assets/js/app.js
cd services/worker && npm ci && npm run check     # typecheck, vitest, wrangler dry-run (parked, see below)
cd services/relay && python3 -m unittest discover -s tests -v   # parked, see below
```

Build into a temporary destination for checks; `public/` is gitignored and never committed.

## Deploy pipeline

Push `master` to GitHub → DigitalOcean App Platform runs `hugo` automatically → serves `public/`. Hugo is pinned in `.hugo-version`. GitHub Actions (`.github/workflows/check.yml`) checks the site, Worker and relay; confirm the branch is green before publishing `master`.

**Workflow with Viktor:** he sets the goal, you lead the work; don't ask about small things, collect real open decisions into one short list.
- Substantial changes (repositioning, redesign, new site sections): a branch and a PR, merged only after Viktor approves.
- Smaller changes: commit to `master` so Viktor can check them on the live site and iterate. Prepare everything (build, `check_site.py`, a short note on what changes and what to check live), then stop right before `git push`: the push deploys, and Viktor gives the go-ahead.
- After every deploy, verify production yourself; Viktor should not have to check. Fetch the homepage, `/clipstay/` and `/clipstay/privacy/` without a query string and confirm they serve the new version. DigitalOcean's CDN (`Cache-Control: s-maxage=86400`) can keep serving an old copy of some URLs for 20–60 minutes after a deploy, so if a page is stale, compare against the same URL with `?cb=<commit>` (fresh means the build is right and it is CDN lag), recheck later, and report only if it is still stale after about an hour. No screenshots unless asked.
- If a deploy clearly broke the live site, revert to the last working commit and push without waiting, then report.
- Money, deleting data and cloud resources always need Viktor's explicit confirmation.

## What the site is

ermolov.dev is the home of Viktor Ermolov's own software products (currently Chrome extensions). The site shows the products and hosts each product's pages: description, support and privacy policy. Site copy is English. Keep the tone positive and plain; describe what the products do. Do not add blocks about the developer's approach, principles or availability, and do not mention client work or services, even to rule them out.

## Architecture

Hugo site. Active templates in `layouts/`:
- `_default/baseof.html`: document shell (head, sticky header, main block, footer, fingerprinted JS)
- `_default/legal.html`: legal pages such as the Clipstay privacy policy (`schemaType: WebPage`)
- `partials/head.html`: SEO/meta, favicons, font preload, JSON-LD for every page type, fingerprinted CSS, pre-paint theme init, Cloudflare Web Analytics beacon
- `partials/header.html`, `footer.html`, `brand-mark.html`
- `partials/project-row.html`, `project-status.html`: homepage project row and the visitor-facing status chip
- `index.html`: homepage (hero → projects → engineering notes, only when notes exist → contact). It shows the products; no principles, services or about blocks. The hero is text only and product-neutral (no product visuals or links to one product): the Projects list is the showcase and should start on the first screen.
- `404.html`: not-found page (noindex)
- `project/single.html`: product page (hero, what it does, privacy, free plan, good to know, support with FAQ)
- `notes/single.html`, `notes/list.html`: engineering notes (BlogPosting / CollectionPage schema). There are no notes right now: the three service-era notes were removed in October 2026. The homepage section and the Notes links in the header and footer appear automatically once `content/notes/` has a published note; add `content/notes/_index.md` with a description at the same time.
- `robots.txt`

Header and footer anchors use `/#section` off the homepage. `scripts/check_site.py` checks every generated page (self-canonical, one h1, schema, local links and cross-page anchors, sitemap equals the generated pages) plus the rules below.

**Styling and JS:** `assets/css/main.css` is the sole custom stylesheet (Hugo Pipes); breakpoints are 960, 720 and 400 px. Fonts are self-hosted OFL variable fonts in `static/fonts/` (Bricolage Grotesque for headings and interface, Newsreader for reading text). Light/dark theming uses CSS custom properties on `:root[data-theme]`; the palette is blue. `assets/js/app.js` handles the theme toggle and the optional copy-address button. Content stays visible without JavaScript and email is always available.

## Content model: projects

Each product is **one markdown file** in `content/` with `type: project` (see `content/clipstay.md`, which documents every field). The homepage builds its rows from those files, sorted by `weight`; adding a product means adding one file plus its icon and screenshots under `static/img/<slug>/`. Product pages keep a stable URL (`url:` in front matter).

- `status` is `pending-review`, `live` or `archived`. **The site never shows "Pending review".** Until `live`, visitors see "Coming soon to the Chrome Web Store" and no store link. Switching to `live` shows the store link and adds `installUrl` to the schema.
- Product pages carry SoftwareApplication schema (`applicationCategory: BrowserApplication`, `operatingSystem: Chrome`). `check_site.py` validates it, the homepage row, the privacy link and the store-link rules.
- **`/clipstay/privacy/` must never change address.** It is listed in the Chrome Web Store, and `check_site.py` fails if it moves. Update its text and its `date` whenever the extension's data handling changes, and keep it accurate for the shipped extension. The policy covers the extension; the website's analytics are described in its "This website" section.
- Do not add placeholder projects. Only show products Viktor has approved (BytLot is intentionally not shown).
- Do not publish prices until a paid plan exists.

Engineering notes and any first-person text are published under Viktor's name: get his approval on new or rewritten text before merging to `master`. Notes should be about his own products and how they are built, not advice for clients.

**Name and location:** the visible brand is `brand` in `config.toml` ("Viktor E."). The full name stays in `author` for structured data, meta author and the copyright line. Do not add a location line (US-based and similar); `check_site.py` fails on it.

## Visual preference

Do not use personal photographs, portrait illustrations, avatars, or Memoji. Use typography, spacing, rules and restrained abstract graphics. Do not add floating bottom call-to-action bars that cover page content. Keep the blue palette.

## Parked inquiry infrastructure

The contact form was removed from the site (October 2026). `services/worker/` (Cloudflare Worker + D1 + Turnstile) and `services/relay/` (Raspberry Pi relay → Notification Bot → Telegram) are still deployed and still have tests and CI jobs, but nothing on the site uses them. **Do not modify, disable or delete the Worker, D1, Turnstile widget, relay or Bot source without Viktor's explicit confirmation.** Decommissioning is a separate step with its own plan of what is removed and what is lost. Until then: use only Free-tier resources and no paid upgrades; never log credentials, request bodies or personal information; never expose the Pi or Bot API to the Internet; keep `robots.txt` disallowing `/api/`. See `docs/OPERATIONS.md`.

**Site metadata** (name, bio, social links, analytics token) lives in `config.toml` under `[params]` and `[params.contact]`. Public tokens are not secrets.
