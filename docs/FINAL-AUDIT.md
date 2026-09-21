# Final audit — 21 September 2026

**Status: audit revisions published and verified.** The site serves the final UI revision `7b7d3f2044fdac0ca3cb5e1dc4aaf7e0aa0e46e8`; the Pi relay remains on the tested service revision `bcebd580115d34c435a93bc47e47d50b8cb693d6`. CI and published mobile/desktop Lighthouse checks passed. The Search Console live test and one indexing request completed successfully. The initial launch evidence remains in [RELEASE.md](RELEASE.md).

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
| Accessible brand name | An earlier public Lighthouse run reported one unweighted `label-content-name-mismatch` finding on the header brand link despite an accessibility score of 100. | The final UI follow-up removes the overriding `aria-label` and lets visible brand text provide the natural accessible name. Final published mobile and desktop checks pass, with no remaining failed audits. |
| Verification readiness | After Turnstile rendered, its caption could continue to say spam protection was loading. | Production now shows “Complete the spam verification to send your inquiry.” after rendering, with the SDK available and the submit button enabled. The human-verification control is visible; agents did not complete that challenge. |
| Canonical URLs | `www` and `/index.html` returned duplicate `200` pages with an apex canonical. | Scoped Cloudflare `301` rules consolidate public GET/HEAD URLs while preserving query strings. API and Cloudflare challenge paths are excluded as described below. |
| Search metadata | Domain-only site naming differed from the visible personal brand; the structured graph duplicated the public email. | Open Graph and `WebSite.name` use `Viktor Ermolov`, with the domain as `alternateName`; WebSite/WebPage declare `en-US`. Person.email is removed. Large image previews are permitted. No invented reviews, client results or location data were added. |
| Crawl controls | Crawlers had no reason to be directed away from API paths. | `robots.txt` excludes `/api/` and retains the canonical sitemap. The homepage and render assets remain crawlable. This is a crawl preference, not API authorization or an indexing prohibition. |
| Edge response policy | The static site lacked an explicit scoped baseline for framing, MIME handling and related browser controls. | Added the response-header rule recorded in `infrastructure/cloudflare/security-headers.json`. It also removes two unnecessary origin-identifying response headers. The CSP is deliberately a baseline, not a strict script policy. |

Frontend regression tests execute the real `assets/js/app.js` in a controlled DOM/network fixture. They cover ambiguous retries, frozen attribution, busy-state restoration, repeated clicks, optional-field errors, email syntax, UTF-16 boundaries and control characters. They do not replace real-browser Turnstile checks.

A separate local browser fault-injection check returned 503, changed the CTA, then accepted the retry: two attempts used one submission ID and retained `hero` attribution on both. This confirms the browser retry behavior without sending a production inquiry.

The generated-site check now enforces exactly one absolute canonical, a sitemap containing only the canonical homepage, no `noindex`/`nofollow`, coherent JSON-LD IDs/references/name/language, and appropriate crawl permissions. A production Hugo build passes. Five deliberately broken temporary artifacts were rejected: accidental noindex, duplicate canonical, site-wide crawl denial, a noncanonical sitemap URL and a dangling schema reference. Both recorded CI runs completed all three jobs successfully, with 21 Worker tests, four frontend tests and 28 relay tests.

## Security and runtime evidence

