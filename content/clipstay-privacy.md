---
title: "Clipstay Privacy Policy"
description: "Clipstay keeps your clipboard history on your device. It never sends your clips anywhere and has no account or analytics."
date: 2026-11-04
url: "/clipstay/privacy/"
layout: "legal"
schemaType: "WebPage"
---

Clipstay is a Chrome extension that keeps a history of the text you copy in the browser. This policy explains what it handles and where that data goes. The short version: **your clips and settings stay on your device. Clipstay has no account and no analytics, and it never sends your clips anywhere.**

## What Clipstay stores

All of the following is kept in your browser's local extension storage (`chrome.storage.local`) on your computer:

- **Text you copy or cut on web pages**, with the time it was copied.
- **Your current clipboard text when you open the Clipstay popup**, if it is new and “Add clipboard when the popup opens” is enabled. Starting with Clipstay 1.1.4, this import requires capture to be active. This preserves import from other apps. The shared clipboard can also contain text from Incognito or a password manager; the normal popup cannot identify where that text came from. You can turn clipboard import off in Settings.
- **Your settings:** whether capture is paused, your list of excluded sites, whether Clipstay adds your clipboard when the popup opens and, starting with version 1.1, your plan (free or Pro).
- **The last clip you deleted, so that you can undo the delete within 5 minutes** (starting with version 1.1.1). Only one such clip is kept; deleting another clip replaces it. After 5 minutes it can no longer be restored, and it is removed the next time Clipstay saves a new clip, you open the popup or the browser starts, or right away when you undo or clear your history.
- **Optional names for pinned clips** (starting with version 1.1.3). These names are stored only on your device.
- **A few counters for a one-time rating reminder** (starting with version 1.1.2): when you installed or updated Clipstay, how many times you copied from the popup, and whether the reminder was shown. They stay on your device and are never sent anywhere.
- **A short fingerprint (hash) of text copied on an excluded site.** The text itself is never saved. The fingerprint only lets Clipstay recognize and skip that text when you open the popup. A similar fingerprint of the last capture is kept to avoid saving the same copy twice.
- **Capture-state metadata** (starting with version 1.1.4): two revision counters, a fingerprint of the clipboard text read at Resume, and boolean markers for a new permitted page copy or saved-clip copy-back. The fingerprint contains the text length and a non-cryptographic hash after Clipstay's text-size limit is applied, not the raw clipboard text. These metadata stay on your device and are not included in clip exports or diagnostics. Their lifecycle is described below.
- **A local count of history-limit replacements and when they were planned.** It contains no clip text.
- **Local clip-history bookkeeping** (starting with version 1.1.4): separate per-clip recopy timestamps, so updating recency does not rewrite a clip's name or pinned state, and deletion markers containing a clip identifier and deletion time, so a delayed capture retry can recognize a deleted clip. These records contain no clip text. Recopy timestamps are removed with the clip where possible, and orphan entries are removed during later cleanup. Deletion markers become eligible for cleanup after 24 hours and are removed during a subsequent cleanup; this is separate from the five-minute Undo copy described above.
- **Free-history retention bookkeeping** (starting with version 1.1.4): a generation counter, a retained-history size boundary, a transition flag, and pending replacement records with clip identifiers and flags. These local records let new captures replace at most one oldest unpinned clip each without bulk-trimming existing or imported history. Pending records are removed when processed or no longer applicable; the retention state remains until updated or the extension is uninstalled. They contain no clip text. These separate bookkeeping records are not included in clip exports or diagnostics; exported clips still include their normal copy timestamps, including updated recopy times.
- **A local error log** for troubleshooting. An entry may include the website's domain name where an error happened. It never includes copied text.

Clipstay does **not** save the address of the page you copied from, your browsing history, or anything you did not copy.

## Page capture and the shared clipboard

Web-page capture skips copy and cut events from password fields, sites you add to the excluded list and Incognito pages. Clipstay does not request Incognito access.

Optional clipboard import is a separate path: opening the normal popup can save text left on your shared system clipboard. That text can come from Incognito, password managers or other apps. The popup cannot identify its origin. Turn off “Add clipboard when the popup opens” in Settings if you do not want that import.

### Resuming capture (Clipstay 1.1.4 and later)

Starting with Clipstay 1.1.4, pausing capture pauses web-page capture and popup clipboard import. Resume reads the current clipboard and saves its separate local fingerprint before enabling capture; read or storage problems are reported.

Popup import skips that unchanged text across popup closure and browser restart. Suppression ends when enabled popup import observes different or empty clipboard content, or Clipstay processes a new permitted page copy or saved-clip copy-back. An identical external-app recopy is indistinguishable from leaving the clipboard unchanged: first let a normal popup observe different or empty content. There is no timer that later imports unchanged text.

The fingerprint has no time-based expiry. The popup import check clears it after observing changed or empty content or a processed-copy marker; a later Resume replaces it. A permitted copy can therefore end suppression before the stored fingerprint is cleared by the next enabled popup import check. Revision counters remain. Obsolete boolean markers are removed on a best-effort basis; inert older markers may remain without time-based expiry. Uninstalling Clipstay removes this local extension data.

