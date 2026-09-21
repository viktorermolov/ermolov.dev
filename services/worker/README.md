# Contact API

Native TypeScript Cloudflare Worker and D1 outbox for `ermolov.dev`. The static site remains on DigitalOcean. The Raspberry Pi relay connects outbound to this API; no public Pi port or Telegram credentials are needed here.

## Local verification

Use Node.js 22 or later. From this directory:

```sh
npm ci
npm run types
npm run typecheck
npm test
npx wrangler deploy --dry-run
```

Tests execute in Workers with real local D1, mocked Siteverify, and no production calls. The test-pool runtime currently uses compatibility date `2026-08-15`; the production Worker uses `2026-09-21`. The `sharp` override patches a vulnerable image decoder in the development-only Miniflare dependency; production has no npm runtime dependencies.

For interactive local development, copy `.dev.vars.example` to ignored `.dev.vars`, apply migrations with `npx wrangler d1 migrations apply ermolov-leads --local`, and run `npm run dev`. Production origin/hostname restrictions remain enabled; use a separate local config and Cloudflare's documented test site/secret keys when exercising a local frontend. Never deploy test secrets. On a restricted desktop set `WRANGLER_LOG_PATH` to a writable temporary path.

## Provisioning and release

The checked-in account, D1 ID and domain routes identify this project only. Secrets are declared as required in Wrangler and generated types; provision them with `wrangler secret put TURNSTILE_SECRET_KEY` and `wrangler secret put RELAY_TOKEN`. The relay token must contain at least 32 characters; generate a random 256-bit secret and share it with the Pi relay through private files, never through source control.

Apply `npx wrangler d1 migrations apply ermolov-leads --remote`, set secrets, then deploy with `npm run deploy`. The Turnstile widget must allow `ermolov.dev` and `www.ermolov.dev`, and the client must use action `contact`. Routes cover only `/api/*`; `workers.dev` and preview URLs are disabled. Configure the route to fail closed. API route deployment does not replace the Hugo site or the existing Bytlot Worker/database.

Run an end-to-end inquiry after deployment: observe acceptance, relay receipt, Notification Bot `sent`, and D1 `sent`. A `202` from the Notification Bot is only a queue receipt. Roll back a Worker version with `wrangler rollback`; do not roll back/delete the D1 database or clear pending inquiries.

## Public API

`POST /api/leads`, `Content-Type: application/json`, allowed `Origin` required. Maximum body 16 KiB, enforced while streaming even without Content-Length.

| Field | Constraint |
|---|---|
| `submissionId` | UUID; same immutable inquiry uses the same identifier for retries |
| `email` | Required, valid basic email syntax, up to 254 UTF-16 units |
| `message` | Required, up to 2500 UTF-16 units; plain text |
| `name` | Optional, up to 80 UTF-16 units |
| `service` | Empty or `saas`, `ai`, `automation`, `advisory`, `rescue`, `other` |
| `budget`, `timeline` | Optional, up to 80 UTF-16 units each |
| `website` | Honeypot; leave empty |
| `turnstileToken` | Required for a new inquiry; validated with hostname and action |
| `source` | Optional object: `utmSource`, `utmMedium`, `utmCampaign` up to 80; `referrer` hostname only up to 120; `cta` up to 40 |

Strings are trimmed. NUL, invalid Unicode and control characters are rejected; message permits newlines/tabs. Email case is retained. All accepted lead/source fields contribute to the canonical idempotency hash; the challenge token does not. An identical saved inquiry is acknowledged before validating a consumed challenge. A different payload with the same ID is a conflict. Siteverify uses a stable UUIDv8 key derived from ID, canonical payload hash and token to retry ambiguous validation safely.

Success is `{ "ok": true, "id": "uuid" }`: `202` for newly saved, `200` for replay. All errors are `{ "ok": false, "error": { "code": "...", "message": "...", "fields": { "field": "hint" } } }`; `fields` is optional. Responses are JSON and `Cache-Control: no-store`.

| HTTP | Codes / meaning |
|---|---|
| 400 | `invalid_request`, `invalid_json`, `validation_error`; `challenge_required` / `challenge_failed` require a fresh challenge |
| 403 | `origin_forbidden` |
| 409 | `submission_conflict` |
| 413 | `body_too_large` |
| 415 | `unsupported_media_type` |
| 429 | `rate_limited`, Retry-After 60 |
| 503 | `capacity_reached`, `unavailable`, `challenge_unavailable`, Retry-After 300 |

Keep form contents on failure and expose the email alternative. Treat acceptance as durable receipt, not Telegram delivery. A filled honeypot receives a synthetic success without persisting anything.

## Private relay API

All `/api/internal/*` endpoints require `Authorization: Bearer <RELAY_TOKEN>` with a timing-safe comparison. They return no CORS permissions.

