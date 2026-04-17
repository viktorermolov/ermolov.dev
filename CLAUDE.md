# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
hugo server          # local dev server with live reload (http://localhost:1313)
hugo                 # build to public/ (gitignored — done by DigitalOcean on deploy)
```

## Deploy pipeline

Push to GitHub → DigitalOcean App Platform runs `hugo` automatically → serves `public/`. Never commit `public/`.

## Architecture

Single-page Hugo portfolio at [ermolov.dev](https://ermolov.dev). No `content/` directory — the entire page is a single template.

**Two layout layers (root overrides theme):**
- `themes/vncnt-hugo/` — upstream theme, kept for reference but effectively bypassed
- `layouts/` — active templates that override the theme entirely:
  - `_default/baseof.html` — shell: sticky header, theme-toggle JS (localStorage + `prefers-color-scheme`), footer
  - `index.html` — full homepage: hero → skills → projects → about → contact sections
  - `partials/icons/x.html` — inline SVG for the X (Twitter) logo (Font Awesome has no X icon)

**Styling:** `static/css/main.css` is the sole custom stylesheet. Light/dark theming uses CSS custom properties on `body[data-theme]`. Responsive breakpoints: 600 px (2-col hero) and 900 px (3-col grids). Theme libraries (`normalize.css`, `fonts.css`, `all.min.css`) live in `themes/vncnt-hugo/static/css/` and are copied to `public/css/` at build time.

**Projects section:** Falls back to hardcoded placeholder projects. To supply real data, create `data/projects.toml` (or `.yaml`/`.json`) with a top-level `items` array — each item: `title`, `description`, `tech`, `link`.

**Site metadata** (name, bio, social links) lives in `config.toml` under `[params]` and `[params.contact]`.
