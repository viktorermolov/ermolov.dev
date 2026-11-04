# Clipstay 1.1.4 clipboard and Incognito copy preparation

Prepared on 2026-11-04 UTC against site release head `97d87eb807ae06aee4d01c2307572047d5864a74`. These are draft future-version claims, not a statement of current website deployment or published extension behavior.

## Authorized direction and delivery gates

- The owner accepted preserving automatic clipboard import from other applications. This is not a clipboard-import removal or opt-in redesign.
- Resume must read the current clipboard and persist a separate suppression fingerprint before unpausing, with a bounded lifecycle. Failures must not silently enable import; races with popup/options and reads already in flight need product verification.
- Direct Incognito page capture stays excluded, but text left on the shared system clipboard can enter the normal popup. Do not promise provenance tracking or permanent exclusion of all text ever copied while paused.
- Implementation is being prepared by the Clipstay author task `01a1a3f3-2d3b-74f3-8036-c2ce4b886001`; coordinate through the parent coordinator. No final implementation SHA/lifecycle has been supplied yet. Existing read-only Clipstay source at `fd18d11513db6d136a3d97f1acd885de996f452c` (manifest 1.1.3) establishes current import controls, not the proposed Resume guarantee.
- **Required gate for both copy and privacy:** final implementation and matching regression checks verified, exact public text reconciled to its hash lifecycle and error/race behavior, native screenshot claim corrected, independent review before any release integration, actual publication of Clipstay 1.1.4 before public website deployment, then explicit owner authorization for the exact master merge/deployment. Store submission alone is insufficient. No new behavior claim may publish for 1.1.3.
- Extension publication additionally requires successful canonical master CI at the exact final release SHA. No publication is authorized by this preparation.
- Keep purchase/network facts and refund policy unchanged. Existing legal/refund PR #46 remains separate, open draft and pending; this owner decision grants no retention/revocation policy decision.

## Exact proposed copy awaiting implementation reconciliation

Product/alternatives version-scoped sentence:

> Starting with Clipstay 1.1.4, resuming capture temporarily suppresses popup import of the clipboard text read at Resume. This applies to that current text; it does not identify everything copied while capture was paused.

Product shared-clipboard disclosure:

> Web-page capture skips password fields and Incognito pages. Optional clipboard import in the normal popup can still save text left on your shared system clipboard, including text from Incognito or other apps. You can turn it off in Settings.

Proposed privacy marker disclosure, to be prepared in a **separate legal-page PR**:

> A separate temporary local fingerprint of the clipboard text read when capture resumes (starting with version 1.1.4). It helps prevent that text from immediately being added by popup clipboard import. The marker is not a record of everything copied while paused.

The word “temporarily”, the precise scope of the marker and the statement that import is paused while capture is paused remain **proposals awaiting final code verification**. Do not add an invented TTL, clearing event, storage key, digest algorithm, privacy guarantee, fallback or error message. Final privacy wording must describe the actual retention/removal lifecycle once supplied.

## Page and image audit

- `content/clipstay.md`: replaced absolute password/Incognito capture claims, qualified popup import, retained external-app import and added a version-scoped pause explanation. The privacy note and highlights propagate into the product page; featureList keeps optional clipboard import. Homepage descriptions/tagline contain no conflicting pause/Incognito guarantee.
- `content/clipstay-alternatives.md`: replaced the same absolute guarantee and preserved the external-app use case; version-scoped Resume explanation added.
- `content/clipstay-privacy.md`: requires its separate legal-page draft, replacing “What Clipstay never captures” and the absolute pause/Incognito claims, describing shared clipboard limitations and the proposed temporary marker without fabricating lifecycle details.
- **Blocking image:** `static/img/clipstay/private.webp`, rendered by `content/clipstay.md` and included in SoftwareApplication screenshots, has correct approved network copy but its embedded options UI says “While paused, nothing is saved” and “It never captures password fields or incognito windows.” These are too broad in the new shared-clipboard context. The image is left unchanged until a reviewed native screenshot from the final implementation is available. No fabricated interface or painted-over screenshot. Do not integrate/publish this copy with that stale image.
- Needed source: regenerated native Clipstay `store/screenshots/03-private.png` at the final reviewed 1.1.4 implementation commit (or an author-confirmed replacement path), with truthful Capture/Resume/clipboard-import labels and the approved network sentence. Re-encode losslessly to `static/img/clipstay/private.webp`, inspect, record source/output checksums and verify matching rendered alt text.
- Visually inspected `history.webp`, `search.webp`, `pro.webp` and `static/og/og-clipstay.png`. No additional pause/Incognito assertion was found in them. The Pro screenshot has older activation wording; that is not expanded into a new network policy or retention decision here. Its separate current-version asset fidelity should be rechecked by the product author before publication.

## Acceptance and remaining steps

1. Parent coordinator obtains the finalized implementation SHA and fingerprint lifecycle: persistence location/data, expiry/reset conditions, behavior for a changed clipboard or repeated copy, and pause/Resume read/write failures in both popup and options. Confirm the wording against races and already-started imports; avoid brittle millisecond-only assertions. Require product evidence for preserved external-app import and the acknowledged Incognito limitation.
2. Reconcile the exact proposed sentences above, including what “temporarily” means; finalize the privacy retention sentence. Match all user-visible extension copy and screenshot captions. Real Chrome validation is still required by the product task; static source or synthetic checks are not browser evidence.
3. Obtain and verify the native screenshot replacement. Keep copy/privacy PRs draft until these dependencies are resolved, and obtain independent review before any release integration.
4. Run pinned Hugo production build, existing full site checker, JS syntax and whitespace checks for each final head and combined changes. Preserve the exact approved network sentence exactly once per privacy page, the never-in-background line, checkout URL/35-day retention and all unrelated facts. Existing tests/workflows must not be weakened or skipped.
5. Record exact PR heads and successful existing Actions. Reconcile the privacy-file overlap with #46 at integration time without importing its pending refund decisions.
6. After actual Clipstay 1.1.4 publication and matching implementation verification, obtain specific owner authorization for master deployment, verify production with fresh SHA query strings, then evaluate issue closure. No merge, deploy or issue closure is authorized now.
