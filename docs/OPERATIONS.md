# Operations

## Resources

| Resource | Identifier |
| --- | --- |
| Cloudflare account | `52a5f4d5c9b84f6ab34ad87c1651f61d` |
| Zone | `3532291be695455e1ce46639f0a7dcb4` |
| Worker | `ermolov-leads-api` |
| D1 | `ermolov-leads` / `825db71d-c29a-4bc4-99de-71b4a59122b4` |
| Pi | SSH alias `pi` |
| Relay root | `/data/programming/projects/ermolov.dev` |
| Bot source | `ermolov-site` |
| Private Bot URL | `http://notification-bot:8080` |
| Canonical redirect ruleset | `925c1da6060a4fff90f20e7879f8424c` |
| Static security-header ruleset | `04393da9a4634d67a815b6af4ef0acec` |

Worker secrets: `TURNSTILE_SECRET_KEY`, `RELAY_TOKEN`. Pi environment: `RELAY_TOKEN`, `NOTIFICATION_API_KEY`; no Telegram token or Cloudflare account credential. Keep `.env.relay` outside releases with mode `0600`. Never commit/print credentials or put them in URLs.

## Deployment

From `services/worker`, run `npm ci`, `npm run check`, `npx wrangler d1 migrations apply ermolov-leads --remote`, then `npm run deploy`. On first deployment use `npx wrangler deploy --secrets-file /private/path/worker-secrets.json` with a mode-0600 JSON file containing the two Worker secrets. Existing secrets survive subsequent deployment; rotate them with `wrangler secret bulk` from a private file. Review migrations and never erase accepted leads. Routes cover only `/api/*` on apex/www; DNS remains proxied to DigitalOcean.

On the Pi, register the source with the Bot's `scripts/manage_api_keys.py add ermolov-site --output <private-path>`, without printing credentials. Load the changed source map through that repository's guarded `scripts/deploy_remote.sh`: candidate build and unit/integration tests precede replacement. Preserve queue volume and other sources.

Provision the relay's environment from its example, commit the site code, then run `scripts/deploy_relay.sh`. This isolated deployment tests a candidate image with no network before replacement. See [relay instructions](../services/relay/README.md) for release layout, health, rollback and configuration. Publish the frontend last, with production Turnstile configuration.

## Delivery and recovery

The relay claims up to five leads with a short lease. A stable Bot idempotency key and immutable payload close the crash window between enqueue and saving the Bot ID. Keep that ID while awaiting delivery; only `sent`, not `202`, permits completion.

Transient failures retry with backoff and `Retry-After`. A stale lease stops processing. Terminal failure, conflicting idempotency and ambiguous results beyond the Bot's 30-day deduplication window require attention. Preserve D1 data; do not invent a new ID and silently resend.

Authenticated `GET /api/internal/status` exposes redacted queue state. Investigate private leads deliberately through D1, keeping them off logs/shared screenshots. Resolve failures by direct email or documented recovery after checking Telegram. There is no public inbox.

Cloudflare Browser Integrity Check rejects the default Python user agent with error 1010. The relay sends the descriptive `ermolov-lead-relay/1.0 (+https://ermolov.dev)` user agent. Use that header for command-line health checks too; do not disable the zone's protection.

Fault/recovery alerts pass through the existing Bot and their deduplication state survives relay restart. During total Pi outage, Cloudflare continues bounded intake, but Telegram alerts cannot originate from the offline Pi. Check last-poll/oldest-pending in API status and Cloudflare logs; restoring the relay resumes processing.

