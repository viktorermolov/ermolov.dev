---
title: "Reuse the text you type every day: pins and keyboard shortcuts in Chrome (Clipstay)"
description: "Pin text you paste often and open it from the keyboard in Chrome, including what Windows already pins and what an extension adds."
date: 2026-11-23
weight: 4
---

Text you paste every day does not have to be typed again. Copy it once, pin it, and open the list from the keyboard the next time you need it. Chrome itself does not keep a clipboard history, and it does not pin copied text. Windows can pin items in its own clipboard history. A Chrome extension can pin the text you copy on web pages and open that list over the page.

## What you can pin without an extension

On Windows, press the Windows logo key + V. The first time, select **Turn on**. You can pin items you use often. Windows keeps 25 copied entries. Older items are removed unless you pin them. Restarting the PC clears the history except for pinned items. Text, HTML and bitmap images are supported, up to 4 MB per item. Sync to other Windows PCs is optional and uses a Microsoft account or a work account. Leave it off when this PC should be the only place the history lives. Microsoft’s guide: [Using the clipboard](https://support.microsoft.com/en-us/windows/apps/using-the-clipboard).

Mac and ChromeOS have their own short histories. The steps and the limits are in [How to see your clipboard history in Chrome](/notes/clipboard-history-chrome/). Those lists belong to the operating system. They include copies from other apps. They are not a list of pinned snippets inside Chrome, and they are not limited to text you copied on a web page.

A document or a sticky note can also hold a sentence you reuse. You leave the page to get it. That is enough when the sentence lives in one file. It is a poor fit when you want the sentence in a list you open over the page, then paste.

## Pins inside Chrome

[Clipstay](/clipstay/) keeps a text history of what you copy or cut on supported web pages, and lets you pin the clips you want again. There is no account. [Add it from the Chrome Web Store](https://chromewebstore.google.com/detail/biellalamlbfmgljmpfppaebblmmhokn?utm_source=ermolov.dev&utm_medium=article&utm_campaign=pins-shortcuts-chrome&utm_content=cta-top).

Copy or cut the text on a page. Open Clipstay. Pin the clip. Pinned clips stay when the free history is full: a new clip can replace the oldest unpinned one, and a pinned clip does not roll off for that reason. On the free plan you can add a pin while fewer than five clips are pinned. Clips and pins you already have, including ones you import, stay even when they are above those numbers. Free also includes 100 unpinned clips. Pro is $4.99, paid once, and removes the history and pin limits. Search, export and import stay free. Clipstay and Pagestay together are $6.99 as a bundle, which unlocks Pro in both.

You can give a pinned clip a name. In the popup, **N** names the selected pin. A name is optional, up to 60 characters, and it stays on the device. Search matches every word you type, in any order, in the clip text or in that name. You can also filter the list by date. The date filter is All time, Today, Past week or Past month. You can show pinned clips only.

Clipstay stores text only. Each clip stores up to 100 KiB of text. Longer text is cut to that size on the free plan and on Pro. Images stay in the operating-system clipboard. Clipstay does not save the address of the page you copied from. Web-page capture skips password fields and Incognito pages. Chrome-restricted pages, such as the Chrome Web Store and `chrome://` pages, do not allow automatic capture. You can exclude sites, or pause capture, in Settings.

Copying a clip back puts it on the clipboard. You paste it yourself where you need it. Enter does that for the selected clip, and so does a click. With “Add clipboard when the popup opens” turned on, opening the popup can also save text already on the system clipboard, including text from other apps. Clipstay does not watch other apps in the background. Turn the option off in Settings when you do not want that import.

## Open the list from the keyboard

The suggested shortcut opens Clipstay: Control+Shift+V on a Mac, and Alt+Shift+V on Windows, Linux and ChromeOS. On a Mac that is the Control key, not Command. Chrome’s command shortcuts turn a plain Ctrl into Command on a Mac. An extension that wants the Control key names it `MacCtrl`, which is what Clipstay’s Mac shortcut uses. On a Mac keyboard, Alt is the Option key.

Change the shortcut at `chrome://extensions/shortcuts`. Settings shows the shortcut that is actually assigned, or “not set”, and **Change shortcut** opens that page. Chrome does not give two extensions the same shortcut. If another extension already uses those keys, this one can be left blank until you pick a free combination. Operating-system and Chrome shortcuts, such as window management, take priority and cannot be overridden.

Extension shortcuts are active while Chrome is the focused window. They do not run when another app is in front, unless the command is marked global. Clipstay’s open shortcut is not global. The reference is [chrome.commands](https://developer.chrome.com/docs/extensions/reference/commands).

Once the popup is open, Settings lists these keys:

- **/** focuses search.
- **Up** and **Down** move through the clips.
- **Enter** copies the selected clip.
- **P** pins or unpins it.
- **N** names a pin.
- **Delete** or **Backspace** deletes it.
- **Ctrl+Z**, or **Command+Z** on a Mac, undoes the last delete. Undo lasts 5 minutes, including if you closed the popup. Only the last deleted clip can be undone.
- **Home** and **End** jump to the first or last clip.
- **Esc** clears the search.

Export the history to JSON or CSV at any time, and import that file on another computer. JSON keeps pins, names and dates. CSV has the text and the date, and names when you have any. The file name starts with `clipstay-` and the UTC date. Export and import are free. The file stays on your machine. Uninstalling Clipstay removes the stored history.

The [Clipstay page](/clipstay/) has the free plan, Pro and the shortcut. The [privacy policy](/clipstay/privacy/) lists what is stored, including optional names for pinned clips. [Add Clipstay from the Chrome Web Store](https://chromewebstore.google.com/detail/biellalamlbfmgljmpfppaebblmmhokn?utm_source=ermolov.dev&utm_medium=article&utm_campaign=pins-shortcuts-chrome&utm_content=cta-bottom).
