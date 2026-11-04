# Reviewed product screenshot conversions

Prepared on 2026-11-04 for the release/site-bugfix-preparation-2026-11 branch. This change replaces four image assets and corrects only the Clipstay image alt text. No legal pages, product claims, layout, workflow or tests are changed.

## Sources and version scope

- Clipstay source checkout `ddd3b51e7592e83ac4d6ef709bb23c1af9de7102`, PR #71 head `4b487b14bbc24c16632b275c84e838e28df93521`, [capture run 41761083124](https://github.com/viktorermolov/Clipstay/actions/runs/41761083124). The source and PR head share tree `541ab2bfcb57961cb3c1c87181a44c4e6b397ea9`. The manifest still reads 1.1.3; the captured resume-baseline UI is being prepared for 1.1.4, not evidence of a published release.
- Pagestay source checkout `fa36bfb4eff836112f200b095ab71f48cb10391b`, source PR head `489edf5bb8ad3f37e61769922040509d573645f4`, release base `46082d7f0158c3f910bd14378ad5734c2410cff7`, [capture run 41761022248](https://github.com/viktorermolov/Pagestay/actions/runs/41761022248). Version 1.0.2 preparation. Source runtime and image generators match the release base; differences are limited to the CI capture step, a provenance script, roadmap and provenance documentation.
- Both inputs were downloaded as Actions artifacts through the authorized GitHub connector, hash-checked and visually inspected. Only intended image assets and provenance are committed, not transport archives.
- These are compositions using real extension UI and synthetic fixture data, not native Chrome browser-frame captures. Pagestay combines an Acme demo page and 400 × 800 rendered panel. Pro is locally seeded in the fixture; no live purchase or activation is represented.

## Conversion

Pillow 13.0.0 / libwebp 1.6.0. Open the PNG, convert to RGB, then save WebP with `lossless=True, method=6, exact=True`. No crop, resize, overlays or UI edits. Each output is 1280 × 800. Decode each output as RGB and compare every byte against the RGB input: all four are pixel-identical.

| Source repository / PNG | Website target | Output bytes |
| --- | --- | --- |
| Clipstay / `store/screenshots/03-private.png` | `static/img/clipstay/private.webp` | 191186 |
| Pagestay / `store/screenshots/1-notes-for-this-page.png` | `static/img/pagestay/notes.webp` | 47890 |
| Pagestay / `store/screenshots/2-edit-note.png` | `static/img/pagestay/organize.webp` | 47686 |
| Pagestay / `store/screenshots/3-search-notes.png` | `static/img/pagestay/search.webp` | 48024 |

## SHA-256

- `static/img/clipstay/private.webp`
  - Input PNG: `7a84b7ff0e81818184a8b6194a60ba8360f3cad4387d2e697ac9fd066afc0969`
  - Output WebP: `9b4d2db489dad8682e73845dd2ac8776731efcb3e59b46977cca6fe458411c51`
- `static/img/pagestay/notes.webp`
  - Input PNG: `8a1f4d8c12e76006550f22bd2f70196c319a3530ca3c929b854bf4b8b2bf5afc`
  - Output WebP: `1e2c204b991a580ec107111f209e66422b6f8d770b736298ed49f12001512733`
- `static/img/pagestay/organize.webp`
  - Input PNG: `42a4770f3628128c252a4facfc1cea65347046c87fee10029c881bb83a98a123`
  - Output WebP: `143e140d44da9b342673bd4d1241408cb003afba1e456f0e67e4afaf03e6cfc6`
- `static/img/pagestay/search.webp`
  - Input PNG: `dba85360b74ad79174e4308406d126d1cd04a5607daaa8d88902c8b529b7c350`
  - Output WebP: `e3ac21242a34de35f2b4088e83a15d9f3dbbc0aec70fa49d54ddb812fecb46f0`

## Visual inspection and gates

The Clipstay image retains the complete Capture section, including the shared-clipboard limitation. Its new alt text no longer claims an excluded-sites list that is absent from this composition. Pagestay notes, rule-editing and search images retain their Free/Pro captions and visible controls. The notes image also feeds the homepage card through the existing content configuration.

Independent review and current site CI on this exact change are required before integration into the preparation release branch. The source images include unreleased bug-fix preparation; they are not proof of live-store compatibility. Master merge and production deployment require the owner's separate explicit go-ahead and the corresponding version/publication decision. No deployment, store upload or publication is performed here.
