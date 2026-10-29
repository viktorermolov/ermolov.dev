---
title: "Pagestay Privacy Policy"
description: "Pagestay keeps your notes and the addresses of the pages they are attached to on your device. It has no account, no sync, no AI and no analytics. The only thing it can ever send is the email address you type to activate the optional Pro plan, with the product name."
date: 2026-10-21
url: "/pagestay/privacy/"
layout: "legal"
schemaType: "WebPage"
---

Pagestay is a Chrome extension that keeps notes in the browser's side panel. A note can be global or attached to a site or a single page. This policy explains what Pagestay handles and where that data goes. The short version: **your notes, the addresses they are attached to and your settings stay on your device. Pagestay has no account, no sync, no AI and no analytics. The only thing it can ever send anywhere is the email address you type to activate the optional Pro plan, together with the product name “pagestay” (see “Pro purchase and activation”). If you never activate Pro, Pagestay makes no network requests at all.**

## What Pagestay stores

All of the following is kept in your browser's local extension storage (`chrome.storage.local`) on your computer:

- **Your notes:** the text you write, with titles, folders and tags, and when each note was created and changed.
- **Where a note is attached.** A site note stores the site's host name (for example `example.com`). A page note stores the page address without its query string or fragment, unless you turn on “keep query” for that site. A rule note (Pro) stores the URL pattern you typed, such as `example.com/docs/*`. Pagestay stores an address or pattern for a note you attach to it. The one exception is the “keep query” switch, which remembers the host name of a site where you turned it on, even if no note is attached there.
- **Earlier versions and the trash:** up to 20 earlier versions of each note, and deleted notes for 30 days (you can turn the automatic emptying off in Options). When you import a file, Pagestay also keeps copies of the notes it replaced until you undo the import or start another one.
- **Unsaved text:** when you close the panel in the middle of typing, the unsaved text is kept until the panel next opens, so it can be recovered.
- **Your settings:** including your plan (free or Pro), the sites where you keep the query string and your backup schedule.
- **A local error log** for troubleshooting: error messages with the time they happened. You can copy it from the options page. Pagestay never sends it anywhere.

Pagestay does **not** save your browsing history, the pages you visit without writing a note, or the content of web pages. It has no content scripts and no access to page content.

## Why Pagestay needs its permissions

Installing Pagestay shows no permission warning: the Active tab access below works only for a tab where you click the Pagestay button, and the two permissions that let Pagestay follow your tabs or write files are optional and are requested only when you turn on the feature that uses them.

- **Side panel:** to show the notes panel.
- **Storage and unlimited storage:** to keep your notes on your device without a size cap.
- **Active tab:** when you click the Pagestay button (or press its keyboard shortcut), Chrome lets Pagestay read the address of that one tab, for that visit only, so the panel can show that page's notes and a note can be attached to that page or site. It ends when the tab goes to another site or subdomain.
- **Alarms:** to run scheduled backups and to empty the trash after 30 days, unless you turn that off.
- **Offscreen:** used only by scheduled backups, to wrap a backup file for saving. It shows no warning at install and reads no web page.
- **Tabs (optional):** requested when you choose “Enable page notes”. It lets Pagestay see the address of any tab you are on (Chrome words this permission as “Read your browsing history”), so the panel can keep following you between tabs and sites without another click, and the toolbar badge can show that a note exists for the current page or site. Pagestay uses tab addresses on your device only, to find your notes, and does not store or send them.
- **Downloads (optional):** requested when you turn on scheduled backups. It lets Pagestay save backup files to your Downloads folder.

## Sharing and selling

Pagestay's only network request is the check made when you press Activate for Pro (described below). Your data is never sold, shared with or transferred to third parties (other than the service providers that run the Pro purchase and activation, Stripe and Cloudflare, as described below), used for advertising, or used to determine creditworthiness. The developer has no access to your notes or to the addresses you attach them to.

The use of information received by Pagestay adheres to the [Chrome Web Store User Data Policy](https://developer.chrome.com/docs/webstore/program-policies/policies), including the Limited Use requirements.

## Your control

- Edit, delete or restore any note at any time. Emptying the trash deletes its notes permanently.
- Export all your notes as JSON or Markdown, and import them again. Export and restore are always free, with or without Pro.
- Scheduled backups are files saved to your own computer. They are never uploaded.
- Turning off scheduled backups removes the permission to save files.
- Uninstalling Pagestay also removes the permission to read tab addresses.
- To have your purchase records (the hash and the payment ID) deleted from the license service, email [viktor@ermolov.dev](mailto:viktor@ermolov.dev) from the address you paid with. They are not deleted automatically. After they are deleted, that email can no longer be used to activate Pro, so keep your Stripe receipt if you want proof of purchase.
- Uninstalling Pagestay removes all of its stored data from your browser. Backup files you saved stay where they are until you delete them.

## Pro purchase and activation

Pagestay has a free plan and an optional Pro plan: $4.99, paid once. Pro is also sold together with Clipstay for $6.99, and Pagestay Pro owners can add Clipstay Pro for $2, through a link shown inside Pagestay. The free plan includes unlimited notes, page and site notes, autosave, revisions, trash and export.

- **Payment is handled by [Stripe](https://stripe.com/privacy)**, on a Stripe-hosted page that opens in a new browser tab, outside the extension. Stripe collects your payment details and email address under its own privacy policy. The developer receives your email address and the payment details Stripe shows a merchant (such as name, amount, country or postcode, and card brand and last four digits); full card numbers are never seen or stored by the developer. Pagestay itself never sees any payment information.
- **Activation sends one request.** In Options, under Plan, you enter the email address you paid with and press Activate. Pagestay then sends **only that email address, and the name of the product (“pagestay”)** to a small license service run by the developer (a Cloudflare Worker, shared with Clipstay), which answers yes or no. If the answer is yes, Pro is switched on locally in your browser. The email address is not saved in the extension.
- **What the license service stores.** It stores an unsalted SHA-256 hash of your normalized purchase email (a one-way function, but one that could be matched against a list of known email addresses), per product, together with the Stripe payment ID, so that activation and refunds can work. The email address itself is not stored by the service; it stays with Stripe. If a payment is fully refunded and no other payment still covers the license, the license entry is deleted. Two records remain: the payment record and a refund marker, so that a repeated refund notice from Stripe is handled correctly. Both contain the hash and the payment ID. These records are kept without an expiry date and are deleted by hand when you ask (see “Your control” above). Nothing else is stored, and no device identifiers or license keys are used.
- **Pagestay checks only when you press Activate**, never in the background and never again afterwards. Your notes, addresses, settings and history are never part of this request. The service sees your IP address like any web server and uses it only for brief rate limiting.
- To use Pro on another computer, enter the same email there.
- Refund terms are on the [Pro refund policy](/pagestay/refunds/) page.

If you never activate Pro, Pagestay makes no network requests at all. If you do, the activation is that one request and nothing is checked afterwards.

## This website

This policy covers the Pagestay extension. The ermolov.dev website, including this page, uses Cloudflare Web Analytics to measure visits and page performance. The extension has no connection to the website and sends nothing to it.

## Changes and contact

Changes to this policy will be posted on this page with a new "last updated" date.

Questions: [viktor@ermolov.dev](mailto:viktor@ermolov.dev).
