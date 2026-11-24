---
title: "Where your browser notes actually live, and how to back them up (Pagestay)"
description: "See where notes in Chrome are stored, why signing in does not copy them, and how to keep a file you can restore."
date: 2026-11-23
weight: 5
---

A note you type next to a web page lives with the tool that stored it. Signing in to Chrome does not turn that note into a file, and it does not copy an extension’s local storage to another computer. If you want a copy you can move, export one. Pagestay keeps notes on the device and treats the export as the backup.

## What Chrome already keeps

A bookmark is the address and a name. Chrome can save bookmarks, the reading list, passwords and other items in your Google Account when you sign in. Google’s list of that info includes extensions. [Get your bookmarks, passwords and more on all your devices](https://support.google.com/chrome/answer/165139?hl=en) is the guide. A bookmark is still not the paragraph you wanted to remember about the page.

Saving the page itself stores the page as a file: **More**, then **More tools**, then **Save page as**. [Download a file](https://support.google.com/chrome/answer/95759?hl=en) includes that step, and the download setting **Ask where to save each file before downloading** (Settings, then Downloads). That file is the page. It is not a note you wrote beside it.

Google Docs and Google Keep keep text in a Google account. A notes app on the computer can sync through the account on that computer. Those are separate files. Nothing in Chrome opens them when you return to the site. [Take notes on a specific website in Chrome, without an account](/notes/notes-on-a-website-chrome/) is the note on attaching text to a page or a site instead.

## Where a Pagestay note lives

[Pagestay](/pagestay/) stores notes in Chrome’s local extension storage, `chrome.storage.local`, on that computer. There is no account, no sync and no analytics. [Add it from the Chrome Web Store](https://chromewebstore.google.com/detail/lehddjgolnpdbmmijbefdffhblbgiejj?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=browser-notes-backup&utm_content=cta-top).

Chrome’s storage API describes that area as local to each machine. The data is cleared when the extension is removed. It is a different area from `chrome.storage.sync`, which is the area that syncs when Chrome sync is on. Clearing the cache and browsing history does not clear extension storage. The reference is [chrome.storage](https://developer.chrome.com/docs/extensions/reference/storage).

Notes are not copied to a server. They do not appear on another computer because you signed in. The addresses a note is attached to stay on the device as well. Pagestay does not save your browsing history, or the pages you visit without writing a note. It has no content scripts and no access to page content. Uninstalling Pagestay removes what it stored in the browser. A file you already exported stays on disk until you delete it.

What that local storage holds:

- The note text, a title, and when the note was created and changed.
- Where it is attached: a page, a site, a global note, or, on Pro, a rule pattern you typed.
- Up to 20 earlier versions of each note.
- Deleted notes in the trash. Settings can delete them 30 days after they were moved there. The checkbox is **Delete notes 30 days after they were moved to the trash**. Turn it off and they stay until you empty the trash.
- A copy of the note you are editing, written while you type, so the text can survive if the panel closes before the note is saved. That copy is removed once the note is saved or you discard the changes.

A single note whose text is over 1 MB is not saved. The free plan does not limit how many notes you can keep. Pagestay needs Chrome 130 or newer. How the side panel and page notes work is in [Using Chrome’s side panel for notes while you read](/notes/chrome-side-panel-notes/).

## A file you can keep

Export does not need Pro, and it does not ask for the downloads permission. The file is built in Settings and saved through a download link, so Chrome’s normal download settings apply.

**Export all notes (JSON)** saves a Pagestay JSON file. **Export notes (Markdown)** saves a Markdown file. The file name starts with `pagestay-` and the UTC date, such as `pagestay-2026-11-23.json`. If you want to pick the folder each time, turn on **Ask where to save each file before downloading**.

The JSON file is the one you can import. It includes your notes, including notes that are in the trash, and your folders. It does not include the earlier versions. Before it is written, Pagestay saves text that a closed panel had not stored yet, so that text is in the file. Markdown is the current notes, not the trash, as a file you can read. Pagestay does not import the Markdown file.

To restore, choose the JSON file in Settings. Read the preview. Nothing is written until you confirm. The preview counts new, updated and unchanged notes. It says when an entry will be skipped, and when a note over 1 MB will be cut to fit. **Undo last import** is there after an import that changed something. A file that is not a Pagestay export is refused, and nothing is written.

If you have notes and have not exported for two weeks, Settings shows “You have notes and have not exported a backup in 2 weeks.” That clock follows a JSON export, and a scheduled backup that finishes. A Markdown export does not reset it. The two weeks are counted from the install when you have never exported.

The extension on a second computer starts empty. Export the JSON on the first computer and import it on the second. There is no account that would carry the notes across.

## Scheduled backups on this computer

Pro can save a JSON copy on a schedule. The files stay on this computer. They go in `Downloads/Pagestay backups/` and Pagestay keeps the last 7, replacing the oldest, so the folder does not grow. The names are `pagestay-backup-1.json` through `pagestay-backup-7.json`. Choose every day or every week. The first backup runs when you turn the setting on. Later ones run while Chrome is open. If Chrome was closed when one was due, it runs the next time Chrome starts.

Turning backups on asks for permission to save files. Chrome asks only then. Turn off **Ask where to save each file before downloading**, or Chrome asks for a folder and Pagestay skips that unattended backup. Settings then tells you to turn that download setting off, and to turn scheduled backups off and on again. Turning scheduled backups off removes the permission to save files.

If Pro is no longer active, new scheduled backups pause. Files already in the folder stay where they are. Your notes in the extension stay either way. If a scheduled backup says the notes are too large for it, use **Export all notes (JSON)** instead.

Pro is $4.99, paid once. The bundle with Clipstay is $6.99 and unlocks Pro in both. Search inside notes, folders, tags and rule notes are the other Pro pieces. Export and import stay free without Pro.

The [Pagestay page](/pagestay/) lists the free plan and Pro. The [privacy policy](/pagestay/privacy/) is the full account of what is stored, and of backup files you saved. [Add Pagestay from the Chrome Web Store](https://chromewebstore.google.com/detail/lehddjgolnpdbmmijbefdffhblbgiejj?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=browser-notes-backup&utm_content=cta-bottom).
