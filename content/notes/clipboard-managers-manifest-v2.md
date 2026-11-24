---
title: "Clipboard managers after Manifest V2: what changed (Clipstay)"
description: "See what Chrome did to Manifest V2 extensions, what the operating system still keeps, and how a Manifest V3 extension stores text you copy."
date: 2026-11-23
weight: 6
---

If a clipboard extension disappeared from Chrome, the clipboard on the computer is still there. What changed is Chrome’s rules for extensions. Manifest V2 extensions were turned off, and on August 31, 2026 the remaining ones were removed from the Chrome Web Store. The operating system’s own history did not move. A Manifest V3 extension can still keep text you copy on web pages.

## The history that did not move

Windows, Mac and ChromeOS still keep a short clipboard history outside the extension. On Windows, press the Windows logo key + V. On a Mac, Spotlight can search recent clipboard items. On a Chromebook, press Search+V, or Launcher+V where the key has that label. The steps, and the limits of each list, are in [How to see your clipboard history in Chrome](/notes/clipboard-history-chrome/). Those tools are not extensions. The Manifest V2 change did not remove them. They also are not a searchable list of only the text you copied on web pages.

## What Chrome did to Manifest V2

Google’s page is the [Manifest V2 support timeline](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline). The dates below are the ones on that page.

In January 2022 the Chrome Web Store stopped accepting new public or unlisted Manifest V2 extensions. In June 2022 it stopped accepting new private ones.

On June 3, 2024 the phase-out began on Chrome Beta, Dev and Canary. People with Manifest V2 extensions could see a warning on `chrome://extensions`, and Manifest V2 extensions with the Featured badge lost that badge.

From October 9, 2024 Chrome started disabling installed Manifest V2 extensions on the stable channel, rolled out over the following weeks. People were sent to the Chrome Web Store for a Manifest V3 alternative. For a short time they could still turn a disabled Manifest V2 extension back on. Enterprises using the ExtensionManifestV2Availability policy stayed exempt from the browser changes until June 2025.

On March 31, 2025 Manifest V2 extensions were disabled by default on all channels, and people could still turn them back on. The same section of the timeline says Chrome 138 is the final version of Chrome that supports Manifest V2 extensions, and only when paired with that enterprise policy. Support is removed in the Chrome 139 branch, for everyone on Chrome 139 at once, unlike the earlier disablement that rolled out gradually.

On July 24, 2025, with Chrome 138, the timeline says Manifest V2 extensions are disabled for all users on all channels, and users can no longer turn them back on. The enterprise policy is removed with Chrome 139. Manifest V2 extensions then cease to function for anyone upgrading to Chrome 139 or a later version.

On August 31, 2026 the remaining Manifest V2 extensions were removed from the Chrome Web Store. The timeline says existing installs on Chrome 138 or earlier continue to run, and that they can no longer receive updates or be reinstalled if removed.

This note does not suggest staying on an old version of Chrome. The timeline is the source for which Chrome version can still run a Manifest V2 extension, and for the store removal. An install that has taken the Chrome updates described there, through Chrome 139 or later, does not run Manifest V2 extensions.

## What Manifest V3 changed for a clipboard extension

Manifest V3 replaces the extension background page with a service worker. Google’s guide is [Migrate to a service worker](https://developer.chrome.com/docs/extensions/develop/migrate/to-service-workers).

A background page was an environment that lived independent of any window or tab, so an extension could observe and act on events from there. A service worker runs when it is needed and then stops. It does not keep state in global variables across those stops. Timers in it can end when the worker stops, which is why periodic work moves to alarms. It cannot use the DOM or the `window` object. The same guide says service workers cannot read the clipboard. Starting in Chrome 157, a service worker with the clipboard-write permission can write text to the clipboard. Reading is still not available in the service worker.

A clipboard extension cannot rely on a background page that stays open and reads the clipboard all day. The service worker that replaced that page cannot read the clipboard. That is a limit of the extension platform. It is not a limit of the system clipboard, which the first section still uses.

## A Manifest V3 history for text you copy in Chrome

[Clipstay](/clipstay/) is a Manifest V3 extension. It saves text you copy or cut on supported web pages, keeps it on the computer, and lets you search it, pin it and copy it back. There is no account and no analytics. [Add it from the Chrome Web Store](https://chromewebstore.google.com/detail/biellalamlbfmgljmpfppaebblmmhokn?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=clipboard-managers-manifest-v2&utm_content=cta-top).

The save happens when you copy or cut on the page, including in tabs that were already open. Clipstay does not watch other apps in the background. If “Add clipboard when the popup opens” is on, and capture is active, opening the popup can save text that is already on the system clipboard, including text from another app. That read happens because you opened the popup. Turn the option off in Settings when you do not want it. Web-page capture skips password fields and Incognito pages. Chrome-restricted pages, such as the Chrome Web Store and `chrome://` pages, do not allow automatic capture.

The suggested shortcut is Control+Shift+V on a Mac and Alt+Shift+V on other systems. Change it at `chrome://extensions/shortcuts`. Pins, the keys inside the popup, and the free limits are in [Reuse the text you type every day: pins and keyboard shortcuts in Chrome](/notes/pins-shortcuts-chrome/). Each clip stores up to 100 KiB of text. Longer text is cut to that size on the free plan and on Pro. Free includes 100 unpinned clips, and you can add a pin while fewer than five clips are pinned. Clips and pins you already have, including ones you import, stay even above those numbers. Pro is $4.99, paid once, and removes the history and pin limits. Search, export and import stay free.

Installing Clipstay does not restore another extension’s saved history. If the old extension exported a file, keep that file. Do not assume the new extension can read it. Clipstay imports a JSON or CSV file exported from Clipstay, in Settings, and that import is free. Export from Clipstay the same way when you want a copy outside the extension. The file stays on your machine. Uninstalling Clipstay removes what it stored in Chrome.

[What Clipstay covers, and what is different](/clipstay/alternatives/), is the page for that comparison. This note does not restate it.

The [Clipstay page](/clipstay/) has capture, the free plan and Pro. The [privacy policy](/clipstay/privacy/) lists what is stored and which permissions are used. [Add Clipstay from the Chrome Web Store](https://chromewebstore.google.com/detail/biellalamlbfmgljmpfppaebblmmhokn?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=clipboard-managers-manifest-v2&utm_content=cta-bottom).
