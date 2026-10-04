---
title: "Clipstay Privacy Policy"
description: "Clipstay keeps your clipboard history on your device. It collects nothing, sends nothing, and has no account or analytics."
date: 2026-10-04
url: "/clipstay/privacy/"
layout: "legal"
schemaType: "WebPage"
---

Clipstay is a Chrome extension that keeps a history of the text you copy in the browser. This policy explains what it handles and where that data goes. The short version: **everything stays on your device. Clipstay has no server, no account, and no analytics, and it does not send your data anywhere.**

## What Clipstay stores

All of the following is kept in your browser's local extension storage (`chrome.storage.local`) on your computer:

- **Text you copy or cut on web pages**, with the time it was copied.
- **Your current clipboard text when you open the Clipstay popup**, if it is new. This lets text copied in other apps appear in your history.
- **Your settings:** whether capture is paused and your list of excluded sites.
- **A short fingerprint (hash) of text copied on an excluded site.** The text itself is never saved. The fingerprint only lets Clipstay recognize and skip that text when you open the popup.
- **A local error log** for troubleshooting. An entry may include the website's domain name where an error happened. It never includes copied text.

Clipstay does **not** save the address of the page you copied from, your browsing history, or anything you did not copy.

## What Clipstay never captures

- Text copied from password fields.
- Anything on sites you add to the excluded list, or while capture is paused.
- Anything in Incognito windows. Clipstay does not request Incognito access.

## Why Clipstay needs its permissions

- **Read and change data on all websites:** to notice when you copy or cut text on a page. Clipstay reads only the text you copy, at the moment you copy it. It also uses this access to start working in tabs that were already open when it was installed or updated.
- **Read data you copy and paste:** to add your current clipboard text when you open the popup.
- **Modify data you copy and paste:** to put a saved item back on your clipboard when you click it.
- **Storage and unlimited storage:** to keep your history on your device without a size cap.
- **Scripting:** to start capture in already-open tabs after installation or an update.

## Sharing and selling

Clipstay makes no network requests. Your data is never sold, shared, transferred to third parties, used for advertising, or used to determine creditworthiness. The developer has no access to it.

The use of information received by Clipstay adheres to the [Chrome Web Store User Data Policy](https://developer.chrome.com/docs/webstore/program-policies/policies), including the Limited Use requirements.

## Your control

- Delete any item, clear your history, or pause capture at any time from the popup or the options page.
- Export your full history as JSON or CSV at any time. Export is always free.
- Uninstalling Clipstay removes all of its stored data from your browser.

## Future paid features

Clipstay currently has no paid features and no payment code. If a paid plan is added later, payments will be handled by a third-party payment processor, and this policy will be updated before that change is released.

## Changes and contact

Changes to this policy will be posted on this page with a new "last updated" date.

Questions: [viktor@ermolov.dev](mailto:viktor@ermolov.dev).
