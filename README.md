# ermolov.dev

The website of Viktor Ermolov, an independent developer who builds and maintains small software products, starting with Chrome extensions. It shows the products and hosts their pages (description, support, privacy policy). Hugo builds a static site; GitHub `master` deploys through DigitalOcean App Platform.

## Develop and check

Use Hugo **0.166.0** (`.hugo-version`), Node.js 22+ and Python 3.11+.

```sh
hugo server
hugo --environment production --destination /tmp/ermolov-site
python3 scripts/check_site.py /tmp/ermolov-site
node --check assets/js/app.js
```

## Structure

- `content/`: product pages (one markdown file per product, `type: project`) and the Clipstay privacy policy. Engineering notes go in `content/notes/` (none published right now); the homepage section appears when the first note exists.
- `layouts/`, `assets/`, `static/`: Hugo templates, CSS, browser JS, fonts, images.
- `config.toml`: public site information and analytics token (not credentials).
- `scripts/check_site.py`: checks the generated site (links, SEO, structured data, project pages).
- `docs/`: operations notes and the September 2026 audit and release records.
- `services/worker/`, `services/relay/`: the former contact-form pipeline. Still deployed, no longer used by the site, and parked until a separate decommissioning step. See [operations](docs/OPERATIONS.md).

## Add a product

1. Copy `content/clipstay.md` to `content/<slug>.md` and edit the front matter.
2. Put the icon and screenshots in `static/img/<slug>/`.
3. Keep `status: pending-review` until the product is published; the site shows "Coming soon" until it is `live`.
4. Build and run `scripts/check_site.py`.

Fonts: Bricolage Grotesque and Newsreader (SIL Open Font License; licenses in `static/fonts/`).
