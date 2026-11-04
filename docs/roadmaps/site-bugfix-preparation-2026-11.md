# Site corrections for Clipstay 1.1.4 and Pagestay 1.0.2

Prepared on 2026-11-04 UTC. This is preparation, not publication.

## Baseline and delivery boundary

- Site master: `fba7e7b3b8f1468a52b972ce09211715ea6fd926`.
- Canonical master check: [Check site #167](https://github.com/viktorermolov/ermolov.dev/actions/runs/41558936961), successful at that exact SHA.
- Release branch: `release/site-bugfix-preparation-2026-11`, initially at that master SHA.
- No existing release roadmap or open site PR was found. The old `pagestay/pro-inactive-wording` branch is retained; its relevant wording is already present on current master.
- Fresh feature branches and draft PRs target the release branch. Legal pages and product claims remain separate. Independent review precedes any merge. No formal self-approval.
- No master merge, deployment, tags, releases, store submissions, payment changes or security changes are authorized in this preparation.

## Issue scope and acceptance

All listed Issues stay open until their delivery criteria have been verified on production. Preparing or merging a PR does not publish a correction.

| Issue | Preparation scope | Acceptance before delivery |
| --- | --- | --- |
| [#33](https://github.com/viktorermolov/ermolov.dev/issues/33) | Privacy dates reflect actual policy edits | Both prepared policies show the actual edit date; recheck it when publication is authorized. Verify rendered date and live content after deployment. |
| [#35](https://github.com/viktorermolov/ermolov.dev/issues/35) | Fix nested 404 assets, homepage, section and footer links | Generated 404 resolves links/assets at top-level and arbitrarily nested missing addresses, with and without trailing slash; noindex and skip-link remain correct. Live `/clipstay/old-page` confirmation already supplied by audit; repeat after deployment. |
| [#36](https://github.com/viktorermolov/ermolov.dev/issues/36) | Match current Chrome Web Store titles | Product title, Open Graph, Twitter and SoftwareApplication alternateName agree with source manifests/listings for Clipstay 1.1.3 and Pagestay 1.0.1. |
| [#37](https://github.com/viktorermolov/ermolov.dev/issues/37) | Verify and harmonize shared purchase-data disclosure | Unsalted normalized-email hash, payment/refund records and exception for records without a known hash match Worker source; merchant payment fields are qualified as examples, not extra Worker storage. Preserve checkout URL/35-day retention and approved network line. |
| [#38](https://github.com/viktorermolov/ermolov.dev/issues/38) | Replace stale `static/img/clipstay/private.webp` from native repository screenshot | Image has the approved activation and $2 eligibility line; inspect it and record source SHA, file, conversion and checksum. No fabricated interface. |
| [#39](https://github.com/viktorermolov/ermolov.dev/issues/39) | Distinguish rule matching from automatic display | Product and refund pages both say existing rules still match and notes can be opened manually on Free; automatic opening/previews pause without Pro. |
| [#40](https://github.com/viktorermolov/ermolov.dev/issues/40) | Align refund section structure | Shared section order and bundle/upgrade coverage; preserve prices, 30-day whole-payment refund terms and valid-other-payment behavior. Clipstay retention paragraph remains pending owner decision. |
| [#41](https://github.com/viktorermolov/ermolov.dev/issues/41) | Explain existing folder/tag assignment restrictions | Free users can keep/remove existing assignments; moving to another folder or adding a tag, including existing ones, needs Pro. Existing text stays editable/exportable; restore remains free. |
| [#42](https://github.com/viktorermolov/ermolov.dev/issues/42) | Separate JSON/Markdown export from JSON import | Product summary, featureList, FAQ and privacy control text specify Pagestay JSON import; no Markdown import claim. |
| [#43](https://github.com/viktorermolov/ermolov.dev/issues/43) | Qualify Clipstay capture coverage and size | Product lede, highlight, featureList and limits describe supported web pages, Chrome-restricted pages and 100 KiB UTF-8 truncation. |

## Evidence and publication gates

- Clipstay source inspected read-only at `fd18d11513db6d136a3d97f1acd885de996f452c` (manifest 1.1.3): `manifest.json`, `store-upload/LISTING.md`, `background.js`, `lib/store.js`, `worker/index.mjs`, `worker/upgrade.mjs` and native screenshot assets.
- Pagestay source inspected read-only at `d6d8975a6f4926d3237f0c9383f11405cb008c27` (manifest 1.0.1): `manifest.json`, `store/listing.md`, `lib/store.js`, `lib/match.js` and `sidepanel.js`.
- Stripe reference: [Checkout Session](https://docs.stripe.com/api/checkout/sessions/object) and [PaymentMethod](https://docs.stripe.com/api/payment_methods/object). These establish available purchase fields, not the actual settings of a particular merchant account. No live payment data was accessed.
- These factual corrections describe published 1.1.3/1.0.1 behavior; they make no claim that 1.1.4/1.0.2 is available. Conservative proposed gate: independent review, owner acceptance of exact legal/copy text and publication timing, evidence that corresponding extension versions are actually published, then explicit owner authorization for the site master merge. The owner has not yet approved a final publication gate.
- Before any extension publication, require successful canonical master CI at the exact final extension release SHA. The site's current green master is only baseline evidence, not evidence for a future release commit.

## Completed checks and deviations

- Baseline Hugo 0.166.0 production build, existing site checker (8 content pages, 2 products), and JavaScript syntax check passed.
- Added a meaningful nested-404 regression to the existing checker. Against the unchanged baseline artifact it fails at `https://ermolov.dev/clipstay/old-page` because recovery links resolve under `/clipstay/`. After disabling Hugo's relative-URL rewriting, the same regression and whole-site checks pass. Root-relative asset and navigation paths now work at arbitrary missing URLs; canonical URLs remain unchanged.
- No existing failing test was weakened, skipped or replaced. No workflows changed. Local URL-resolution evidence is synthetic generated-HTML validation, not a fresh browser or live production retest.
- Existing CI is used unchanged and economically; final feature heads and check links are recorded in the draft PRs.

## Unresolved decisions and dependencies

- **Clipstay refund retention:** current policy says old clips are never deleted or hidden if Pro is inactive, but Free pruning can discard excess unpinned clips. The earlier audit found no supported refund-driven local downgrade; Pro is stored locally and activation checks are user-triggered. Do not pick a retention or revocation policy. Keep the contested paragraph unchanged and do not mark #40 fully delivered until the owner resolves it or explicitly accepts the unchanged scope.
- **Pagestay screenshots, product Issue #43:** coordinated independently by the Pagestay author. Site targets are `static/img/pagestay/{notes,search,organize}.webp`, referenced in `content/pagestay.md` including the homepage card. Need exact author-reviewed source files/commit, intended published version (1.0.2 if they show changed behavior), verified captions and mapping to each target. Current existing repository images are not assumed to satisfy that task. Bring any replacement through a separate site PR after the owning product provides it.
- A production Stripe Dashboard inspection is outside this task. Disclosure uses existing agreed Pagestay examples and source-verified Worker facts; it does not assert extra personal fields are stored in KV.

## Remaining release steps

1. Finish and validate separate mechanics, product-claims/assets and legal-pages draft PRs into the release branch; record exact heads and CI.
2. Obtain read-only independent review, including source facts and preserved refund terms; resolve findings through the relevant feature PR. No merge before current successful PR CI.
3. Resolve owner policy/publication decisions and Pagestay screenshot provenance. Recheck all issue acceptance criteria and prepared policy dates for the actual publication plan.
4. After review, integrate only through PRs; prepare a release-branch PR to master. Rebuild/check the combined site, preserving all existing checks and no unpublished-version claims.
5. Obtain explicit authorization for the exact master merge/deployment. Extension publication separately requires exact-final-master CI and its own publication authorization.
6. After authorized deployment, verify homepage, product/legal pages, nested 404 and images with fresh `?v=<final-sha>` URLs; confirm deployed SHA. Only then close delivered Issues. Record any partial or pending scope.
