---
# One file per product. The homepage lists every page with `type: project`, sorted by weight.
# status: pending-review | live | archived
#   The site never shows "Pending review". Until the status is `live`, visitors see
#   "Coming soon to the Chrome Web Store" and no store link. When Chrome Web Store
#   publishes the item, change `status` to `live`; `storeURL` is already filled in.
# privacyURL must be <product url>privacy/ (the page must exist). privacyLead and privacyNote are the
# product page's Privacy section text (both required, plain text only). footerPrivacy: false hides the product's privacy link in the footer.
title: "Clipstay — Clipboard History Manager"
name: "Clipstay"
description: "Clipstay is a Chrome extension that keeps your clipboard history on your device: search it, pin it and copy it back in one click. No account, no analytics."
headline: "Your clipboard history, saved."
tagline: "Your clipboard history, saved. Your clips never leave your device."
lede: "Clipstay saves everything you copy in Chrome, so you can search it, pin it and copy it back in one click. Your clips never leave your device."
date: 2026-10-05
weight: 1
url: "/clipstay/"
type: "project"
schemaType: "SoftwareApplication"
status: "live"
store: "Chrome Web Store"
itemID: "biellalamlbfmgljmpfppaebblmmhokn"
storeURL: "https://chromewebstore.google.com/detail/biellalamlbfmgljmpfppaebblmmhokn"
privacyURL: "/clipstay/privacy/"
privacyLead: "Your clips stay on your device. Clipstay has no account and no analytics, and makes no network requests, except a single one-time check when you activate Pro."
privacyNote: "It never captures password fields or Incognito windows, and you can exclude any site or pause capture."
icon: "/img/clipstay/icon-128.png"
cardImage: "/img/clipstay/history.webp"
cardImageAlt: "The Clipstay popup showing a list of recent clips, with three pinned. Caption: Your clipboard history, saved."
ogImage: "og/og-clipstay.png"
ogImageAlt: "Clipstay: your clipboard history, saved. A Chrome extension for clipboard history."
shortcuts:
  mac: "Control+Shift+V"
  other: "Alt+Shift+V"
highlights:
  - title: "Every copy, saved"
    text: "Copy or cut on any web page and Clipstay keeps it, even in tabs you opened before installing. When you open the popup it also adds what is on your clipboard right now, so text from other apps lands in your history too."
  - title: "Find it again in seconds"
    text: "Search your history, pin the clips you reuse and copy any of them back with one click. Open Clipstay from the keyboard with the shortcut below, then move through your clips with the arrow keys, copy with Enter, and pin with P."
    image: "/img/clipstay/search.webp"
    alt: "The Clipstay popup filtered by the word git, showing three matching clips. Caption: search by several words in any order, filter by date or pinned clips."
  - title: "You decide what it keeps"
    text: "Exclude any site, pause capture whenever you like, and export your history to JSON or CSV and import it back. Password fields and Incognito windows are never captured."
    image: "/img/clipstay/private.webp"
    alt: "The Clipstay settings page with a pause switch, an excluded sites list and the option to add the clipboard when the popup opens. Caption: Stays on your device."
  - title: "Free, with an optional Pro"
    text: "Pro removes the history and pin limits. $4.99, paid once, no subscription. Unlock it by entering your purchase email once. Search, export and import stay free."
    image: "/img/clipstay/pro.webp"
    alt: "The Plan section of Clipstay settings: free limits, Pro with unlimited history and pins for $4.99 one-time, a Buy Pro button and a field to activate with your purchase email."
features:
  - "Saves copy and cut on every web page"
  - "Works in tabs opened before you installed"
  - "Adds your clipboard when the popup opens (optional)"
  - "Instant search"
  - "Pins for the clips you reuse"
  - "One-click copy back"
  - "Keyboard shortcut"
  - "Excluded sites and a pause switch"
  - "Keyboard control in the popup: search, arrows, Enter to copy, P to pin"
  - "Delete a clip with undo for 5 minutes"
  - "Export to JSON and CSV and import them back, always free"
proPlan: "Pro: $4.99 one-time, unlimited history and pins. Search, export and import stay free. Clipstay and Pagestay together are $6.99 as a bundle, which unlocks Pro in both; if you already own one, the other is a $2 upgrade."
refundsURL: "/clipstay/refunds/"
freePlan: "The free plan keeps your 100 most recent unpinned clips, plus up to 5 pinned clips on top. When the history is full, the oldest unpinned clips make room for new ones, and Clipstay lets you know. Pinned clips never roll off. Exporting to JSON or CSV is always free. Importing a file keeps the newest 100 unpinned clips overall, and pinned clips are always kept."
goodToKnow:
  - "Clipstay captures text you copy or cut on web pages in Chrome."
  - "For other apps, it adds whatever is on your clipboard at the moment you open the popup. It does not run in the background of other apps."
  - "Clipstay stores text only."
supportNote: "Include your Chrome version and operating system if you can, and leave out any private text you copied."
faq:
  - q: "Where is my clipboard history stored?"
    a: "On your device, in Chrome's local extension storage. Clipstay makes no network requests, except a single one-time check when you activate Pro. Uninstalling it removes the data."
  - q: "How do I keep passwords out of my history?"
    a: "Clipstay never captures password fields. If you copy passwords from a password manager, turn off “Add clipboard when the popup opens” in Settings."
  - q: "How do I keep a clip for good?"
    a: "Pin it. You can pin up to 5 clips, and pinned clips stay when older ones make room. You can also export your history at any time."
  - q: "How do I save text from other apps?"
    a: "Copy it in the app, then open Clipstay. It adds what is on your clipboard at that moment."
  - q: "How do I take my history with me?"
    a: "Export it to JSON or CSV at any time and import the file on another computer in Settings. Export and import are always free. On the free plan an import keeps the newest 100 unpinned clips overall."
  - q: "Can I undo a delete?"
    a: "Yes. After you delete a clip, press Undo or Ctrl/Cmd+Z within 5 minutes, even if you closed the popup. Undo covers the last clip you deleted."
  - q: "Switching from an extension removed in the Manifest V2 cleanup?"
    a: "Clipstay keeps a local text history of what you copy in Chrome."
    link:
      text: "See what it covers and what is different."
      href: "/clipstay/alternatives/"
---