- `POST /api/internal/leads/claim`: returns `{leads:[{id,leaseToken,leaseExpiresAt,payload,notificationId,firstAttemptAt}]}`. Times are ISO UTC; `notificationId` is null until saved. At most five records, atomic 120-second lease. Expired leases become eligible again. `firstAttemptAt` never changes after the first claim. `payload` is the exact immutable Bot object `{title,message,level}` and is bounded including Bot's `[ermolov-site] INFO` prefix.
- `POST /api/internal/leads/:id/update`: JSON `{leaseToken,action,notificationId?,delaySeconds?,errorCode?}`. Actions: `progress` saves an immutable notification ID and renews lease (ID may be omitted to renew only); `sent` records confirmed delivery and requires notification ID; `retry` clears lease and schedules another attempt (default 60s, range 1–86400s); `attention` preserves the inquiry and removes it from automatic claims. Retry preserves any Bot ID. Only short machine error codes are accepted. A successful `progress` response includes `leaseExpiresAt`; all successful updates include `{ok:true,id}`.
- `GET /api/internal/status`: `{ok:true,counts:{pending,sent,attention,resolved},lastPoll,oldestPending}`. Times are ISO UTC or null. No inquiry text, email, IDs or credentials are returned. `resolved` is a separate operator-only terminal state, not a claim of Telegram delivery.

Private failures: `401 unauthorized`, `404 not_found`, `409 lease_conflict`, `409 notification_conflict`; invalid arguments use the standard `400` envelope. Stale ownership never changes a lead. Exact repeated `sent` acknowledgments with the original lease and receipt succeed after the original lease expires. Sending requires verification of Bot `sent`; queued receipts must remain pending. Notification Bot terminal metadata expires after 30 days: ambiguous older attempts require human reconciliation and must not be reposted blindly.

## Recover an attention item

Use the Cloudflare dashboard D1 console for **ermolov-leads**. Inspect only the selected UUID privately; do not paste inquiry contents or credentials into logs or task updates. Identify the reason and, when available, check the exact Bot notification ID using the source credential on the Pi. An old missing receipt is ambiguous, not evidence of failed delivery.

If a Bot credential/network issue is fixed, or the exact existing receipt still reports `queued`/`sent`, restore automatic processing with this guarded statement. It preserves the original payload, notification ID, first-attempt time and idempotency key; it does not change the unresolved counter. Do not use this for terminal Bot `failed` or an expired/unknown receipt.

```sql
UPDATE leads SET state='pending', next_attempt_at=unixepoch('now')*1000,
  error_code=NULL, lease_token=NULL, lease_expires_at=NULL
WHERE id='REPLACE_WITH_LEAD_UUID' AND state='attention';
```

For terminal failures or ambiguous receipts, reconcile manually and respond to the lead by email if needed. After the owner has handled the inquiry, use this operator-only resolution (also appropriate for confirmed spam). It preserves the deduplication record and releases one place in the unresolved cap:

```sql
UPDATE leads SET state='resolved', resolved_at=unixepoch('now')*1000,
  error_code='operator_resolved', lease_token=NULL, lease_expires_at=NULL
WHERE id='REPLACE_WITH_LEAD_UUID' AND state='attention';
```

The `account_operator_resolution` trigger decrements `service_state.unresolved` in the **same statement transaction**; retrying the guarded SQL changes zero rows and cannot decrement twice. No explicit `BEGIN` is needed or supported through D1's query API. Do not manually decrement counters, delete unresolved rows, clear notification IDs, edit saved payloads, or generate a new Bot key to bypass a failed/expired receipt. `resolved` records follow the same 30-day PII/90-day metadata retention measured from `resolved_at`. Confirm the selected row is resolved and the private status no longer counts it as attention.

## Free-tier controls and retention

- Rate binding: approximate 5 POSTs/IP/minute, before database writes. It is local to a Cloudflare location and is not a global quota.
- D1 hard caps: 100 new inquiries/UTC day and 1000 unresolved inquiries. Unique insert and both counters execute in one transaction; any conflict/cap error rolls back the entire admission. Attention records count as unresolved. Exactly one transition to `sent` decrements the counter.
- Pi polls every 60 seconds: 1440 baseline Worker requests/day. Accounts share Worker and D1 quotas with other projects. Accepted-lead caps cannot prevent request-quota exhaustion under unbounded external traffic. Stay on Workers Free; do not automatically upgrade or enable billable services.
- Indexed due queries avoid scanning the delivered history on empty polls. Worker output contains no inquiry content, IPs or secrets; automatic invocation logs are disabled. Structured acceptance/error/terminal events are recorded.
- Hourly cleanup redacts sent/resolved email/message/payload after 30 days, retains hash/receipt metadata through 90 days, then deletes it. Pending/attention records are retained for recovery within the 1000-item cap. Each cleanup statement handles at most 100 records/run. D1 Time Travel backups may retain removed data for the account's backup retention window. Existing Telegram messages have their own retention.
- Monitor Cloudflare's account-level quotas, private status and the Pi relay health. A completely offline Pi cannot send its own Telegram outage alert. This service does not provision a separate paid monitor.

Tests cover replay/changed payload/concurrent duplicate, Turnstile failures and safe retry keys, origin/rate/body bounds, Unicode bot size, atomic caps, parallel claims, lease fencing, persisted notification ID, sent ACK replay, attention retention, redaction and redacted health output.
