# Release verification — 2026-09-21

## Deployed

- Site: https://ermolov.dev/ via the existing GitHub → DigitalOcean pipeline.
- Application commit: `1bc3b51f9910cdf6c961493921744bb1053980d5` (the subsequent portrait-free About, FAQ and documentation follow-up does not change the services).
- Worker version: `133aea6b-9746-4450-a253-34be4faa51f3`; production D1 migration `0001_leads.sql` applied.
- Pi relay: healthy, no published ports, approximately 19 MiB RAM measured after startup; 128 MiB container limit.
- Existing Notification Bot source `ermolov-site` loaded through its guarded deployment: 80 unit tests and one integration test passed before replacement.
- [Release CI](https://github.com/viktorermolov/ermolov.dev/actions/runs/35662288094): all three jobs passed.

## Delivery evidence

One explicitly labelled test inquiry was submitted through the real production form and real Turnstile. The UI confirmed acceptance only after persistence. The private Bot API reported `sent`, one attempt. The relay then recorded `sent` in D1 and reduced unresolved count to zero.

- Inquiry ID: `84c9d2f8-9be9-4158-94c1-e503905ef2ac`
- Bot notification ID: `6de4d1bd-70f8-4f91-b89a-27c12608b1be`
- Content included Cyrillic and an emoji. No real customer data was used.

## Verification performed

- Hugo production build; generated anchors/assets, canonical, sitemap, robots, structured data, form bounds and fallback checks.
- Worker TypeScript, 21 real workerd/D1 integration tests, deploy dry run; npm audit reported no vulnerabilities at release time.
- Relay: 24 tests locally, in CI, and in the Pi candidate image with networking disabled. Covers crash windows, queued/sent/failed, expired leases, ambiguous requests, deduplication age, Unicode, auth failures, persistent alert state and health semantics.
- Desktop/mobile light and dark layouts; 320, 375, 720 and 1440 px reflow checks; no horizontal overflow. Form validation and service preselection checked in-browser.
- A local fault-injection fixture returned 503, then success: text preserved, two HTTP attempts used one submission ID, a third click caused no additional request. The fixture's Turnstile double was local only.
- With all scripts removed from a local build, every main section remained visible and the direct email remained usable. Native form submission stayed disabled, preventing accidental PII in a GET URL.
- Production API rejected invalid Turnstile (400), foreign Origin (403), bodies over 16 KiB (413), and private requests without auth (401); JSON errors used `no-store`.
- Secret-value scan of staged files passed; runtime logs contain identifiers/error codes, not inquiry text or credentials.

## Measured size and resource use

One production HTTP measurement of the initial release from the workstation (not a Lighthouse or field Core Web Vitals result): document 8,354 compressed bytes / 0.429 s TTFB; CSS 5,627 bytes; custom JS 3,367 bytes; initial font 165,648 bytes. The font was reduced from about 724 KiB to 162 KiB. These figures exclude separately loaded analytics and Turnstile. The subsequent About revision removes the portrait asset entirely; current HTML/CSS sizes may differ slightly.

D1 was 61,440 bytes after the test inquiry. Reading the inquiry by primary key read one row and wrote none (0.204 ms SQL time in the observed query). Routine polling uses the due index and a singleton status row, rather than scanning the archive.

## Verification boundaries

The domain's Cloudflare Free plan was verified. Available API credentials could not read the Workers subscription/billing endpoint; no upgrade, paid add-on or subscription change was made. Account-wide quotas remain shared with other projects. Intake caps, bounded retention and the 60-second polling interval are enabled.

Native browser 200% zoom and full Lighthouse/Core Web Vitals measurements were not available in the in-app browser used for release verification; responsive reflow and HTTP transfer measurements are recorded above. Cloudflare Web Analytics is configured to collect real visits/performance. Long Pi outages and crash windows were simulated in tests, not induced on the live machine.

The labelled test record remains subject to normal retention. See [Operations](OPERATIONS.md) for recovery, quota checks, retention and rollback.
