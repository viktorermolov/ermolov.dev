# Operations

The site is static Hugo on DigitalOcean App Platform behind Cloudflare. Pushes to `master` deploy it (see `CLAUDE.md`). The contact form was removed in October 2026, and its Worker and Pi relay code was removed from this repository; nothing here depends on them. The `/api/` exclusions in the edge rules below date from that API and are harmless.

## Resources

| Resource | Identifier |
| --- | --- |
| Cloudflare account | `52a5f4d5c9b84f6ab34ad87c1651f61d` |
| Zone | `3532291be695455e1ce46639f0a7dcb4` |
| Canonical redirect ruleset | `925c1da6060a4fff90f20e7879f8424c` |
| Static security-header ruleset | `04393da9a4634d67a815b6af4ef0acec` |

Never commit or print credentials.

## Scoped Cloudflare rules

The desired definitions are [canonical-redirects.json](../infrastructure/cloudflare/canonical-redirects.json) and [security-headers.json](../infrastructure/cloudflare/security-headers.json). They use Free-plan features and add no Worker execution or paid service. Treat them as reviewed definitions, not as permission to replace an entire existing phase ruleset. Read current rules before every change and preserve unrelated rules.

| Phase / ruleset | Rule ref | Scope and behavior |
| --- | --- | --- |
| `http_request_dynamic_redirect` / `925c1da6060a4fff90f20e7879f8424c` | `ermolov_index_canonical` | First: GET/HEAD `/index.html` on apex/www → `https://ermolov.dev/`, 301, preserve query. |
| Same redirect ruleset | `ermolov_www_canonical` | Then: GET/HEAD on www → apex with the same path/query, 301; excludes `/api/` and `/cdn-cgi/` prefixes. |
| `http_response_headers_transform` / `04393da9a4634d67a815b6af4ef0acec` | `ermolov_static_security` | Apex/www responses except `/api/` and `/cdn-cgi/` prefixes. |

Exact hostname conditions exclude unrelated subdomains. Non-GET/HEAD requests are not affected by these redirect rules. Existing HTTPS behavior and Cloudflare protection remain separate from these rules.

The static response rule sets:

```text
Content-Security-Policy: base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; upgrade-insecure-requests
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Strict-Transport-Security: max-age=31536000
```

It removes `x-do-app-origin` and `x-rgw-object-type`. This CSP restricts base URLs, embedded objects, framing and form destinations; it is not a strict script policy. There is no `script-src`/`default-src` restriction. Any later strict CSP needs separate browser tests for Hugo's inline theme setup, Turnstile, analytics and form fetches. HSTS intentionally omits `includeSubDomains` and preload; a browser that learns it still applies HTTPS to that hostname's API paths.

After an edge change, use an honest user agent such as `ermolov-release-check/1.0 (+https://ermolov.dev)` and inspect redirects without following them first. Check apex `/` is 200, www `/` and apex/www `/index.html` are 301 to the intended canonical, and query strings survive. Verify `/robots.txt`, `/sitemap.xml`, static CSS/JS and a missing path (404). Check that another existing subdomain retains its expected response. Do not submit an inquiry merely to inspect headers.

If robots/sitemap still show an older build, inspect the public body and cache response first. During this release `robots.txt` was a stale Cloudflare HIT; purging only `https://ermolov.dev/robots.txt` and `https://ermolov.dev/sitemap.xml` fixed it. Prefer this targeted purge after confirming publication; do not purge the whole zone or alter API cache behavior for a static metadata update.

### Cache rules and zone settings

Two dashboard-managed Cache Rules (`http_request_cache_settings`) apply to the apex host only:

| Rule | Match | Edge TTL | Browser TTL |
| --- | --- | --- | --- |
| Static CSS and JS (fingerprinted) | path starts with `/css/` or `/js/` | 1 year, ignore origin | 1 year |
| Fonts | path starts with `/fonts/` | 1 month, ignore origin | 1 month |

CSS and JS URLs carry a content fingerprint, so a year is safe; the font filename is fixed, so it stays shorter. HTML is intentionally not edge-cached: the Free plan's minimum Edge TTL is two hours and DigitalOcean deploys do not purge Cloudflare. A renamed font needs no purge; replacing the same font file needs a targeted purge of that URL.

Email Address Obfuscation is off so `mailto:` links work without JavaScript. The DigitalOcean static-site component sets build variable `HUGO_VERSION=0.166.0`; keep it in step with `.hugo-version`.

## Edge rollback

Rollback only the implicated scoped rule. In the Cloudflare zone's Rules interface, locate it by its description/ref above and disable it. The rule IDs are distinct from the ruleset IDs; do not use a ruleset ID as a rule ID. Do not delete either whole phase ruleset or overwrite it with the local JSON, because unrelated rules may have been added since this audit.

For an API-based rollback using the existing authorized connector:

1. Read `GET /zones/3532291be695455e1ce46639f0a7dcb4/rulesets/<ruleset-id>` and save its current definition privately. Find exactly one rule matching each intended `ref`; stop if the match is missing or ambiguous.
2. For redirect rollback, target `ermolov_index_canonical` and/or `ermolov_www_canonical` in ruleset `925c1da6060a4fff90f20e7879f8424c`. For header rollback, target only `ermolov_static_security` in ruleset `04393da9a4634d67a815b6af4ef0acec`.
3. Call `PATCH /zones/3532291be695455e1ce46639f0a7dcb4/rulesets/<ruleset-id>/rules/<resolved-rule-id>` with the existing writable definition (`ref`, `description`, `expression`, `action`, `action_parameters`, and any other currently configured writable rule fields), changing only `enabled` to `false`. Preserve the existing rule order and omit response-only IDs/version/timestamps. Cloudflare requires the rule fields to be retained in an update; a bare partial body must not silently drop them.
4. Read the ruleset again. Confirm only the selected rules changed, then repeat the status/header checks above in a fresh client. A browser may retain a cached 301; disabling an edge redirect does not clear that browser cache. Re-enable only after the cause is corrected and preserve the index-before-www rule order.

If the rollback specifically needs to retract HSTS, disabling the header rule is insufficient for browsers that already cached it. Keep valid HTTPS available. Use the same single-rule update with `enabled: true` and set its HSTS value to `max-age=0`, retaining the intended remaining fields and original hostname scope; verify that HTTPS responses emit it. Remove a problematic individual header from that definition if necessary instead of disabling the HSTS-clearing response. Clients clear the learned policy only when they receive that response; other clients can retain the prior one-year policy until expiry. Do not switch the site to HTTP or disable TLS as an incident workaround. Ordinary rollback of a CSP/header regression does not require removing HTTPS or HSTS.

References: [Cloudflare single-rule updates](https://developers.cloudflare.com/ruleset-engine/rulesets-api/update-rule/) and [HSTS requirements](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/http-strict-transport-security/). The September audit changes require no Worker/D1 rollback, since those components were not changed.

## Site rollback

Redeploy the previous site commit through GitHub/DigitalOcean.

## Analytics and privacy

Cloudflare Web Analytics measures visits and performance with a public token (`analyticsToken` in `config.toml`; not a secret). The site collects no other data. The visible email stays in the footer and the contact section.

## Search

The canonical sitemap is `https://ermolov.dev/sitemap.xml`. When changing metadata or routing, run the production Hugo build and `scripts/check_site.py`, then inspect the published robots, sitemap, canonical and response headers. Keep the site name consistent across the visible brand, Open Graph and structured data.