- A bounded secret-pattern scan inspected 41 commits and 190 blobs. Matches were reviewed as known example/test false positives; no live credential was identified by that scan. Pattern scanning does not prove that every possible secret format is absent.
- `npm audit` reported 171 audited dependencies and zero known vulnerabilities at the time of this audit. The Worker has no npm production runtime dependencies; the dependency count includes development tooling. This is a point-in-time advisory check.
- Read-only Pi runtime inspection confirmed the relay's restrictions and mode `0600` for its environment file. Its configured protections include non-root UID/GID 10001, a read-only root filesystem, dropped capabilities, `no-new-privileges`, resource limits and no published port. Only its dedicated alert/heartbeat state is writable and persistent.
- The Pi candidate image passed all 28 relay tests before deploying revision `bcebd580115d34c435a93bc47e47d50b8cb693d6`. The deployed service was healthy. One post-deployment snapshot showed a poll age of 36 seconds, heartbeat age of six seconds, zero pending, two sent and zero attention records; the log check returned zero lines. These are observed values, not an uptime guarantee, and no inquiry contents were inspected for this report.
- Inspected runtime logs contained identifiers and fixed error codes rather than inquiry text, email or credentials. The relay does not possess the Telegram token or a Cloudflare account credential. Secrets and customer submissions are intentionally omitted from this report.
- Previously verified production rejection paths remain documented in [RELEASE.md](RELEASE.md): invalid Turnstile `400`, foreign Origin `403`, oversized body `413`, private request without authentication `401`, with JSON `no-store` responses. This audit introduces no Worker change and no new successful test inquiry.
- The final edge check verified canonical redirects with query preservation, private API `401`/`no-store` responses on both apex and www without redirection, the expected response headers, and `404` for the checked sensitive-file paths. These bounded probes do not constitute an exhaustive exposure scan.
- The public business email remains in the footer, privacy text and no-JavaScript fallback, consistent with the earlier request to remove only the direct callout above the form. It is public contact information, not a secret; removing it from JSON-LD does not make it undiscoverable.

The underlying Bot provides at-least-once delivery. A crash after Telegram accepts a message can still produce a duplicate. Stable inquiry IDs, immutable payloads, saved Bot receipts, lease fencing and manual handling beyond the deduplication window reduce duplicate risk without claiming exactly-once Telegram delivery.

## Performance and accessibility measurements

| Measurement | Observed value | Interpretation |
| --- | --- | --- |
| Final published Lighthouse accessibility, mobile and desktop | 100 | The natural brand-name fix is verified; automated checks are not an accessibility certification. |
| Final published Lighthouse best practices, mobile and desktop | 100 | A score for the tested page/run, not a full security assessment. |
| Final published Lighthouse SEO, mobile and desktop | 100 | Basic technical checks, not a ranking or indexing guarantee. |
| Final published Lighthouse Agentic category, mobile and desktop | 100 | Both reports record 53 passed and zero failed audits overall. |
| Published mobile trace: 390 × 844, DPR 2, 4× CPU slowdown, Slow 4G, cold browser-cache/cache bypass | LCP 1,845 ms; CLS 0; TTFB 154 ms | A controlled lab observation of this navigation, not field Core Web Vitals or a claim that every CDN/network cache was cold. |
| Local build responsive checks | No horizontal overflow at 320, 720 and 1,440 px in dark theme; at 320 px in light theme | Tested against the local build/mock copy on port 1315, not the public site; not an exhaustive device/browser matrix. |
| Local build 200% CSS zoom at 1,440 px | No horizontal overflow | Local port 1315; CSS zoom, not native browser zoom. |
| Published responsive/theme check at 390 px | No horizontal overflow in light or dark theme; no portrait or floating bottom CTA | Public-site verification at this viewport. |
| Field CrUX / INP | Not available in this audit | No field-performance or interaction-latency claim is made. |

No Lighthouse performance score is inferred from the trace. The earlier 991 ms reload was likely warm-cache and is superseded here by the explicitly described lab run. Transfer-size measurements in the initial release report remain historical. Actual visits are needed for field-performance evidence.

The real Turnstile SDK returned `200` and the widget rendered its human-verification control on the published page. Automated Chrome did not complete that challenge, and agents sent no new inquiries. During challenge rendering the browser contained obfuscated console entries; their origin was not established. No application CSP violation was observed. This report does not claim an entirely warning-free browser console.

## Search discoverability

The live pre-revision audit found a `200` canonical homepage, working `robots.txt` and a one-URL sitemap, no homepage `noindex` or `X-Robots-Tag` exclusion, server-rendered content, and a real `404` for an unknown path. HTTP already redirected to HTTPS. The duplicate www/index URLs were the main consolidation issue. Search results exposed an older www title/snippet; that observation is not proof of the current state of either Google's or Bing's index.

