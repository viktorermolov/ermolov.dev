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
- Smaller changes: they go to `master` so Viktor can check them on the live site and iterate. Prepare everything (build, `check_site.py`, a short note on what changes and what to check live), then wait for Viktor's go-ahead: reaching `master` deploys.
- **Branches are merged through pull requests.** The repository has "Automatically delete head branches" on, and this session cannot delete branches itself (git and the API both refuse), so a merged PR is the only way a branch disappears on its own. Anything waiting for Viktor's go-ahead lives on a pushed branch with an open PR, not as an unpushed local commit; on his "yes", merge the PR with the REST API (`PUT /repos/viktorermolov/ermolov.dev/pulls/<n>/merge`), and GitHub deletes the branch. Do not leave branches without a PR. Create PRs with `gh api` (REST); `gh pr` uses GraphQL, which is blocked here.
- After every deploy, verify production yourself; Viktor should not have to check. A deploy is live on ermolov.dev within a few minutes. Check the homepage, `/clipstay/` and `/clipstay/privacy/`, each with a unique query string (`?v=<commit>`): Claude's web-fetch tool caches responses per exact URL and can return an old copy of a bare URL long after the site has updated (this caused false "stale page" reports in October 2026). If a page with a fresh query string is still old, the deploy itself failed: check the DigitalOcean build, then report. No screenshots unless asked.
- If a deploy clearly broke the live site, revert to the last working commit and push without waiting, then report.
- Money, deleting data and cloud resources always need Viktor's explicit confirmation.

**Boundary with the Clipstay project (since 2026-10-07).**
- This project (ermolov.dev) is the only owner of the site: only it merges to `master`, deploys and verifies production, and it is responsible for the site as a whole (copy, templates, structured data, homepage, sitemap, `check_site.py`).
- The Clipstay project owns the product facts: what the extension does, limits, permissions, keyboard shortcuts, Chrome Web Store status, and the extension's privacy policy. It never pushes to `master` of this repository.
- How Clipstay changes arrive:
  1. For each change, Clipstay creates a fresh branch `clipstay/<what-changes>` from the current `origin/master`.
  2. It edits only Clipstay files (`content/clipstay.md`, `content/clipstay-privacy.md`, `static/img/clipstay/`), builds with the Hugo version in `.hugo-version`, runs `scripts/check_site.py` and pushes the branch. Pushing a branch deploys nothing.
  3. Viktor brings a note here: the branch name, what changed and why, what to check.
  4. Here: fetch the branch and re-check the whole site for consistency (homepage, structured data and any other place that mentions Clipstay), finish it if needed, open a PR for the branch if there is none, merge the PR under the usual rules (with Viktor's go-ahead; GitHub then deletes the branch), and verify production with `?v=<commit>`.
  5. If anything in the branch conflicts with the site's rules, do not merge: take the question back to Viktor.
- The other direction: this project does not change product facts itself. If work on the site reveals a mismatch with the product (for example, limits on the site differ from the store listing), write the question down for Viktor instead of editing the fact.
- Before this agreement Clipstay pushed to `master` directly twice: `9e0d297` (free plan wording: 100 unpinned clips plus up to 5 pinned) and `912f820` (`status: live`, Clipstay published in the Chrome Web Store on 2026-10-06). Both are in production and verified; nothing to redo.

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
