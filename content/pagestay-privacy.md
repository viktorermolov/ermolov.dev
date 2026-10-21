---
title: "Pagestay Privacy Policy"
description: "Pagestay keeps your notes and the addresses of the pages they are attached to on your device. It has no account, no sync, no AI and no analytics. The only thing it can ever send is the email address you type to activate the optional Pro plan."
date: 2026-10-21
url: "/pagestay/privacy/"
layout: "legal"
schemaType: "WebPage"
---

Pagestay is a Chrome extension that keeps notes in the browser's side panel. A note can be global or attached to a site or a single page. This policy explains what Pagestay handles and where that data goes. The short version: **your notes, the addresses they are attached to and your settings stay on your device. Pagestay has no account, no sync, no AI and no analytics. The only thing it can ever send anywhere is the email address you type to activate the optional Pro plan (see “Pro purchase and activation”). If you never activate Pro, Pagestay makes no network requests at all.**

## What Pagestay stores

All of the following is kept in your browser's local extension storage (`chrome.storage.local`) on your computer:

- **Your notes:** the text you write, with titles, folders and tags, and when each note was created and changed.
- **Where a note is attached.** A site note stores the site's host name (for example `example.com`). A page note stores the page address without its query string or fragment, unless you turn on “keep query” for that site. A rule note (Pro) stores the URL pattern you typed, such as `example.com/docs/*`. Pagestay stores an address or pattern only for a note you attach to it.
- **Earlier versions and the trash:** up to 20 earlier versions of each note, and deleted notes for 30 days.
- **Unsaved text:** when you close the panel in the middle of typing, the unsaved text is kept until the panel next opens, so it can be recovered.
- **Your settings:** including your plan (free or Pro), the sites where you keep the query string and your backup schedule.
- **A local error log** for troubleshooting: error messages with the time they happened. You can copy it from the options page. Pagestay never sends it anywhere.

Pagestay does **not** save your browsing history, the pages you visit without writing a note, or the content of web pages. It has no content scripts and no access to page content.

## Why Pagestay needs its permissions

Installing Pagestay shows no permission warning, because the two permissions that read tab addresses or write files are optional and are requested only when you turn on the feature that uses them.

- **Side panel:** to show the notes panel.
- **Storage and unlimited storage:** to keep your notes on your device without a size cap.
- **Active tab:** to read the address of the tab where you click the Pagestay button, so a note can be attached to that page or site.
- **Alarms:** to run scheduled backups and to empty the trash after 30 days.
- **Offscreen:** used only by scheduled backups, to wrap a backup file for saving. It shows no warning at install and reads no web page.
- **Tabs (optional):** requested when you choose “Enable page notes”. It lets Pagestay see the address of the tab you are on, so the panel can follow you between pages and the toolbar badge can show that a note exists for the current page or site. Pagestay uses tab addresses on your device only, to find your notes, and does not store or send them.
- **Downloads (optional):** requested when you turn on scheduled backups. It lets Pagestay save backup files to your Downloads folder.

## Sharing and selling

Pagestay's only network request is a single one-time check when you activate Pro (described below). Your data is never sold, shared, transferred to third parties, used for advertising, or used to determine creditworthiness. The developer has no access to your notes or to the addresses you attach them to.

The use of information received by Pagestay adheres to the [Chrome Web Store User Data Policy](https://developer.chrome.com/docs/webstore/program-policies/policies), including the Limited Use requirements.

## Your control

- Edit, delete or restore any note at any time. Emptying the trash deletes its notes permanently.
- Export all your notes as JSON or Markdown, and import them again. Export and restore are always free, with or without Pro.
- Scheduled backups are files saved to your own computer. They are never uploaded.
- Turn off “Enable page notes” by removing the optional permission in Chrome's extension settings.
- To have your purchase records (the hash and the payment ID) deleted from the license service, email [viktor@ermolov.dev](mailto:viktor@ermolov.dev) from the address you paid with. They are not deleted automatically. After they are deleted, that email can no longer be used to activate Pro, so keep your Stripe receipt if you want proof of purchase.
- Uninstalling Pagestay removes all of its stored data from your browser. Backup files you saved stay where they are until you delete them.

## Pro purchase and activation

Pagestay has a free plan and an optional Pro plan: $4.99, paid once. Pro is also sold together with Clipstay for $6.99, and Pagestay Pro owners can add Clipstay Pro for $2, through a link shown inside Pagestay. The free plan includes unlimited notes, page and site notes, autosave, revisions, trash and export.

- **Payment is handled by [Stripe](https://stripe.com/privacy)**, on a Stripe-hosted page that opens in a new browser tab, outside the extension. Stripe collects your payment details and email address under its own privacy policy. The developer receives your email address and the fact that the payment was made; card details are handled by Stripe and are not seen or stored by the developer. Pagestay itself never sees any payment information.
- **Activation sends one request.** In Options, under Plan, you enter the email address you paid with and press Activate. Pagestay then sends **only that email address, and the name of the product (“pagestay”)** to a small license service run by the developer (a Cloudflare Worker, shared with Clipstay), which answers yes or no. If the answer is yes, Pro is switched on locally in your browser. The email address is not saved in the extension.
- **What the license service stores.** It stores a one-way SHA-256 hash of your normalized purchase email, per product, together with the Stripe payment ID, so that activation and refunds can work. The email address itself is not stored by the service; it stays with Stripe. If a payment is fully refunded and no other payment still covers the license, the license entry is deleted. A record of that payment ID, marked as refunded, remains so that a repeated refund notice from Stripe is handled correctly; it can include the hash. These records, the hash and the payment ID, are kept without an expiry date and are deleted by hand when you ask (see “Your control” above). Nothing else is stored, and no device identifiers or license keys are used.
- **Pagestay checks only when you press Activate**, never in the background and never again afterwards. Your notes, addresses, settings and history are never part of this request. The service sees your IP address like any web server and uses it only for brief rate limiting.
- To use Pro on another computer, enter the same email there.
- Refund terms are on the [Pro refund policy](/pagestay/refunds/) page.

If you never activate Pro, Pagestay makes no network requests at all. If you do, the activation is that one request and nothing is checked afterwards.

## This website

This policy covers the Pagestay extension. The ermolov.dev website, including this page, uses Cloudflare Web Analytics to measure visits and page performance. The extension has no connection to the website and sends nothing to it.

## Changes and contact

Changes to this policy will be posted on this page with a new "last updated" date.

Questions: [viktor@ermolov.dev](mailto:viktor@ermolov.dev).
