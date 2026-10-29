---
title: "Clipstay Privacy Policy"
description: "Clipstay keeps your clipboard history on your device. It never sends your clips anywhere and has no account or analytics. Version 1.0 makes no network requests; starting with version 1.1, the only request is a single one-time check when you activate the optional Pro plan."
date: 2026-10-29
url: "/clipstay/privacy/"
layout: "legal"
schemaType: "WebPage"
---

Clipstay is a Chrome extension that keeps a history of the text you copy in the browser. This policy explains what it handles and where that data goes. The short version: **your clips and settings stay on your device. Clipstay has no account and no analytics, and it never sends your clips anywhere. Version 1.0 makes no network requests at all. Starting with version 1.1, the only thing Clipstay can ever send is the email address you type to activate the optional Pro plan (see “Pro purchase and activation”).**

## What Clipstay stores

All of the following is kept in your browser's local extension storage (`chrome.storage.local`) on your computer:

- **Text you copy or cut on web pages**, with the time it was copied.
- **Your current clipboard text when you open the Clipstay popup**, if it is new. This lets text copied in other apps appear in your history. You can turn this off in Settings (“Add clipboard when the popup opens”), for example if you copy passwords from a password manager.
- **Your settings:** whether capture is paused, your list of excluded sites, whether Clipstay adds your clipboard when the popup opens and, starting with version 1.1, your plan (free or Pro).
- **A short fingerprint (hash) of text copied on an excluded site.** The text itself is never saved. The fingerprint only lets Clipstay recognize and skip that text when you open the popup.
- **A local error log** for troubleshooting. An entry may include the website's domain name where an error happened. It never includes copied text.

Clipstay does **not** save the address of the page you copied from, your browsing history, or anything you did not copy.

## What Clipstay never captures

- Text copied from password fields.
- Anything on sites you add to the excluded list, or while capture is paused.
- Anything in Incognito windows. Clipstay does not request Incognito access.

## Why Clipstay needs its permissions

- **Read and change data on all websites:** to notice when you copy or cut text on a page. Clipstay reads only the text you copy, at the moment you copy it. It also uses this access to start working in tabs that were already open when it was installed or updated.
- **Read data you copy and paste:** to add your current clipboard text when you open the popup, unless you turn that off in Settings.
- **Modify data you copy and paste:** to put a saved item back on your clipboard when you click it.
- **Storage and unlimited storage:** to keep your history on your device without a size cap.
- **Scripting:** to start capture in already-open tabs after installation or an update.

## Sharing and selling

Clipstay version 1.0 makes no network requests. Starting with version 1.1, its only network request is a single one-time check when you activate Pro (described below). Your data is never sold, shared, transferred to third parties, used for advertising, or used to determine creditworthiness. The developer has no access to your clips.

The use of information received by Clipstay adheres to the [Chrome Web Store User Data Policy](https://developer.chrome.com/docs/webstore/program-policies/policies), including the Limited Use requirements.

## Your control

- Delete any item, clear your history, or pause capture at any time from the popup or the options page.
- Turn off adding your clipboard when the popup opens in Settings.
- Export your full history as JSON or CSV at any time. Export is always free.
- To have your purchase records (the hash and payment IDs, including those kept after a refund) removed from the license service, write to the address below. After that, the email can no longer be used to activate Pro.
- Uninstalling Clipstay removes all of its stored data from your browser.

## Pro purchase and activation (version 1.1 and later)

Starting with version 1.1, Clipstay has a free plan and an optional Pro plan, a one-time purchase of $4.99. Earlier versions have no Pro plan and none of what follows.

- **Payment is handled by [Stripe](https://stripe.com/privacy)**, on a Stripe-hosted page that opens in a new browser tab, outside the extension. Stripe collects your payment details and email address under its own privacy policy. The developer receives your email address and the fact that the payment was made; card details are handled by Stripe and are not seen or stored by the developer. Clipstay itself never sees any payment information.
- **Activation sends one request** (version 1.1 and later). In Settings you enter the email address you paid with and press Activate. Clipstay then sends **only that email address** to a small license service run by the developer (a Cloudflare Worker), which answers yes or no. If the answer is yes, Pro is switched on locally in your browser. The email address is not saved in the extension.
- **What the license service stores.** The developer's license service (a Cloudflare Worker) stores a one-way SHA-256 hash of your normalized purchase email and the Stripe payment ID, so that activation and refunds can work. The email address itself is not stored by the service; it stays with Stripe. The service keeps one such record for each payment that covers your license. After a full refund, that payment can no longer be used to activate Pro, and the payment ID of the refunded payment (and, where one was recorded, the hash) is kept, with no expiry, only so that a late or repeated notification of the refunded payment cannot switch Pro on again for that email; you can have them removed on request (see “Your control”). The same license service also answers for the developer's other extensions and keeps the same kind of records for them (a hash and payment IDs, never your email address). Nothing else is stored, and no device identifiers or license keys are used.
- **Clipstay checks only when you press Activate**, never in the background and never again afterwards. Your clips, settings and history are never part of this request. The service sees your IP address like any web server and uses it only for brief rate limiting.
- To use Pro on another computer, enter the same email there.
- Refund terms are on the [Pro refund policy](/clipstay/refunds/) page.

If you never activate Pro, Clipstay makes no network requests at all, in any version. If you do, the activation is that one request and nothing is checked afterwards.

## This website

This policy covers the Clipstay extension. The ermolov.dev website, including this page, uses Cloudflare Web Analytics to measure visits and page performance. The extension has no connection to the website and sends nothing to it.

## Changes and contact

Changes to this policy will be posted on this page with a new "last updated" date.

Questions: [viktor@ermolov.dev](mailto:viktor@ermolov.dev).
