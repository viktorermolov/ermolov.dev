---
title: "Keep copied text and page notes in Chrome, on this computer"
description: "Hold on to sentences you copy and notes attached to a page or a site, in Chrome, without creating an account."
date: 2026-11-25
weight: 7
---

Copying a sentence from a page, then copying something else, leaves only the second sentence on the clipboard. Writing a thought about a page in a document keeps the words, but nothing in Chrome opens that document when you return to the page. Chrome does not do either job on its own.

The computer already keeps a short clipboard history, and Chrome already keeps bookmarks. They are not a searchable list of text you copied on web pages, and they do not bring a note back next to the page you wrote it for.

[Clipstay](/clipstay/?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=copied-text-and-page-notes-chrome&utm_content=intro-clipstay) keeps a history of text you copy in Chrome. [Pagestay](/pagestay/?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=copied-text-and-page-notes-chrome&utm_content=intro-pagestay) keeps notes in the side panel, attached to a page, a site, or kept globally. Both stay on this computer, with no account to create.

## What you already have

Windows, Mac and ChromeOS each keep a short clipboard history, including copies from other apps. That is not a history inside Chrome of only the text you copied on web pages. The steps and the limits are in [How to see your clipboard history in Chrome](/notes/clipboard-history-chrome/).

A bookmark stores the address and a name. Opening it later brings back the page, not a note about it. [Take notes on a specific website in Chrome, without an account](/notes/notes-on-a-website-chrome/) is the note on attaching text to a page or a site.

## A history of the text you copy

[Clipstay](/clipstay/?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=copied-text-and-page-notes-chrome&utm_content=body-clipstay) saves text you copy or cut on supported web pages, so you can search it, pin it and copy it back in one click. Clips stay on the device, in Chrome’s local extension storage. There is no account and no analytics. [Add Clipstay from the Chrome Web Store](https://chromewebstore.google.com/detail/biellalamlbfmgljmpfppaebblmmhokn?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=copied-text-and-page-notes-chrome&utm_content=cta-clipstay-top).

Open the popup to search the list (several words, in any order), pin a clip you reuse, and copy it back. The suggested shortcut is Control+Shift+V on a Mac and Alt+Shift+V on other systems. How pins and that shortcut work is in [Reuse the text you type every day](/notes/pins-shortcuts-chrome/).

Clipstay stores text only, up to 100 KiB per clip; longer text is cut to that size on the free plan and on Pro. Web-page capture skips password fields and Incognito pages. Chrome-restricted pages, such as the Chrome Web Store and `chrome://` pages, do not allow automatic capture. You can exclude sites, or pause capture, in Settings. A clip keeps the text and the time it was copied, not the address of the page.

With “Add clipboard when the popup opens” turned on, opening the popup can also save text already on the system clipboard, including text from other apps or Incognito. Clipstay does not watch other apps in the background. Turn the option off in Settings when you do not want that import.

Free includes 100 unpinned clips, and you can add a pin while fewer than five clips are pinned. Existing and imported clips and pins are kept even above those numbers. When the free history is full, a new clip can replace the oldest unpinned one; pinned clips are kept. Pro is $4.99, paid once, and removes the history and pin limits. Search, export and import stay free. Uninstalling the extension removes the stored data, so export to JSON or CSV first if you want a copy.

## A note that belongs to the page

[Pagestay](/pagestay/?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=copied-text-and-page-notes-chrome&utm_content=body-pagestay) keeps notes in Chrome’s side panel, next to the page you are reading. A note can be attached to the page, to the whole site, or kept global. Notes are saved as you type, and each note keeps earlier versions. There is no account, no sync, no AI and no analytics. [Add Pagestay from the Chrome Web Store](https://chromewebstore.google.com/detail/lehddjgolnpdbmmijbefdffhblbgiejj?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=copied-text-and-page-notes-chrome&utm_content=cta-pagestay-top).

Pagestay needs Chrome 130 or newer. Click the toolbar button, or use the suggested shortcut: Control+Shift+N on a Mac and Alt+Shift+N on other systems. **New note** attaches to the page you are on when Pagestay can see that tab’s address. **Note for this site** is the hostname, such as `example.com`. **Global note** is not attached to any page or site. How the panel works, and how a page address differs from a site address, is in [Using Chrome’s side panel for notes while you read](/notes/chrome-side-panel-notes/) and the note linked above.

Pagestay does not read the words on the page. It has no content scripts and no access to page content. It uses the tab’s address to find notes you attached, and it does not save pages you visit without writing a note. Clicking the button, or using the shortcut, lets it read the address of that one tab, for that visit. To keep the panel following your tabs, and to show a dot on the button when a note exists, press **Enable page notes**. Chrome then asks for the tabs permission, which it describes as reading your browsing history. Pagestay uses those addresses on your device and does not send them anywhere. Without that permission, it still works on the tab where you click its button.

Notes stay on that computer, in Chrome’s local extension storage. Uninstalling the extension removes what it stored, so export to JSON or Markdown first if you want a copy. Export is always free, and a Pagestay JSON file can be imported on another computer. How to keep a backup is in [Where your browser notes actually live, and how to back them up](/notes/browser-notes-backup/).

The free plan has unlimited notes in the side panel — page, site and global — with version history, a 30-day trash and a filter by title. Pro is $4.99, paid once. It adds search inside the text of your notes and by tag, folders and tags, rule notes for a URL pattern you type (such as `example.com/docs/*`), and scheduled backups saved on the computer.

## Using them together

Clipstay is the list of sentences you copied. Pagestay is the note that should be waiting when you open the page again. They do not share a database: a clip is not turned into a page note, and a note is not added to the clipboard history.

Copy a quote, an error message or a command you will paste again into Clipstay, and pin it if you will need it often. Write a decision, a question or a short checklist that should come back with the page or site in Pagestay. Because Clipstay does not store the page address, the history will not take you back to the source. If the source matters, put it in the Pagestay note.

Both sets of data stay on this computer. There is no account and no sync in either extension. To use the same clips or notes on another computer, export a file and import it there. Pro is $4.99 once for each extension, or $6.99 as a bundle, which unlocks Pro in both.

## Before you rely on them

Clipstay’s popup can import text left on the shared system clipboard when “Add clipboard when the popup opens” is on; you can turn that off in Settings. Starting with Clipstay 1.1.3, there are no network requests, except a one-time check when you activate Pro and an eligibility check when you start the $2 upgrade.

Pagestay shows no permission warning when you install it. The permission to follow your tabs is asked for only if you press **Enable page notes**. Scheduled backups ask for permission to save files only when you turn them on. Starting with Pagestay 1.0.1, there are no network requests, except a one-time check when you activate Pro and an eligibility check when you start the $2 upgrade.

The [Clipstay page](/clipstay/?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=copied-text-and-page-notes-chrome&utm_content=cta-clipstay) has the free plan and Pro. The [Clipstay privacy policy](/clipstay/privacy/) lists what is stored. [Add Clipstay from the Chrome Web Store](https://chromewebstore.google.com/detail/biellalamlbfmgljmpfppaebblmmhokn?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=copied-text-and-page-notes-chrome&utm_content=cta-clipstay-bottom).

The [Pagestay page](/pagestay/?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=copied-text-and-page-notes-chrome&utm_content=cta-pagestay) lists the free plan and Pro. The [Pagestay privacy policy](/pagestay/privacy/) lists what is stored. [Add Pagestay from the Chrome Web Store](https://chromewebstore.google.com/detail/lehddjgolnpdbmmijbefdffhblbgiejj?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=copied-text-and-page-notes-chrome&utm_content=cta-pagestay-bottom).
