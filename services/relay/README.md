# Website lead relay

Python standard library only. The service polls the Cloudflare Worker, submits
immutable notification payloads to the existing private Notification Bot, and
acknowledges each lead only after the bot reports `sent`. It exposes no port and
does not possess the Telegram bot token or chat ID.
HTTP requests identify the service as
`ermolov-lead-relay/1.0 (+https://ermolov.dev)`.

## Configuration and runtime

Provision `/data/programming/projects/ermolov.dev/.env.relay` **on the Pi**, mode
`0600`, using the names in `.env.example`. The Cloudflare `RELAY_TOKEN` and the
Notification Bot `NOTIFICATION_API_KEY` are separate credentials. Create the
bot source as `ermolov-site` using the bot's existing credential-management
command; never copy the shared bot credentials into this project. The bot needs
a controlled recreation to load a newly provisioned source key.

The Compose service `ermolov-lead-relay` uses project `ermolov-site`, its own
outbound network and the existing external/internal `notification-bot` network.
Its dedicated persistent volume `ermolov-lead-relay-data` stores only alert
deduplication metadata and a heartbeat; it does not cache lead text or email.
The image runs as UID/GID 10001 with a read-only root filesystem and dropped
capabilities. No third-party Python packages are installed.

```bash
cd services/relay
python3 -m unittest discover -s tests -v
```

## Worker contract

The base URL is `LEADS_API_URL=https://ermolov.dev/api`; all calls use bearer
`RELAY_TOKEN`. A claim request is `POST /internal/leads/claim` with `{}`. It
returns at most five records under `leads`, each with `id`, `leaseToken`,
`leaseExpiresAt` and `firstAttemptAt` (UTC ISO timestamps), `notificationId`
(nullable), and immutable `payload: {title, message, level}`.

`POST /internal/leads/{id}/update` receives `leaseToken`, an `action`, and
applicable fields:

- `progress`: optionally save `notificationId`, renew the lease for 120 seconds;
  response includes `leaseExpiresAt`. Omitting the ID only renews the lease.
- `sent`: include `notificationId`; the bot has confirmed delivery.
- `retry`: include `delaySeconds`, optional `notificationId`/`errorCode`; clear
  the lease but preserve the saved notification ID.
- `attention`: include a fixed `errorCode`, optional `notificationId`; retain
  the original lead for manual recovery.

Successful updates have `ok: true`. Unknown/stale leases return 404/409; the
relay stops using them. Authentication failures abort the batch. Every lease is
renewed before the first bot request, and the relay uses a ten-second safety
margin before expiry. No additional lead send occurs after a failed cloud update.

Bot submission uses `Idempotency-Key: ermolov-lead:<lead-id>:v1`; every retry
uses the same untouched payload. The relay saves the bot receipt before reading
its status. `queued` schedules another status check; `sent` acknowledges the
lead; `failed`/unknown IDs require attention. An uncertain POST result retries
with the same key. Once the 30-day deduplication window is nearly exhausted,
the relay requires manual reconciliation instead of risking a new delivery.
The existing bot has at-least-once delivery semantics, so a crash after Telegram
accepts a message can still produce a duplicate.

The normal poll is 60 seconds plus jitter. Outages back off exponentially to
15 minutes, honoring a longer server `Retry-After` when present. A heartbeat
continues throughout backoff. SIGTERM finishes the current lead then exits;
unprocessed leases expire and are reclaimed. Alert state is atomically persisted
and uses stable bot keys, one fault alert per outage and one recovery alert.
Attention alerts contain the lead ID and a fixed error code, never the lead's
email or message. The alert queue is bounded to 100 records, attention dedup to
1,000 IDs/30 days. Expired alert keys are dropped with a fixed log warning.

## Deployment and recovery

After tests and a clean Git commit, run `./scripts/deploy_relay.sh` from the
repository root. Optional `REMOTE_HOST`/`REMOTE_PATH` override the default `pi`
and `/data/programming/projects/ermolov.dev`.

Deployment syncs only relay source to `relay-releases/<commit>`, excludes all
environment/state files, tests the candidate image on the Pi with `--network
none`, validates configuration without printing it, and only then replaces
this service. Existing Notification Bot and unrelated containers are untouched.
A healthy deployment updates `relay-current`; an unhealthy candidate restores
the previous release when one exists. Images/releases are retained for rollback.

For manual rollback, select a known previous 40-character commit from
`relay-releases/`, set `RELAY_IMAGE=ermolov-lead-relay:<commit>` and
`RELAY_ENV_FILE=/data/programming/projects/ermolov.dev/.env.relay`, then use:

```bash
docker compose -p ermolov-site -f /data/programming/projects/ermolov.dev/relay-releases/<commit>/docker-compose.yml up -d --force-recreate --wait ermolov-lead-relay
```

Use the same project and persistent volume; do not run `down -v`. After rollback
passes health checks, point `relay-current` at that release. Rotating a relay
credential changes the private environment file and requires recreation of
only the service that loads it. Do not show the environment file or full Docker
container inspection output in logs.

Docker health checks **liveness**, including during upstream outages. Inspect
the redacted `health.json`, `docker compose logs --tail=100 ermolov-lead-relay`,
and authenticated Worker `GET /api/internal/status` for delivery health, oldest
pending lead, and attention count. A bot `202` or a healthy container alone is
not evidence of successful Telegram delivery.

For attention records, investigate the fixed error code and bot status first.
Recover through an explicit operator action after determining whether Telegram
already received the lead; never generate a new event key automatically. The
site's original lead remains in Cloudflare according to its retention policy.
Production smoke testing must use an explicitly authorized synthetic inquiry;
all automated tests use test doubles and send no Telegram messages.
