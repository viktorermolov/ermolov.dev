# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Commands

```bash
hugo server          # local dev server with live reload (http://localhost:1313)
hugo                 # build to public/ (gitignored — done by DigitalOcean on deploy)
python3 scripts/check_site.py public/ # generated HTML, links, form, and SEO
cd services/worker && npm ci && npm run check
cd services/relay && python3 -m unittest discover -s tests -v
```

## Deploy pipeline

Push master to GitHub → DigitalOcean App Platform runs `hugo` automatically → serves `public/`. Hugo is pinned in `.hugo-version`. Never commit `public/`. Check the branch in CI before publishing master.

Deploy the Worker separately using `services/worker/wrangler.jsonc`; apply reviewed D1 migrations first. Deploy the Raspberry Pi relay with `scripts/deploy_relay.sh`, which requires clean Git and tests the candidate image before replacing the service. Runtime credentials stay outside releases. See `docs/OPERATIONS.md`.

## Architecture

Single-page Hugo service site at [ermolov.dev](https://ermolov.dev). No `content/` directory — the entire page is a single template.

**Active layout layer:**
- `layouts/` — active templates:
  - `_default/baseof.html` — document shell: head partial, sticky header, main block, footer, fingerprinted JS
  - `partials/head.html` — SEO/meta tags, favicons, font preload, JSON-LD, fingerprinted CSS, pre-paint theme init
  - `partials/header.html` — brand, desktop anchor navigation, theme toggle
  - `partials/footer.html` — footer copy and social links
  - `index.html` — homepage: hero → services → engagements → process → about → decision notes → FAQ → contact
  - `robots.txt` — generated robots file with sitemap

**Styling and JS:** `assets/css/main.css` is the sole custom stylesheet, processed by Hugo Pipes. `assets/js/app.js` handles theme, service selection, lazy Turnstile loading, accessible form states, and stable submission IDs. Content stays visible without JavaScript; email is always available. Light/dark theming uses CSS custom properties on `:root[data-theme]`.

**Lead delivery:** `services/worker/` owns validation, Turnstile, D1 intake, atomic limits and fenced leases. `services/relay/` polls from Raspberry Pi and calls the existing private Notification Bot. Never mark a lead sent merely because the Bot returned 202; confirm `sent`. Preserve immutable payloads, idempotency keys and notification IDs across retries. Pending data survives restarts. Delivery remains at-least-once.

**Safety and cost:** use only the agreed Free-tier resources; no paid upgrades. Never log credentials, request bodies or personal information. Public keys in Hugo are not secrets. Never expose the Pi or Bot API to the Internet. Keep tests offline with service doubles; only deliberate release smoke checks may create a clearly labelled test inquiry. Keep delivered-data retention and pending-data preservation intact.

**Content model:** There is no projects/portfolio data source yet. Do not add placeholder projects. Until real projects exist, position the site as an expertise-led service page and keep case notes framed as engineering decision notes rather than client case studies.

**Visual preference:** Do not use personal photographs, portrait illustrations, avatars, or Memoji. Use typography, spacing, rules and restrained abstract graphics for the About section and other page content.

**Site metadata** (name, bio, social links) lives in `config.toml` under `[params]` and `[params.contact]`.
