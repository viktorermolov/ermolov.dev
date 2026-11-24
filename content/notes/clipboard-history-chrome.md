---
title: "How to see your clipboard history in Chrome (Mac, Windows, ChromeOS)"
description: "See clipboard history on Windows, Mac, and ChromeOS with the tools already on the computer, and when a Chrome extension is the better place to keep text you copy."
date: 2026-11-22
weight: 1
---

To see clipboard history while you are in Chrome, open the history the computer already keeps. Copying and pasting in a Chrome window uses that system clipboard.

- **Windows:** press the Windows logo key + V. The first time, select **Turn on**.
- **Mac:** press Command-Space to open Spotlight, then Command-4. The first time, choose **Allow**.
- **Chromebook:** press Search+V. If that key is labeled Launcher, press Launcher+V.

Those lists are short, and they differ. The steps below are the limits of each one. After that: when a Chrome extension is the better place to keep text you copy on web pages.

## Windows

Press the Windows logo key + V. Select **Turn on** if Windows asks.

Windows keeps 25 copied entries. Text, HTML, and bitmap images are supported, up to 4 MB per item. Older items are removed to make room, unless you pin them. Restarting the PC clears the history except for pinned items. From the same panel you can delete one item, or clear everything except what you pinned.

Sync to other Windows PCs is optional. It uses a Microsoft account or a work account. The switch is under Start > Settings > System > Clipboard. Leave it off when this PC should be the only place the history lives.

Microsoft’s guide: [Using the clipboard](https://support.microsoft.com/en-us/windows/apps/using-the-clipboard).

## Mac

Apple’s Mac User Guide describes clipboard history inside Spotlight.

1. Press Command-Space to open Spotlight.
2. Press Command-4, or use the Clipboard control beside the search field.
3. The first time, choose **Allow**. Apple notes that sensitive information may appear.
4. Search, or look through the recent items. Copy one with Command-C, then paste it with Command-V where you need it.
5. To erase the history, open the control beside the search field and choose **Clear History**.

How long items stay searchable is a setting. Open System Settings > Spotlight. Under “Clipboard history is available in Spotlight,” choose 30 minutes, 8 hours, or 7 days. Items older than that period disappear from Spotlight. The same settings screen clears the history. **Results from Clipboard** controls whether clipboard contents appear in Spotlight.

If Spotlight settings on your Mac have no Clipboard controls, this history is not available there. Command-V still pastes only what is on the clipboard now.

Universal Clipboard is a separate feature. It copies the current item to another nearby Apple device signed in to the same Apple Account, for a short time. Apple’s page: [Copy and paste between your devices](https://support.apple.com/guide/mac-help/copy-and-paste-between-devices-mchl70368996/mac).

The Spotlight steps: [Search your Clipboard history in Spotlight](https://support.apple.com/guide/mac-help/search-your-clipboard-history-mchl40d5b86b/mac) and [Spotlight settings](https://support.apple.com/guide/mac-help/spotlight-settings-on-mac-mchl54d95e8a/mac).

## ChromeOS

On a Chromebook, press Search+V. Where the key is labeled Launcher, press Launcher+V. With a Windows or Mac keyboard attached, Google’s shortcut help says to use the Windows key or the Command key in place of Search or Launcher.

ChromeOS keeps five clipboard items. Copying a sixth drops the oldest. The menu can hold text and images. On a work or school Chromebook, a policy can turn clipboard history off: the menu then stays closed and stored items are cleared.

[Chromebook keyboard shortcuts](https://support.google.com/chromebook/answer/183101?hl=en) is Google’s list, including that key substitution.

## Where the built-in history stops

These tools answer what you copied a moment ago.

- Windows stops at 25 entries. Unpinned items are gone after a restart. A pin keeps an item. Sync across PCs needs a Microsoft account or a work account.
- Spotlight on a Mac keeps clipboard history only for the period you choose, at most 7 days. It is a search of recent copies.
- ChromeOS keeps five items.
- All three record the system clipboard, including copies from other apps. They are not a history of only the text you copied on web pages, and they are not a list of pinned snippets sitting inside Chrome.

Windows and ChromeOS also keep images in that history. A sentence you want again next week often falls off these short lists.

## When a Chrome extension helps

Use an extension when you want the text you copy on web pages in a list you can search and pin, kept on that computer, without turning on account sync. Keep using the system history for images and for the last few copies. The extension covers the text those short lists drop.

[Clipstay](/clipstay/) is a Chrome extension for that text history. [Add it from the Chrome Web Store](https://chromewebstore.google.com/detail/biellalamlbfmgljmpfppaebblmmhokn?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=clipboard-history-chrome&utm_content=cta-top).

## What Clipstay keeps

Copy or cut text on a web page in Chrome and Clipstay saves it. Open the popup to search the list, pin a clip you reuse, and copy it back in one click. The suggested shortcut is Control+Shift+V on a Mac and Alt+Shift+V on other systems. Change it at `chrome://extensions/shortcuts`.

Clips stay on the computer, in Chrome’s local extension storage. Clipstay has no account. Each clip keeps the text and the time it was copied. Clipstay does not save the address of the page you copied from. Uninstalling the extension removes the stored data.

A few limits matter before you rely on it:

- Clipstay stores text only. Images stay in the operating-system clipboard. Each clip stores up to 100 KiB of text. Longer text is cut to that size on the free plan and on Pro.
- Web-page capture skips password fields and Incognito pages. Chrome-restricted pages, such as the Chrome Web Store and `chrome://` pages, do not allow automatic capture. You can exclude sites, or pause capture, in Settings.
- Free includes 100 unpinned clips, and you can add a pin while fewer than five clips are pinned. Clips and pins you already have, including ones you import, stay even when they are above those numbers. When the free history is full, a new clip can replace the oldest unpinned one. Pinned clips are kept. Pro is $4.99, paid once, and removes the history and pin limits. Search, export, and import stay free.
- With “Add clipboard when the popup opens” turned on, opening the popup can also save text already on the system clipboard, including text from other apps. Clipstay does not watch other apps in the background. Turn the option off in Settings when you do not want that import.
- Export the history to JSON or CSV at any time, and import the file on another computer. The file stays on your machine.

The [Clipstay page](/clipstay/) has the free plan, Pro, and the shortcut. The [privacy policy](/clipstay/privacy/) lists what is stored. [Add Clipstay from the Chrome Web Store](https://chromewebstore.google.com/detail/biellalamlbfmgljmpfppaebblmmhokn?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=clipboard-history-chrome&utm_content=cta-bottom).