An attention warning is persisted locally before the Worker receives the terminal `attention` transition. If the alert queue is full (100 pending warnings) or local state cannot be saved, that transition is withheld and the lead remains reclaimable. Restore local storage/alert delivery before intervening in D1. A warning may arrive before a terminal update succeeds; reconcile the current Worker state and exact Bot receipt before taking action. Never clear the alert volume merely to silence a warning. See the [guarded operator recovery statements](../services/worker/README.md#recover-an-attention-item) to resume a known-safe receipt or mark a manually handled inquiry `resolved` without corrupting the unresolved counter.

## Scoped Cloudflare rules

The desired definitions are [canonical-redirects.json](../infrastructure/cloudflare/canonical-redirects.json) and [security-headers.json](../infrastructure/cloudflare/security-headers.json). They use Free-plan features and add no Worker execution or paid service. Treat them as reviewed definitions, not as permission to replace an entire existing phase ruleset. Read current rules before every change and preserve unrelated rules.

| Phase / ruleset | Rule ref | Scope and behavior |
| --- | --- | --- |
| `http_request_dynamic_redirect` / `925c1da6060a4fff90f20e7879f8424c` | `ermolov_index_canonical` | First: GET/HEAD `/index.html` on apex/www → `https://ermolov.dev/`, 301, preserve query. |
| Same redirect ruleset | `ermolov_www_canonical` | Then: GET/HEAD on www → apex with the same path/query, 301; excludes `/api/` and `/cdn-cgi/` prefixes. |
| `http_response_headers_transform` / `04393da9a4634d67a815b6af4ef0acec` | `ermolov_static_security` | Apex/www responses except `/api/` and `/cdn-cgi/` prefixes. |

Exact hostname conditions exclude unrelated subdomains. Non-GET/HEAD requests are not affected by these redirect rules. API responses retain their existing Worker policy, including `Cache-Control: no-store`. Existing HTTPS behavior and Cloudflare protection remain separate from these rules.

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

After an edge change, use an honest user agent such as `ermolov-release-check/1.0 (+https://ermolov.dev)` and inspect redirects without following them first. Check apex `/` is 200, www `/` and apex/www `/index.html` are 301 to the intended canonical, and query strings survive. Verify `/robots.txt`, `/sitemap.xml`, static CSS/JS and a missing path (404). Verify a private API request without credentials still returns the Worker `401` JSON/no-store response without redirection. Check that another existing subdomain retains its expected response. Do not submit an inquiry merely to inspect headers.

## Edge rollback

Rollback only the implicated scoped rule. In the Cloudflare zone's Rules interface, locate it by its description/ref above and disable it. The rule IDs are distinct from the ruleset IDs; do not use a ruleset ID as a rule ID. Do not delete either whole phase ruleset or overwrite it with the local JSON, because unrelated rules may have been added since this audit.

For an API-based rollback using the existing authorized connector:

1. Read `GET /zones/3532291be695455e1ce46639f0a7dcb4/rulesets/<ruleset-id>` and save its current definition privately. Find exactly one rule matching each intended `ref`; stop if the match is missing or ambiguous.
2. For redirect rollback, target `ermolov_index_canonical` and/or `ermolov_www_canonical` in ruleset `925c1da6060a4fff90f20e7879f8424c`. For header rollback, target only `ermolov_static_security` in ruleset `04393da9a4634d67a815b6af4ef0acec`.
3. Call `PATCH /zones/3532291be695455e1ce46639f0a7dcb4/rulesets/<ruleset-id>/rules/<resolved-rule-id>` with the existing writable definition (`ref`, `description`, `expression`, `action`, `action_parameters`, and any other currently configured writable rule fields), changing only `enabled` to `false`. Preserve the existing rule order and omit response-only IDs/version/timestamps. Cloudflare requires the rule fields to be retained in an update; a bare partial body must not silently drop them.
4. Read the ruleset again. Confirm only the selected rules changed, then repeat the status/header checks above in a fresh client. A browser may retain a cached 301; disabling an edge redirect does not clear that browser cache. Re-enable only after the cause is corrected and preserve the index-before-www rule order.

If the rollback specifically needs to retract HSTS, disabling the header rule is insufficient for browsers that already cached it. Keep valid HTTPS available. Use the same single-rule update with `enabled: true` and set its HSTS value to `max-age=0`, retaining the intended remaining fields and original hostname scope; verify that HTTPS responses emit it. Remove a problematic individual header from that definition if necessary instead of disabling the HSTS-clearing response. Clients clear the learned policy only when they receive that response; other clients can retain the prior one-year policy until expiry. Do not switch the site to HTTP or disable TLS as an incident workaround. Ordinary rollback of a CSP/header regression does not require removing HTTPS or HSTS.

References: [Cloudflare single-rule updates](https://developers.cloudflare.com/ruleset-engine/rulesets-api/update-rule/) and [HSTS requirements](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/http-strict-transport-security/). The September audit changes require no Worker/D1 rollback, since those components were not changed.

## Free-tier budget and retention

- Poll every 60 seconds: 1,440 Worker requests/day, plus submissions and state changes.
- Atomic application caps: 100 accepted leads/UTC day and 1,000 unresolved leads.
- Shared Free allowance: Workers 100,000 requests/day, 10 ms CPU/request; D1 5 million rows read and 100,000 written/day, 500 MB/database, 5 GB/account.
- Watch account totals in Cloudflare and D1 query metadata. Investigate at 80% of an allowance; slow the relay if needed. Never upgrade automatically.
- Rejected Worker requests also consume quota. Turnstile/origin/body/rate limits reduce abuse but cannot guarantee availability under unlimited traffic. On quota failure, offer email and never claim a failed save succeeded.
- Hourly bounded cleanup removes delivered personal data after 30 days and technical deduplication records after 90. Pending/attention data stays until handled, within its cap. Telegram messages are outside D1 automatic cleanup.

References: [Workers](https://developers.cloudflare.com/workers/platform/pricing/), [D1 pricing](https://developers.cloudflare.com/d1/platform/pricing/), [D1 limits](https://developers.cloudflare.com/d1/platform/limits/), [Turnstile](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/).

## Rollback

Redeploy the previous site commit through GitHub/DigitalOcean if UI fails. For the Worker, inspect `wrangler deployments list`, then `wrangler rollback <version-id>`; ensure schema compatibility. Restore the relay's prior release independently. Never delete D1, purge the Bot queue volume, or recreate pending leads during rollback.

## Analytics and privacy

Cloudflare Web Analytics measures visits/performance using a public token. D1 stores accepted leads and bounded attribution. Marketing analytics receives no enquiry content; referrer is a hostname, not a full URL. The form explains purpose, processors and retention. No automated email or advertising tracking is added.

The visible business email remains in the footer, privacy notice and no-JavaScript fallback; the contact-intro callout and JSON-LD email property are removed. Do not describe the public address, analytics token or Turnstile site key as a secret. Keep credentials, form content and private D1 records out of reports, screenshots and logs.

## Search and audit follow-up

The canonical sitemap is `https://ermolov.dev/sitemap.xml`. Google Search Console processed it successfully during the 21 September audit: last read 21 September 2026, one discovered page. URL Inspection separately confirmed the canonical URL is on Google, indexed and served over HTTPS. Performance reports were still processing. This confirms the existing page's status, not that the audit revision has been crawled. No separate request for indexing or Bing submission had been made when this report was prepared; record any subsequent published live-URL test/reindex action in the audit release table. Sitemap acceptance alone is not proof of indexing. Preserve one canonical homepage URL and use an accurate content modification date if `lastmod` is added later, not the time of every deployment.

`robots.txt` disallows API crawling while allowing the homepage and render assets. This does not replace authentication and cannot guarantee exclusion from search results. When changing metadata or routing, run the production Hugo build and `scripts/check_site.py`, then inspect published robots/sitemap/canonical and response headers. Keep the site name consistent across the visible brand, Open Graph and WebSite JSON-LD.

[FINAL-AUDIT.md](FINAL-AUDIT.md) records the bounded security scan, test evidence and performance limitations. Its release-verification table remains pending until populated with the published audit revision, final CI results, Pi rollout and browser checks. Baseline Lighthouse scores and a likely warm-cache reload measurement are not field CrUX/INP results.
