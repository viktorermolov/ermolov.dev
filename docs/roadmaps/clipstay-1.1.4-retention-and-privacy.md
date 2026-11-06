# Retention and local-data disclosure

The accepted claims and legal changes were integrated through [PR #56](https://github.com/viktorermolov/ermolov.dev/pull/56) and [PR #46](https://github.com/viktorermolov/ermolov.dev/pull/46), with the Plan image and refund correction completed in #57/#58. They are part of the merged [site release #59](https://github.com/viktorermolov/ermolov.dev/pull/59), not pending review or an unresolved policy decision.

## Behavior to preserve

- Clipstay 1.1.4 retains existing/imported history and pins on passive transitions, import and Undo rather than bulk-trimming to 100. Each genuinely new Free capture at full history can replace one oldest unpinned clip; above 100 it replaces one rather than bulk-reducing the list. Five is the limit for adding pins, not permission to add five more to imported pins.
- A popup can import a genuinely new clipboard value, and popup/startup cleanup can settle replacement work triggered by an earlier capture. Neither “opening the popup can never remove an old clip” nor “saved clips are never deleted” is an unconditional promise the site can make.
- Clipstay local privacy inventory includes recopy timestamp sidecars, clip-ID/deletion-time markers eligible for cleanup after 24 hours and removed during later cleanup, and retention/replacement IDs, counters and flags. The bookkeeping contains no clip text. Normal exported clip timestamps can reflect recopy time, while separate bookkeeping records are not exported. Distinguish deletion markers from the five-minute full-text Undo slot. Do not promise exact timed removal, absolute atomicity or non-loss; no artificial clock/sleep example is needed in public copy.
- Pagestay 1.0.2 new site notes preserve a same-host canonical HTTP(S) creation origin, including protocol and optional port. Site links use it; legacy notes retain the `https://hostname` fallback without automatic backfill. JSON preserves origin; hostname-only matching is unchanged. Do not claim Markdown preserves origin.
- Shared payment disclosure retains the approved network sentence exactly once per privacy page, the never-in-background restriction, and checkout URL/35-day retention. Merchant payment-field examples are not a claim of extra Worker KV storage. No new payment collection or refund terms are implied.
- Preserve [the clipboard/Incognito contract](clipstay-1.1.4-clipboard-copy.md), optional Pro pricing/features, refund window, prices, whole-payment/bundle/upgrade rules and payment method. The [refund-copy correction](refund-copy-owner-correction.md) requires omission of post-refund activation assurances without substituting an immediate-deactivation claim.

## Sources and maintenance

The retention decision is [Clipstay #73](https://github.com/viktorermolov/Clipstay/issues/73), implemented with [PR #78](https://github.com/viktorermolov/Clipstay/pull/78). The source review covered getAllClips, addClipNow, Delete/Undo/clear/pin, retention holds, pruneNow and imports; #77 supplied the local recopy/deletion metadata. No new network, permission or Worker behavior follows from these local records.

Pagestay origin behavior is documented in [PR #61](https://github.com/viktorermolov/Pagestay/pull/61). The site claim/legal diffs and their source/validation evidence remain in #56/#46. The corrected native Plan card is integrated; use [screenshot provenance](../screenshot-provenance-2026-11-04.md) instead of recreating or painting over UI.

For later edits, check product source and accepted behavior together, then run the pinned Hugo build, full site checker and JavaScript syntax checks. Audit for obsolete newest-100 trimming claims and blanket non-deletion promises while preserving unrelated legal facts. Source and cloud/Linux evidence do not establish native desktop, payment or Store acceptance. No integration or image-review step remains in this reference.
