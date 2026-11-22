---
title: "Take notes on a specific website in Chrome, without an account"
description: "Keep a note for one page or a whole site in Chrome without an account, and see where that note is stored."
date: 2026-11-22
weight: 2
---

You can keep a note for one web page, or for every page on a site, in Chrome without an account. The note stays on that computer and can be opened again with the page.

Chrome itself has no place to write that note. A bookmark stores the address and the name you give it. Opening the bookmark later brings back the page, not a note about it. A doc or a sticky note in another app can hold the same words, as a separate file. Nothing in Chrome opens that file when you return to the site. Google Docs and Google Keep use a Google account. Notes apps on a Mac or a Windows PC can sync through the account on that computer when you want the note on another device. None of them attach the note to one page, or to a whole site, and leave it only on this computer.

## What you can do without an extension

Bookmark the page when you only need the address again. Copy the text into a document, Keep, Notes, or a sticky note when the words only need to exist once, somewhere else. Sign in when you want that file on your phone or another computer. The address bar can find a page you have visited. It does not store a note for the site.

When the note should come back with the page, it has to be attached to the address and stored where Chrome can show it.

## A note for a page, or a note for the site

[Pagestay](/pagestay/) keeps notes in Chrome’s side panel, next to the page you are reading. There is no account and no sync. [Add it from the Chrome Web Store](https://chromewebstore.google.com/detail/lehddjgolnpdbmmijbefdffhblbgiejj?utm_source=ermolov.dev&utm_medium=article&utm_campaign=notes-on-a-website-chrome&utm_content=cta-top).

Click the Pagestay button on the page. The suggested shortcut is Control+Shift+N on a Mac and Alt+Shift+N on other systems. **New note** attaches to the page you are on when Pagestay can see that tab’s address. Without an address, the new note is global. The panel also offers **Note for this site**, and **Global note** for a note that is not attached to any page or site.

A page note and a site note use different addresses.

- A **page note** is that page: the scheme (`http` or `https`), the host, the port, and the path. `https://example.com/docs/setup` and `https://example.com/docs/install` are different pages, so each can have its own note. The part after `#` is dropped. The query string, the part after `?`, is left off unless you turn on “Treat ?query as part of the page” for that site. A trailing slash is ignored, except on the site’s root.
- A **site note** is the hostname only, such as `example.com`. It matches every page on that host, so opening the panel on any of those pages shows the note. `www.example.com` is a different host from `example.com`, so the two do not share site notes. The port is not part of a site note: `localhost:3000` and `localhost:4000` share them. Matching uses the host name, so `http` and `https` on that host share site notes too.
- A **global note** is not attached. It stays available no matter which page is open.

A `chrome://` page or a `file` page cannot take a page note or a site note. A new note there is global.

Pagestay does not read the words on the page. It has no content scripts and no access to page content. It uses the tab’s address to find notes attached to that page or site. It stores an address or a pattern for a note you attach. It does not save your browsing history, or the pages you visit without writing a note. The one exception is “Treat ?query as part of the page”: turning it on remembers that site’s host name even when no note is attached there.

Clicking the toolbar button (or using the shortcut) lets Pagestay read the address of that one tab, for that visit. To keep the panel following your tabs without another click, and to show a dot on the button when the page or site has a note, press **Enable page notes**. Chrome then asks for the tabs permission, which it describes as reading your browsing history. Pagestay uses those addresses on your device to find your notes, and does not send them anywhere.

Pagestay needs Chrome 130 or newer.

## Where the notes are stored

Notes stay on that computer, in Chrome’s local extension storage. Pagestay has no account, no sync, and no analytics. Notes are not copied to a server, and they do not show up on another computer by themselves. The addresses a note is attached to stay on the device as well. Uninstalling the extension removes what it stored. Export to JSON or Markdown first if you want a copy you can keep. Export is free, and a Pagestay JSON file can be imported on another computer.

The free plan has unlimited notes in the side panel: page notes, site notes, and global notes, saved as you type. Each note keeps up to 20 earlier versions. Deleted notes stay in the trash, and Settings can delete them 30 days after they were moved there. Turn that off and they stay until you empty the trash. A filter by title is free. A single note whose text is over 1 MB is not saved.

Pro is $4.99, paid once. It adds search inside the text of your notes and by tag, folders and tags, rule notes for a URL pattern you type (such as `example.com/docs/*`), and scheduled backups saved on the computer. Page notes and site notes are on the free plan.

The [Pagestay page](/pagestay/) lists the free plan and Pro. The [privacy policy](/pagestay/privacy/) is the full account of what is stored. [Add Pagestay from the Chrome Web Store](https://chromewebstore.google.com/detail/lehddjgolnpdbmmijbefdffhblbgiejj?utm_source=ermolov.dev&utm_medium=article&utm_campaign=notes-on-a-website-chrome&utm_content=cta-bottom).
