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
