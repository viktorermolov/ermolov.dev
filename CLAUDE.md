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

**Roles and language.** Viktor owns positioning, copy under his name, which products are shown, and any redesign. This project owns the site working and staying consistent. Site copy is English; talk to Viktor in Russian. Viktor answers from his phone: one short message per decision with the question, options, a recommendation and the cost of getting it wrong; don't ask about small things.

**Development standards.** Follow the common standards in the private repo `viktorermolov/dev-standards` (`STANDARDS.md`); read them at the start of work. How they apply here:
- A merge to `master` deploys the site, so the merge is Viktor's go-ahead (the standard reserves merges that ship to production for him).
- Questions for a product project are gathered into one PR comment, because that project is woken by hand and not by PR events.
- Recorded departures: (1) emergency revert of a broken deploy goes straight to `master` without a PR (see the single exception above); (2) `master` has no branch protection, so "all changes through a PR" is enforced by this rule, not by GitHub; (3) the same light checks run on PRs and on `master` pushes, with no separate full suite, because the whole suite takes under a minute.

**Modes.**
- **Integrator (default, autonomous):** changes arrive from product projects (Clipstay now, more later, not only Chrome extensions) as PRs from `<product>/<change>` branches. Bring them in and propagate each change across the whole site: homepage project rows, product page, privacy policy, structured data, sitemap, shared sections. No stale version of a changed fact may remain anywhere. Autonomy ends at a prepared, reviewed PR (a pushed branch with an open PR); pushing to `master`, merging and deploying happen only on Viktor's explicit go-ahead for that specific change, and on his "yes" this project performs the merge via the REST API.
- **Builder (only when Viktor starts it):** redesigns, new sections, new product types, restructuring. Never initiate, but may suggest. Once started, lead it fully.
- Facts embedded in Viktor's copy (homepage hero, engineering notes, any first-person text): a direct fact swap to match the product is integrator work and is flagged in the report. Never remove positioning wording without a replacement; if the fix changes how something is presented, propose wording to Viktor. The product project has the final word on the fact; check its wording first.

**How to work.**
- Implementation goes to executor threads on Sonnet; the coordinator plans, coordinates and integrates. One-line fixes may be done directly by the integrating thread.
- Review is by risk. A separate fresh review thread on Opus that has not seen the work is mandatory for every PR and for builder-mode work. One-line edits and simple fact swaps are self-checked, with no separate reviewer; say so in the report. Never approve your own PR-level work.
- Site mechanics (build, deploy prep, propagation, fixes, `check_site.py` rules, maintenance of the parked Worker and relay) are this project's call; note decisions in the report.
- Substantial changes (repositioning, redesign, new site sections): a branch and a PR, merged only after Viktor approves.
- Smaller changes: they reach `master` through a PR merged on Viktor's go-ahead, so Viktor can check them on the live site and iterate. Prepare everything (build, `check_site.py`, a short note on what changes and what to check live), then wait for Viktor's go-ahead: reaching `master` deploys.
- **Branches are merged through pull requests.** The repository has "Automatically delete head branches" on, and this session cannot delete branches itself (git and the API both refuse), so a merged PR is the only way a branch disappears on its own. Anything waiting for Viktor's go-ahead lives on a pushed branch with an open PR, not as an unpushed local commit; on his "yes", merge the PR with the REST API (`PUT /repos/viktorermolov/ermolov.dev/pulls/<n>/merge`), and GitHub deletes the branch. Do not leave branches without a PR. Create PRs with `gh api` (REST); `gh pr` uses GraphQL, which is blocked here.
- After every deploy, verify production yourself; Viktor should not have to check. A deploy is live on ermolov.dev within a few minutes. Check the homepage, `/clipstay/` and `/clipstay/privacy/`, each with a unique query string (`?v=<commit>`): Claude's web-fetch tool caches responses per exact URL and can return an old copy of a bare URL long after the site has updated (this caused false "stale page" reports in October 2026). If a page with a fresh query string is still old, the deploy itself failed: check the DigitalOcean build, then report. No screenshots unless asked.
- Single exception to the go-ahead rule: if a deploy clearly broke the live site, revert to the last working commit and push without waiting, then report at once.
- Anything irreversible (production deploy, deleting data, money, paid cloud resources, domains) always needs Viktor's explicit confirmation.

