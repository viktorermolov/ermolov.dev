# Clipstay pause-control copy correction

Prepared on 2026-11-05 UTC against site master `78fd75a888fafb5cfb874e5996e58ed6219c4c4e` for [issue #52](https://github.com/viktorermolov/ermolov.dev/issues/52).

## Scope and decision

Correct the remaining inaccurate pause-control sentence in the privacy policy. The owner agreed to describe the existing controls: pause in Settings, resume in Settings or the popup. No new popup button or extension behavior change is needed.

The public-copy change is limited to that control description and the policy's last-updated date. Existing Incognito/shared-clipboard explanations, version-scoped Resume behavior, prices, refund terms and all other product claims are unchanged.

## Verified product versions

The correction applies to both Clipstay 1.1.3 and 1.1.4. This source comparison does not establish which version is currently published in the Chrome Web Store.

- [1.1.3 options.html](https://github.com/viktorermolov/Clipstay/blob/5b5ea3e2d9d51a34fde22646975df5e1753001ba/options.html) has the Pause capture checkbox. [options.js](https://github.com/viktorermolov/Clipstay/blob/5b5ea3e2d9d51a34fde22646975df5e1753001ba/options.js#L26-L28) writes the checkbox value to `paused`, allowing pause and resume.
- [1.1.3 popup.html](https://github.com/viktorermolov/Clipstay/blob/5b5ea3e2d9d51a34fde22646975df5e1753001ba/popup.html#L26-L29) has only Resume in its paused banner. [popup.js](https://github.com/viktorermolov/Clipstay/blob/5b5ea3e2d9d51a34fde22646975df5e1753001ba/popup.js#L667) sets `paused: false`.
- [1.1.4 options.html](https://github.com/viktorermolov/Clipstay/blob/628470edfbffbe115073ba84a9ab6eb9862153a3/options.html#L68-L76) keeps that checkbox. [options.js](https://github.com/viktorermolov/Clipstay/blob/628470edfbffbe115073ba84a9ab6eb9862153a3/options.js#L26-L46) pauses when checked and uses `resumeCapture` when unchecked.
- [1.1.4 popup.html](https://github.com/viktorermolov/Clipstay/blob/628470edfbffbe115073ba84a9ab6eb9862153a3/popup.html#L26-L29) still has only Resume. [popup.js](https://github.com/viktorermolov/Clipstay/blob/628470edfbffbe115073ba84a9ab6eb9862153a3/popup.js#L752-L765) uses the same Resume operation.

## Validation and remaining gates

- Audited all seven current content pages for pause, Resume and Incognito claims. Only the privacy policy claimed the popup could pause capture.
- Local checks cover the exact narrow copy diff, unchanged surrounding claims, source controls in both versions and JavaScript syntax. No tests or workflows are changed.
- The local environment does not have Hugo. The existing Ubuntu `site` PR check must pass using pinned Hugo 0.166.0, the complete `scripts/check_site.py` suite and JavaScript syntax checking. Its result and independent review are recorded on the PR.
- Preparation does not authorize a master merge or production deployment. This correction is valid for both verified versions and does not need a new extension release, but the exact site master merge/deploy still requires the owner's explicit go-ahead.
- Keep #52 open until the corrected privacy page is deployed and verified with a fresh commit-specific URL. No deployment or issue closure is performed in this preparation.
