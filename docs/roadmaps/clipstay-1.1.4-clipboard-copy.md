# Clipstay 1.1.4 clipboard and Incognito copy

The product and privacy wording was integrated through [PR #53](https://github.com/viktorermolov/ermolov.dev/pull/53) and [PR #54](https://github.com/viktorermolov/ermolov.dev/pull/54), then included in the completed [site release #59](https://github.com/viktorermolov/ermolov.dev/pull/59). This is a behavior reference, not a pending publication plan or fresh native acceptance result.

## Product contract

Preserve automatic clipboard import from other applications and its disable setting. Direct Incognito page capture/import remains excluded, but text left on the shared clipboard can enter a normal popup. Do not promise provenance tracking or exclusion of everything ever copied while paused.

The 1.1.4 contract was checked against corrected [Clipstay PR #71](https://github.com/viktorermolov/Clipstay/pull/71), runtime head `4b487b14bbc24c16632b275c84e838e28df93521`. Its asset-only successor did not alter this runtime. Later retention and local inventory decisions are recorded in [the related reference](clipstay-1.1.4-retention-and-privacy.md).

## Source-verified lifecycle and metadata

Read actual `lib/store.js`, `popup.js`, `options.js`, `options.html`, `content.js`, manifest and export/diagnostics code at the source head above, rather than relying only on the PR narrative.

- `lib/store.js` (`resumeCapture`): both popup and Options call this function. Snapshot capture state, read clipboard outside the shared UI lock, recheck paused/revision, persist baseline, then write `paused:false`. UI read/storage failures are reported; changed-state attempts require retry. Resume reads the clipboard even when the automatic popup-import setting is off; the version-scoped clipboardRead-purpose disclosure must state this. Ordinary tested failures do not silently enable import. Ambiguous writes and total storage unavailability prevent absolute persistence claims.
- `meta:capture = {revision, baselineRevision, resumeHash}`. The first two fields are revision counters; `resumeHash` is the existing non-cryptographic `hashText` of normalized/truncated text (text length plus FNV-1a hash), or null for empty content. The metadata contain no raw paused clipboard text. A processed permitted page copy or saved-clip copy-back writes a boolean `meta:copy:<baselineRevision>` marker. These values are local and excluded from clip exports and diagnostics (aggregate storage-byte counts can still reflect them).
- `syncClipboard`, checks fresh settings/revision around its read. The unchanged baseline survives closure/restart, with **no time-based expiry or timer that later imports it**. Different/empty normalized clipboard content observed by enabled popup import, or an observed current-revision permitted-copy marker, ends suppression. The popup import check clears `resumeHash` and tries to remove the corresponding boolean marker.
- The distinction between behavior and physical deletion matters: a permitted copy makes the baseline logically inactive; the stored hash can remain until the next enabled popup import check or a later Resume replaces it. Revision counters remain; obsolete boolean cleanup is best effort, so inert older keys may remain without time-based expiry. Uninstall removes extension storage. Do not promise immediate or timed deletion.
- `capturePage` records a permitted page event including same-text recopy; corrected `touchClip` records saved-clip copy-back only against its gesture-observed baseline generation, so old/unknown queued copies cannot end a newer baseline. These can end the baseline. An identical external-app recopy has no observable event: let a normal popup observe different/empty clipboard content first, then recopy. Different external-app content still imports automatically.
- `content.js` starts state observation during trusted copy/cut dispatch and rechecks before deferred writes. Page origins do not share the UI lock. Clipboard reads, copying, writes and toggles are not atomic. This is not an absolute guarantee for all text ever copied during a pause.
- The current clipboard has no origin information. `popup.js` avoids direct Incognito import, and `content.js` excludes Incognito page events; neither prevents leftover Incognito/password-manager text from entering a normal popup. The existing disable option remains.


## Public wording and version boundary

Keep Resume lifecycle claims explicitly scoped to 1.1.4; the earlier 1.1.3 cached check does not establish the same behavior.

> Starting with Clipstay 1.1.4, Resume saves a local fingerprint of the current clipboard before enabling capture. Popup import skips that unchanged text across popup closure and browser restart. It stops skipping it after the popup observes different or empty clipboard content, or Clipstay processes a new permitted page copy or saved-clip copy-back. This concerns the text read at Resume, not everything copied while capture was paused.

The FAQ also explains reported errors, no timer, atomicity limits and the identical external-recopy workaround. Privacy describes the revision counters, hash/text length, boolean markers and deferred/best-effort cleanup rather than calling these simply temporary metadata. Resume reads even when automatic popup import is off; preserve that clipboardRead-purpose disclosure.

Keep the same limitations in the product page and alternatives page. Preserve the approved network sentence exactly once per privacy page, the never-in-background restriction, checkout URL/35-day retention, and unrelated purchase, control and website facts. Pause is in Settings; Resume is in Settings or the popup, as documented in [the control correction](clipstay-pause-control-copy.md).

## Images and validation limits

The accepted Capture and Pagestay images were integrated in [PR #55](https://github.com/viktorermolov/ermolov.dev/pull/55); the Plan card was corrected in [PR #57](https://github.com/viktorermolov/ermolov.dev/pull/57). [Screenshot provenance](../screenshot-provenance-2026-11-04.md) contains exact sources, hashes and lossless conversion instructions. These dependencies are complete, not pending handoffs.

The images show real extension UI with synthetic fixtures, not native Chrome browser frames. File transport, pixel identity, site checks and Linux captures do not validate native desktop external-app/Incognito behavior, purchases or Store publication. Product browser tests use clipboard stand-ins and a real browser-profile restart; do not infer broader native acceptance from them.