**Cross-project coordination (product projects ↔ this repository).**
- This project (ermolov.dev) is the only owner of the site: only it merges to `master`, deploys and verifies production, and it is responsible for the site as a whole (copy, templates, structured data, homepage, sitemap, `check_site.py`).
- A product project owns its product facts: what the product does (features, including keyboard shortcuts), limits, permissions, price, data handling, the product's own tagline, refund terms, store status, and its privacy policy. It never pushes to `master` of this repository.
- **How changes arrive:** the product project creates a fresh branch `<product>/<what-changes>` from the current `origin/master`, edits only its own files (for Clipstay: `content/clipstay.md`, `content/clipstay-privacy.md`, `content/clipstay-refunds.md`, `static/img/clipstay/`), builds with the Hugo version in `.hugo-version`, runs `scripts/check_site.py` and opens a PR. Legal pages and product claims go in separate PRs, each stating the product version it ships with. Pushing a branch deploys nothing.
- **Coordination happens in the PR comments between the two projects, not through Viktor.** All GitHub comments carry the Claude attribution footer. The site side is the single PR watcher (GitHub delivers a PR's events to only one Claude session): when Viktor says a new PR is open, find it, start a thread on it and subscribe that thread to the PR. If another agent already watches it, tell Viktor once.
- Product projects are not woken by PR events; Viktor wakes them. When the site needs something from the product project, gather all questions into one PR comment, then tell Viktor in a single line, for example "Разбуди Clipstay: вопрос в PR #N".
- **Who decides:** technical details (branches, file placement, wording mechanics, where a fact appears) are settled by the two projects in the PR. Product facts belong to the product project: ask it in the PR, not Viktor. Site-wide matters (layout, redesign, which products are shown, site hero) belong to Viktor; this project proposes and handles the mechanics. Escalate to Viktor only what the owning project cannot settle within its boundaries, or when the two projects disagree.
- **Never change product facts on your own.** If work on the site reveals a mismatch with the product (for example, limits on the site differ from the store listing), ask the product project in the PR.
- **Code as a check:** before stating a checkable fact (what is stored, network requests, price, limits), verify it against the product's code. Code shows what the product does now, not necessarily what is intended: if code and claims differ, or it is unclear whether code reflects current decisions, ask the product project in the PR; don't silently align one to the other.
- **Release sync:** every product PR states which product version it ships with (for example "ships with Clipstay v1.1"). Legal pages (privacy policy, refunds) and product claims go in separate PRs with different go signals. A legal-pages PR becomes merge-ready when the product project comments "vX submitted for review"; a product-claims PR becomes merge-ready when it comments "vX is live" (for example in the Chrome Web Store). Until its signal, a PR may be fully ready but stays unmerged. Pushing to `master`, merging and deploying remain on Viktor's go-ahead.
- Re-check the whole site for consistency on every product PR (homepage, structured data and any other place that mentions the product), finish it if needed, merge under the rules above (with Viktor's go-ahead; GitHub then deletes the branch) and verify production with `?v=<commit>`. If anything in the PR conflicts with the site's rules, do not merge: settle it with the product project in the PR, and take it to Viktor only if they disagree.

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

Engineering notes and any first-person text are published under Viktor's name: get his approval on new or rewritten text before merging to `master`. The exception is a direct fact swap that keeps the product consistent (see Modes above). Notes should be about his own products and how they are built, not advice for clients.

**Name and location:** the visible brand is `brand` in `config.toml` ("Viktor E."). The full name stays in `author` for structured data, meta author and the copyright line. Do not add a location line (US-based and similar); `check_site.py` fails on it.

## Visual preference

Do not use personal photographs, portrait illustrations, avatars, or Memoji. Use typography, spacing, rules and restrained abstract graphics. Do not add floating bottom call-to-action bars that cover page content. Keep the blue palette.

## Parked inquiry infrastructure

The contact form was removed from the site (October 2026). `services/worker/` (Cloudflare Worker + D1 + Turnstile) and `services/relay/` (Raspberry Pi relay → Notification Bot → Telegram) are still deployed and still have tests and CI jobs, but nothing on the site uses them. Maintenance (dependency updates, security patches, CI fixes) is this project's call and goes through a PR with the usual review. **Do not disable, delete or decommission the Worker, D1, Turnstile widget, relay or Bot without Viktor's explicit confirmation.** Decommissioning is a separate step with its own plan of what is removed and what is lost. Until then: use only Free-tier resources and no paid upgrades; never log credentials, request bodies or personal information; never expose the Pi or Bot API to the Internet; keep `robots.txt` disallowing `/api/`. See `docs/OPERATIONS.md`.

**Site metadata** (name, bio, social links, analytics token) lives in `config.toml` under `[params]` and `[params.contact]`. Public tokens are not secrets.