Google Search Console reports **Sitemap processed successfully**, last read **21 September 2026**, with **one discovered page**. URL Inspection of `https://ermolov.dev/` reports **URL is on Google**, **Page is indexed**, and **HTTPS**; Google's chosen canonical matches the declared apex canonical, with a last crawl on **21 September 2026**. The **Manual actions** and **Security issues** reports both show **No issues detected**. These observations establish the URL's indexed status, not which exact deployment Google has processed or the absence of every possible security flaw. Performance reports are still processing. No Bing submission was performed.

The live test, displayed as **21 September 2026 at 4:04 PM** in Search Console, reported **URL is available to Google** and **Page can be indexed**. One indexing request then completed with **Indexing requested** and confirmation that the URL was added to the priority crawl queue. No repeated requests were sent. Queue acceptance does not establish when Google will recrawl or incorporate the latest deployment.

The published robots response initially remained a stale Cloudflare cache hit after deployment. Only the canonical `robots.txt` and `sitemap.xml` URLs were purged, then the public response was checked again and confirmed `Disallow: /api/`. No whole-zone cache purge or API cache change was needed.

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

## Audit revision release record

The following entries record completed observations for the main revision, final UI follow-up and Search Console actions.

| Release check | Result |
| --- | --- |
| Main audit revision and CI | `bcebd580115d34c435a93bc47e47d50b8cb693d6`; [run 35665264988](https://github.com/viktorermolov/ermolov.dev/actions/runs/35665264988) and [run 35665412787](https://github.com/viktorermolov/ermolov.dev/actions/runs/35665412787): all three jobs successful |
| DigitalOcean publication | Final `7b7d3f2` HTML verified publicly with the natural brand name; Last-Modified `21 September 2026 23:06:18 UTC`; JS fingerprint `8be5d03be7ccf66bf110d8d8f39f7f3996ebf146b156988394bd3ef24c9a597f` |
| Build and test results | Hugo/generated-site checks passed; frontend 4, Worker 21 and relay 28 tests passed |
| Pi relay deployment | Same `bcebd580` revision; 28 candidate tests passed; healthy; poll/heartbeat and redacted queue snapshot recorded above |
| Browser checks | Public 390 px light/dark: no overflow, portrait or floating bottom CTA. The wider viewport and CSS-zoom matrix above was local. Real public Turnstile SDK and widget loaded; correct readiness caption and enabled submit button verified; human challenge intentionally not completed. |
| Redirects and API exclusions | Query preservation verified; private API on apex/www returns `401` with `no-store` and no redirect |
| Static security and crawl responses | Expected headers verified; checked sensitive-file paths return `404`; scoped rules preserve unrelated hostnames; public robots includes `/api/` exclusion after targeted purge |
| Search Console sitemap | Processed successfully; last read 21 September 2026; one discovered page |
| Search Console indexed state | Canonical URL on Google/indexed/HTTPS; Google-selected canonical matches; last crawl 21 September 2026; no manual actions or reported security issues |
| Final UI follow-up publication, CI and Lighthouse | `7b7d3f2044fdac0ca3cb5e1dc4aaf7e0aa0e46e8` published after [CI run 35665844967](https://github.com/viktorermolov/ermolov.dev/actions/runs/35665844967) completed all three jobs successfully; [master run 35665965610](https://github.com/viktorermolov/ermolov.dev/actions/runs/35665965610) also completed successfully. Published mobile and desktop: accessibility 100, best practices 100, SEO 100, Agentic 100; 53 passed, zero failed audits. |
| Search Console live test / indexing follow-up | Live test on 21 September 2026 at displayed 4:04 PM: URL available to Google, page can be indexed. One indexing request accepted into the priority crawl queue; no repeated requests. |
| Worker/D1/Notification Bot changes in this audit | None |
