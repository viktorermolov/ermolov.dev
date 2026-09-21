# ermolov.dev

An English service site for Viktor Ermolov: SaaS delivery, AI integration, and automation. Hugo renders the page; a Cloudflare Worker durably accepts enquiries; an outbound-only Raspberry Pi relay delivers them through the existing Notification Bot.

## Develop and check

Use Hugo **0.166.0** (`.hugo-version`), Node.js 22+, and Python 3.11+.

```sh
hugo server
hugo --environment production --destination /tmp/ermolov-site
python3 scripts/check_site.py /tmp/ermolov-site
node --check assets/js/app.js
cd services/worker
npm ci
npm run check
```

Relay tests use the Python standard library and test doubles; they never contact Telegram:

```sh
cd services/relay
python3 -m unittest discover -s tests -v
```

The production Turnstile key is hostname-restricted. Use Cloudflare's documented test widget/secret pair with a local Worker for submission tests. Never disable Turnstile on the public endpoint. No-JavaScript visitors can always use the visible email address.

## Structure

- `layouts/`, `assets/`, `static/`: Hugo templates, CSS, browser JS and local assets.
- `config.toml`: public site information, public Turnstile sitekey and analytics token (not credentials).
- `services/worker/`: API, D1 migrations, Wrangler configuration and integration tests.
- `services/relay/`: Python consumer, container, Compose configuration and tests.
- `scripts/`: generated-site checks and guarded relay deployment.
- `docs/`: audit, operations and release evidence.

```text
Browser -> Cloudflare Worker -> D1 durable inbox
                                  ^
                                  | HTTPS poll/claim/update
Raspberry Pi relay -> private Notification Bot -> Telegram
```

Acceptance and delivery are different events. The form succeeds only after D1 commits. A Bot `202` means queued; the relay marks delivery only after `sent`. Both boundaries use idempotency. Telegram is at-least-once: a crash after Telegram accepts a message can rarely cause a duplicate.

GitHub `master` triggers the existing DigitalOcean static-site deployment. Keep build command `hugo`, source root `/`, and output `public/`; set build environment `HUGO_VERSION=0.166.0` when available. Never commit `public/`. GitHub Actions checks all three components and holds no deployment secrets.

See [operations](docs/OPERATIONS.md), [audit](docs/AUDIT.md), [Worker API](services/worker/README.md), and [relay](services/relay/README.md).