Clipboard reads and capture changes are not atomic. This safeguard concerns the text observed at Resume, not everything ever copied while paused, and it does not identify where clipboard text came from.

## Why Clipstay needs its permissions

- **Read and change data on all websites:** to notice when you copy or cut text on a page. Clipstay reads only the text you copy, at the moment you copy it. It also uses this access to start working in tabs that were already open when it was installed or updated.
- **Read data you copy and paste:** to add your current clipboard text when you open the popup, unless you turn that off in Settings. Starting with Clipstay 1.1.4, Resume also reads the current clipboard to establish its suppression fingerprint, even when automatic popup clipboard import is turned off.
- **Modify data you copy and paste:** to put a saved item back on your clipboard when you click it.
- **Storage and unlimited storage:** to keep your history on your device without a size cap.
- **Scripting:** to start capture in already-open tabs after installation or an update.

## Sharing and selling

### Network requests and $2 checkout (Clipstay 1.1.3 and later)

No network requests, except a one-time check when you activate Pro and an eligibility check when you start the $2 upgrade.

The $2 eligibility check sends your email, target product and attempt ID to the developer’s license service, hosted by Cloudflare. The Worker keeps a temporary checkout association containing the email hash, product, Stripe Checkout Session ID and checkout URL for up to 35 days from the start of the attempt.

The Worker sends your normalized email to Stripe to create the upgrade Checkout Session; Stripe handles checkout and payment under its own privacy policy.

### Data use (all versions)

Your clips, settings and history are not shared with Cloudflare or Stripe. Purchase and activation data is handled by those service providers as described here. Your data is never sold, used for advertising, or used to determine creditworthiness. The developer has no access to your clips.

The use of information received by Clipstay adheres to the [Chrome Web Store User Data Policy](https://developer.chrome.com/docs/webstore/program-policies/policies), including the Limited Use requirements.

## Your control

- Delete any item or clear your history from the popup, and pause capture from the popup or the options page, at any time. A deleted clip can be undone for up to 5 minutes (see above).
- Turn off adding your clipboard when the popup opens in Settings.
- Export your full history as JSON or CSV at any time. Export is always free.
- In Settings, import a JSON or CSV file you exported earlier. The file is read on your device and nothing is uploaded.
- To have your purchase records (the hash and payment IDs, including those kept after a refund) removed from the license service, write to the address below. After that, the email can no longer be used to activate Pro.
- Uninstalling Clipstay removes all of its stored data from your browser.

## Pro purchase and activation (version 1.1 and later)

Starting with version 1.1, Clipstay has a free plan and an optional Pro plan, a one-time purchase of $4.99. Earlier versions have no Pro plan and none of what follows.

Current purchase options also include the Clipstay + Pagestay Pro bundle for $6.99. Pagestay Pro owners can add Clipstay Pro for $2 through a link inside Pagestay. Clipstay Pro owners can add Pagestay Pro for $2 through a link inside Clipstay starting with version 1.1.3.

- **Payment is handled by [Stripe](https://stripe.com/privacy)**, on a Stripe-hosted page that opens in a new browser tab, outside the extension. Stripe collects your payment details and email address under its own privacy policy. The developer receives your email address and the payment details Stripe shows a merchant (such as name, amount, country or postcode, and card brand and last four digits); full card numbers are never seen or stored by the developer. Clipstay itself never sees any payment information.
- **Activation sends one request** (version 1.1 and later). In Settings you enter the email address you paid with and press Activate. Clipstay then sends **only that email address** to a small license service run by the developer (a Cloudflare Worker), which answers yes or no. If the answer is yes, Pro is switched on locally in your browser. The email address is not saved in the extension.
- **What the license service stores.** The developer's license service (a Cloudflare Worker, shared with Pagestay) stores an unsalted SHA-256 hash of your normalized purchase email (a one-way function, but one that could be matched against a list of known email addresses), per product, together with Stripe payment IDs, so that activation and refunds can work. The email address itself is not stored by the service; it stays with Stripe. Each payment has its own record of the licenses it covers. After a full refund, that payment can no longer be used to activate Pro. If no other unrefunded payment covers the license, its license entry is deleted. The payment record and a refund marker remain without expiry, so a late or repeated notification of the refunded payment cannot switch Pro on again. They contain the Stripe payment ID and, where one was recorded, the email hash; a refund marker for a payment with no known license record can contain only the payment ID. You can have these records removed on request (see “Your control”). A separate replay-prevention marker containing only an opaque HMAC ID and the attempt start time is kept without expiry. No device identifiers or license keys are used.
- **Network checks happen only when you activate Pro or start the $2 upgrade, never in the background.** Your clips, settings and history are never sent for activation or upgrade eligibility. The service sees your IP address like any web server and uses it only for brief rate limiting.
- To use Pro on another computer, enter the same email there.
- Refund terms are on the [Pro refund policy](/clipstay/refunds/) page.

## This website

This policy covers the Clipstay extension. The ermolov.dev website, including this page, uses Cloudflare Web Analytics to measure visits and page performance. The extension has no connection to the website and sends nothing to it.

## Changes and contact

Changes to this policy will be posted on this page with a new "last updated" date.

Questions: [viktor@ermolov.dev](mailto:viktor@ermolov.dev).
