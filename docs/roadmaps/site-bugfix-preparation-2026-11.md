# Site corrections for Clipstay 1.1.4 and Pagestay 1.0.2

## Completed scope

The correction release was merged into master through [PR #59](https://github.com/viktorermolov/ermolov.dev/pull/59) on 2026-11-05. Its component work is no longer a pending release plan. Issues #33 and #35–#43 are closed as completed; the remaining pause-control correction was merged through [PR #60](https://github.com/viktorermolov/ermolov.dev/pull/60), and #52 is also closed. These are repository records, not a fresh live-site inspection.

- Nested 404 pages use root-relative assets and recovery links, including arbitrary missing paths with or without a trailing slash. Canonical URLs, noindex and the skip link remain intact.
- Product titles propagate to Open Graph, Twitter and SoftwareApplication metadata.
- Privacy dates reflect actual text edits. Shared purchase-data disclosures distinguish the unsalted normalized-email hash and payment/refund records from examples of merchant payment fields; records without a known hash remain explicitly qualified.
- Pagestay distinguishes JSON import from JSON/Markdown export. Existing rule notes still match and can be opened manually on Free; automatic opening/previews require Pro. Free users can keep/remove assignments, but moving to another folder or adding any tag requires Pro. Existing text remains editable/exportable and restore remains free.
- Clipstay describes supported web-page capture, Chrome-restricted pages and 100 KiB UTF-8 truncation. Its shared-clipboard and Resume limits are documented in [clipboard behavior](clipstay-1.1.4-clipboard-copy.md).
- Clipstay retention and local metadata, and Pagestay's optional creation origin, follow [the accepted behavior and privacy inventory](clipstay-1.1.4-retention-and-privacy.md).
- Refund pages preserve the prices, 30-day whole-payment request window, original payment method, bundle/upgrade rules and other-valid-payment distinctions. They omit the prohibited post-refund activation assurance, as explained in [the correction](refund-copy-owner-correction.md).
- Five native-to-WebP images, including the corrected Clipstay Plan card, have lossless pixel-identity and source evidence in [screenshot provenance](../screenshot-provenance-2026-11-04.md). Do not fabricate interface imagery.

## Maintenance and verification

Use the current product contracts and public pages for subsequent changes, not superseded preparation snapshots. Preserve version boundaries where behavior differs between versions. Site deployment, extension review submission and actual Store publication are distinct.

Run the pinned Hugo production build, full site checker and JavaScript syntax check from [CLAUDE.md](../../CLAUDE.md). The checker includes nested-404 behavior and the refund-copy regression guard. Product assertions, legal facts and screenshots must remain consistent across product pages, privacy/refund pages, metadata and the homepage.

After an authorized deployment, verify the deployed SHA and inspect the homepage, product/legal pages, nested 404 and images using fresh commit-specific query strings. Generated-site checks and Linux extension captures do not establish native OS/Incognito, installed-client, payment or Store acceptance. A live Stripe Dashboard inspection is a separate task, not implied by the purchase-data wording.

There is no remaining release-integration or image-review task in this roadmap. Detailed implementation, checks and merge history remain in [PR #59](https://github.com/viktorermolov/ermolov.dev/pull/59) and its linked component PRs. Future master merges deploy production and still follow the approval requirements in CLAUDE.md.
