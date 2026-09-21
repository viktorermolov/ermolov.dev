# Final audit — 21 September 2026

**Status: audit revisions prepared; final release verification pending.** This report separates observed production behavior, local fixes and measurements from checks that still require the published revision. Fill the release record below after publication. The initial launch evidence remains in [RELEASE.md](RELEASE.md).

## Scope and result

The review covered the Hugo page and form, its Worker/D1 contract, the Raspberry Pi relay, repository history, dependencies, search metadata and scoped Cloudflare edge rules. The approved design remains intact: no portrait and no floating bottom contact bar. This audit does not change the Worker, D1 schema, existing Notification Bot or unrelated Cloudflare services.

The concrete defects found were retry attribution changing the identity of an inquiry, editable fields during an in-flight request, incomplete error feedback for optional fields, and a relay crash window that could lose a manual-review alert after the lead became terminal. The source fixes and regression coverage are recorded below. No claim of complete security, accessibility certification, guaranteed indexing or customer acquisition is made.

## Findings and fixes

| Area | Observed problem | Change and evidence |
| --- | --- | --- |
| Form retry identity | After an ambiguous network failure, clicking another CTA could change attribution and create another submission identity for the same inquiry. | A stable attempt stores its UUID and first-attempt source together. Retries of unchanged content reuse both; accepted unchanged content is not posted again. An actual content edit creates a new attempt. Covered by the frontend regression fixture. |
| In-flight editing | A visitor could edit a note or choose another service while its previous snapshot was sending. | Text controls become read-only, selects and the submit button are disabled, and CTA handlers leave the pending snapshot intact. Original control states are restored on completion or failure. Failure preserves the note. |
| Validation and focus | Optional name/service/budget/timeline errors lacked associated feedback; a server error inside collapsed context could be hard to find. | Every field has associated error text. Optional context opens and the first invalid field receives focus after controls are restored. Client checks match the API's basic email syntax, UTF-16 length limits and invalid-character handling. |
| Relay terminal alert | A crash after Cloudflare accepted `attention` but before saving its local alert could leave a terminal inquiry without an operator warning. | Persist the warning with a stable key before the terminal update. A retry reuses that warning. A full alert queue or failed local persistence prevents the terminal transition, leaving the inquiry reclaimable. The relay suite now has 28 tests, including these crash/storage cases. An early warning after lease expiry is possible and intentional; it does not resend the inquiry. |
| Accessible brand name | Baseline Lighthouse reported one unweighted `label-content-name-mismatch` finding on the header brand link. | The accessible name includes the visible brand text. The fix awaits the published Lighthouse rerun; the baseline score alone did not establish this check passed. |
| Canonical URLs | `www` and `/index.html` returned duplicate `200` pages with an apex canonical. | Scoped Cloudflare `301` rules consolidate public GET/HEAD URLs while preserving query strings. API and Cloudflare challenge paths are excluded as described below. |
| Search metadata | Domain-only site naming differed from the visible personal brand; the structured graph duplicated the public email. | Open Graph and `WebSite.name` use `Viktor Ermolov`, with the domain as `alternateName`; WebSite/WebPage declare `en-US`. Person.email is removed. Large image previews are permitted. No invented reviews, client results or location data were added. |
| Crawl controls | Crawlers had no reason to be directed away from API paths. | `robots.txt` excludes `/api/` and retains the canonical sitemap. The homepage and render assets remain crawlable. This is a crawl preference, not API authorization or an indexing prohibition. |
| Edge response policy | The static site lacked an explicit scoped baseline for framing, MIME handling and related browser controls. | Added the response-header rule recorded in `infrastructure/cloudflare/security-headers.json`. It also removes two unnecessary origin-identifying response headers. The CSP is deliberately a baseline, not a strict script policy. |

Frontend regression tests execute the real `assets/js/app.js` in a controlled DOM/network fixture. They cover ambiguous retries, frozen attribution, busy-state restoration, repeated clicks, optional-field errors, email syntax, UTF-16 boundaries and control characters. They do not replace real-browser Turnstile checks.

A separate local browser fault-injection check returned 503, changed the CTA, then accepted the retry: two attempts used one submission ID and retained `hero` attribution on both. This confirms the browser retry behavior without sending a production inquiry.

The generated-site check now enforces exactly one absolute canonical, a sitemap containing only the canonical homepage, no `noindex`/`nofollow`, coherent JSON-LD IDs/references/name/language, and appropriate crawl permissions. A production Hugo build passes. Five deliberately broken temporary artifacts were rejected: accidental noindex, duplicate canonical, site-wide crawl denial, a noncanonical sitemap URL and a dangling schema reference.

## Security and runtime evidence

- A bounded secret-pattern scan inspected 41 commits and 190 blobs. Matches were reviewed as known example/test false positives; no live credential was identified by that scan. Pattern scanning does not prove that every possible secret format is absent.
- `npm audit` reported 171 audited dependencies and zero known vulnerabilities at the time of this audit. The Worker has no npm production runtime dependencies; the dependency count includes development tooling. This is a point-in-time advisory check.
- Read-only Pi runtime inspection confirmed the relay's restrictions and mode `0600` for its environment file. Its configured protections include non-root UID/GID 10001, a read-only root filesystem, dropped capabilities, `no-new-privileges`, resource limits and no published port. Only its dedicated alert/heartbeat state is writable and persistent.
- Inspected runtime logs contained identifiers and fixed error codes rather than inquiry text, email or credentials. The relay does not possess the Telegram token or a Cloudflare account credential. Secrets and customer submissions are intentionally omitted from this report.
- Previously verified production rejection paths remain documented in [RELEASE.md](RELEASE.md): invalid Turnstile `400`, foreign Origin `403`, oversized body `413`, private request without authentication `401`, with JSON `no-store` responses. This audit introduces no Worker change and no new successful test inquiry.
- The public business email remains in the footer, privacy text and no-JavaScript fallback, consistent with the earlier request to remove only the direct callout above the form. It is public contact information, not a secret; removing it from JSON-LD does not make it undiscoverable.

