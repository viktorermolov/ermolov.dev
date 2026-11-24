---
title: "Using Chrome’s side panel for notes while you read (Pagestay)"
description: "Keep a note beside the page you are reading in Chrome’s side panel, and see what Chrome’s own panels already do."
date: 2026-11-23
weight: 3
---

You can keep a note beside a web page while you read it. Chrome’s side panel is the column that sits next to the page. The panels Chrome includes are for bookmarks, history, a reading list, Reading mode and Google Lens. None of those is a note you write and see again on that page. An extension can add its own panel. That is the piece that holds the note.

## What the side panel already shows

On a computer, open Chrome and go to a page. At the top right, select **More**. Google’s help lists these ways to open a panel:

- **Bookmarks:** Bookmarks and lists, then Show all bookmarks.
- **Reading list:** Bookmarks and lists, then Reading list, then Show reading list.
- **History:** History, then Show history in side panel.
- **Reading mode:** More tools, then Reading mode.
- **Google Lens:** Search with Google Lens.

Next to the icon name, select **Pin to toolbar**. The icon then sits on the left, next to Profile, so you can open that panel again without the menu. To remove it, select the icon and then **Unpin from toolbar**.

[Manage Chrome side panel](https://support.google.com/chrome/answer/13156494?hl=en) is Google’s page for those steps.

A bookmark stores the address and the name you give it, so you can open the page again. [Create, find and edit bookmarks](https://support.google.com/chrome/answer/188842?hl=en) is the guide. A reading list stores pages you want to open later. You can also download a page to read offline. [Read pages later and offline](https://support.google.com/chrome/answer/7343019?hl=en) covers both. History is the list of pages you have visited.

Signing in to Chrome can save bookmarks, the reading list and other items in your Google Account, so they are available on computers where you use the same account. [Get your bookmarks, passwords and more on all your devices](https://support.google.com/chrome/answer/165139?hl=en) lists what that sign-in includes. A bookmark, a reading-list entry and a history row are still the address. They are not a paragraph you wrote about the page.

## An extension panel

Chrome lets an extension show its own page in the side panel, beside the site. The extension’s panel can stay available while you move between tabs, when the extension is set up that way. Opening the panel is something you do: a click on the toolbar icon, a keyboard shortcut, or another gesture. `sidePanel.open()` may only be called in response to a user action. An extension does not get to pop the panel open in the background. The reference is [chrome.sidePanel](https://developer.chrome.com/docs/extensions/reference/sidePanel).

The panel is already next to the page. A notes extension puts your text in it.

## Notes in the panel while you read

[Pagestay](/pagestay/) keeps notes in that side panel. There is no account and no sync. [Add it from the Chrome Web Store](https://chromewebstore.google.com/detail/lehddjgolnpdbmmijbefdffhblbgiejj?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=chrome-side-panel-notes&utm_content=cta-top).

Pagestay needs Chrome 130 or newer. Click the Pagestay button on the toolbar. The suggested shortcut is Control+Shift+N on a Mac and Alt+Shift+N on other systems. On a Mac that shortcut uses the Control key, not Command. Chrome turns a plain Ctrl shortcut into Command on a Mac, unless the extension asks for the Control key by name. Change the shortcut at `chrome://extensions/shortcuts`. Extension shortcuts work while Chrome is the window in front. If another extension already uses those keys, Chrome can leave this one unset, and that page is where you assign a free combination. Some operating-system and Chrome shortcuts always take priority and cannot be replaced. The reference is [chrome.commands](https://developer.chrome.com/docs/extensions/reference/commands).

The page stays in view while you write. **New note** attaches to the page you are on when Pagestay can see that tab’s address. **Note for this site** is the whole host, such as `example.com`. **Global note** is not attached to a page or a site. A `chrome://` page or a `file` page cannot take a page note or a site note. A new note there is global. How a page address differs from a site address, including the query string, is in [Take notes on a specific website in Chrome, without an account](/notes/notes-on-a-website-chrome/).

Pagestay does not read the words on the page. It has no content scripts and no access to page content. It uses the tab’s address to find notes you attached. It does not save your browsing history, or the pages you visit without writing a note.

Clicking the toolbar button, or using the shortcut, lets Pagestay read the address of that one tab, for that visit. To keep the panel following your tabs without another click, and to show a dot on the button when the page or site has a note, press **Enable page notes**. Chrome then asks for the tabs permission, which it describes as reading your browsing history. Pagestay uses those addresses on your device to find your notes, and does not send them anywhere. Without that permission, Pagestay still works on the tab where you click its button.

Notes are saved as you type. They stay on that computer, in Chrome’s local extension storage. Uninstalling the extension removes what it stored. The free plan has unlimited notes in the side panel: page notes, site notes and global notes. Each note keeps up to 20 earlier versions. A single note whose text is over 1 MB is not saved. Where that storage lives, and how to export a copy, is in [Where your browser notes actually live, and how to back them up](/notes/browser-notes-backup/).

Pro is $4.99, paid once. It adds search inside the text of your notes and by tag, folders and tags, rule notes for a URL pattern you type (such as `example.com/docs/*`), and scheduled backups on the computer. A rule note is shown when you open the panel on a matching page. Pagestay does not open the panel for you. Page notes and site notes are on the free plan. Clipstay and Pagestay together are $6.99 as a bundle, which unlocks Pro in both.

The [Pagestay page](/pagestay/) lists the free plan and Pro. The [privacy policy](/pagestay/privacy/) is the account of what is stored. [Add Pagestay from the Chrome Web Store](https://chromewebstore.google.com/detail/lehddjgolnpdbmmijbefdffhblbgiejj?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=chrome-side-panel-notes&utm_content=cta-bottom).
