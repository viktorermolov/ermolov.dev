# Clipstay pause-control copy

The privacy correction was merged through [PR #60](https://github.com/viktorermolov/ermolov.dev/pull/60) on 2026-11-05; [issue #52](https://github.com/viktorermolov/ermolov.dev/issues/52) is closed as completed.

## Existing controls

Pause capture in Settings; resume it in Settings or from the popup. The popup has no Pause button. This applies to both verified Clipstay 1.1.3 and 1.1.4; it needs no new extension behavior.

- [1.1.3 options.html](https://github.com/viktorermolov/Clipstay/blob/5b5ea3e2d9d51a34fde22646975df5e1753001ba/options.html) has the Pause capture checkbox. [options.js](https://github.com/viktorermolov/Clipstay/blob/5b5ea3e2d9d51a34fde22646975df5e1753001ba/options.js#L26-L28) writes the checkbox value to `paused`, allowing pause and resume.
- [1.1.3 popup.html](https://github.com/viktorermolov/Clipstay/blob/5b5ea3e2d9d51a34fde22646975df5e1753001ba/popup.html#L26-L29) has only Resume in its paused banner. [popup.js](https://github.com/viktorermolov/Clipstay/blob/5b5ea3e2d9d51a34fde22646975df5e1753001ba/popup.js#L667) sets `paused: false`.
- [1.1.4 options.html](https://github.com/viktorermolov/Clipstay/blob/628470edfbffbe115073ba84a9ab6eb9862153a3/options.html#L68-L76) keeps that checkbox. [options.js](https://github.com/viktorermolov/Clipstay/blob/628470edfbffbe115073ba84a9ab6eb9862153a3/options.js#L26-L46) pauses when checked and uses `resumeCapture` when unchecked.
- [1.1.4 popup.html](https://github.com/viktorermolov/Clipstay/blob/628470edfbffbe115073ba84a9ab6eb9862153a3/popup.html#L26-L29) still has only Resume. [popup.js](https://github.com/viktorermolov/Clipstay/blob/628470edfbffbe115073ba84a9ab6eb9862153a3/popup.js#L752-L765) uses the same Resume operation.


## Scope and checks

The correction changed only the control description and privacy last-updated date. Delete/Undo instructions, Incognito/shared-clipboard explanations, version-scoped Resume behavior, prices and refund terms were preserved. All seven content pages were audited; only the privacy policy had the incorrect popup-pause claim.

The source comparison establishes the controls in those versions, not current Store status. The completed PR records independent review and the passing pinned-Hugo/full-site/JavaScript check. Future changes still follow CLAUDE.md; this completed correction is not authorization for another deployment.