The underlying Bot provides at-least-once delivery. A crash after Telegram accepts a message can still produce a duplicate. Stable inquiry IDs, immutable payloads, saved Bot receipts, lease fencing and manual handling beyond the deduplication window reduce duplicate risk without claiming exactly-once Telegram delivery.

## Performance and accessibility measurements

| Measurement | Observed value | Interpretation |
| --- | --- | --- |
| Baseline Lighthouse accessibility | 100 | Automated baseline only; one unweighted brand-name finding was fixed and awaits the published rerun. |
| Baseline Lighthouse best practices | 100 | A score for the tested page/run, not a full security assessment. |
| Baseline Lighthouse SEO | 100 | Basic technical checks, not a ranking or indexing guarantee. |
| Mobile reload, 4× CPU slowdown and Slow 4G | LCP 991 ms; CLS 0 | Likely warm-cache observation. It is not a reproducible cold-load benchmark or a field Core Web Vitals result. |
| Field CrUX / INP | Not available in this audit | No field-performance or interaction-latency claim is made. |

No Lighthouse performance score is inferred from the reload measurement. Retain the earlier transfer-size measurements as historical release evidence, not as sizes for the revised build. Actual visits and a fresh published browser run are needed to establish current behavior.

## Search discoverability

The live pre-revision audit found a `200` canonical homepage, working `robots.txt` and a one-URL sitemap, no homepage `noindex` or `X-Robots-Tag` exclusion, server-rendered content, and a real `404` for an unknown path. HTTP already redirected to HTTPS. The duplicate www/index URLs were the main consolidation issue. Search results exposed an older www title/snippet; that observation is not proof of the current state of either Google's or Bing's index.

Google Search Console reports **Sitemap processed successfully**, last read **21 September 2026**, with **one discovered page**. A separate URL Inspection of `https://ermolov.dev/` reports **URL is on Google**, **Page is indexed**, and **HTTPS**. These observations establish the canonical URL's existing indexed status; they do not establish that Google has crawled the unpublished audit revision. Performance reports are still processing. No separate request for indexing or Bing submission has been made as of this report; a published live-URL test/reindex follow-up remains part of the release record.

The sitemap intentionally omits an invented build-time `lastmod`. When a trustworthy significant-content modification date is available, it can be supplied; a new build alone is not evidence of changed content.

These choices follow [Google's canonical guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls), [site-name guidance](https://developers.google.com/search/docs/appearance/site-names), [robots/preview directives](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag), [sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) and [Bing Webmaster Guidelines](https://www.bing.com/webmasters/help/bing-webmaster-guidelines-30fba23a). A sitemap and valid structured data help interpretation/discovery; they do not guarantee search inclusion or special result features.

## Cloudflare changes and limits

The checked-in JSON files record two scoped rulesets:

| Purpose | Ruleset ID | Rule refs |
| --- | --- | --- |
| Canonical redirects | `925c1da6060a4fff90f20e7879f8424c` | `ermolov_index_canonical`, `ermolov_www_canonical` |
| Static response headers | `04393da9a4634d67a815b6af4ef0acec` | `ermolov_static_security` |

Redirects apply only to GET/HEAD. The index rule maps `/index.html` on apex/www to the apex root. The www rule preserves the path, excluding paths beginning `/api/` and `/cdn-cgi/`. Both preserve query strings. Header changes apply only to apex/www outside those two path prefixes. Exact host matching leaves unrelated subdomains untouched.

The header policy is `base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; upgrade-insecure-requests`, alongside `nosniff`, frame denial, a cross-origin referrer policy and disabled camera/microphone/geolocation permissions. It intentionally has no `script-src` or `default-src` restriction; strict CSP-based script/XSS protection is not claimed. HSTS is one year, without `includeSubDomains` or preload. Browser HSTS state persists beyond disabling the response rule; the rollback runbook addresses this.

Only existing Free-plan features are used. No paid add-on, subscription change, new Worker request path, Worker deployment or database migration is part of this audit revision. Existing account-wide request/read/write limits, intake caps and retention still apply. Unlimited traffic can exhaust a free allowance; no zero-cost availability guarantee is possible.

See [Operations](OPERATIONS.md#scoped-cloudflare-rules) for rule scope, verification and rollback that preserves unrelated rules and services.

## Audit revision release record — pending

Complete this table with observed results after the audit changes are committed and published. Do not treat local fixes or the earlier launch test as verification of this revision.

| Release check | Result |
| --- | --- |
| Audit revision commit and CI run | Pending |
| DigitalOcean serves the revised HTML and fingerprinted JS | Pending |
| Final local/CI Hugo, frontend, Worker and 28 relay test results | Pending final run |
| Pi relay candidate tests, deployed revision and runtime health | Pending |
| Published desktop/mobile form, themes, focus/error behavior and Turnstile | Pending |
| Published Lighthouse rerun and brand-name finding | Pending |
| Redirect status/location/query preservation and API exclusions | Pending final release check |
| Static security headers, API no-store behavior and unaffected subdomains | Pending final release check |
| Search Console sitemap | Processed successfully; last read 21 September 2026; one discovered page |
| Search Console URL Inspection | Canonical URL on Google, page indexed, HTTPS; revised publication/live test pending |
| Worker/D1/Notification Bot changes in this audit | None |
