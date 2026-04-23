# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Commands

```bash
hugo server          # local dev server with live reload (http://localhost:1313)
hugo                 # build to public/ (gitignored — done by DigitalOcean on deploy)
```

## Deploy pipeline

Push to GitHub → DigitalOcean App Platform runs `hugo` automatically → serves `public/`. Never commit `public/`.

## Architecture

Single-page Hugo service site at [ermolov.dev](https://ermolov.dev). No `content/` directory — the entire page is a single template.

**Active layout layer:**
- `layouts/` — active templates:
  - `_default/baseof.html` — document shell: head partial, sticky header, main block, footer, fingerprinted JS
  - `partials/head.html` — SEO/meta tags, favicons, font preload, JSON-LD, fingerprinted CSS, pre-paint theme init
  - `partials/header.html` — brand, desktop anchor navigation, theme toggle
  - `partials/footer.html` — footer copy and social links
  - `index.html` — homepage: hero → services → case notes → engagement shapes → approach → contact
  - `robots.txt` — generated robots file with sitemap

**Styling and JS:** `assets/css/main.css` is the sole custom stylesheet, processed by Hugo Pipes. `assets/js/app.js` handles theme toggling, reveal-on-scroll, and light interactive polish. Light/dark theming uses CSS custom properties on `:root[data-theme]`. The main responsive breakpoint is currently 720 px.

**Content model:** There is no projects/portfolio data source yet. Do not add placeholder projects. Until real projects exist, position the site as an expertise-led service page and keep case notes framed as engineering decision notes rather than client case studies.

**Site metadata** (name, bio, social links) lives in `config.toml` under `[params]` and `[params.contact]`.
