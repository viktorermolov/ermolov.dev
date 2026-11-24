(function () {
  "use strict";

  var root = document.documentElement;
  var toggle = document.querySelector(".theme-toggle");
  var storedTheme = null;
  try { storedTheme = localStorage.getItem("theme"); } catch (_) { /* Storage is optional. */ }
  if (storedTheme !== "light" && storedTheme !== "dark") storedTheme = null;
  var themeQuery = window.matchMedia("(prefers-color-scheme: dark)");
  function applyTheme(theme) {
    root.dataset.theme = theme;
    if (toggle) {
      toggle.setAttribute("aria-pressed", String(theme === "dark"));
      toggle.setAttribute("aria-label", theme === "dark" ? "Switch to light theme" : "Switch to dark theme");
    }
  }
  applyTheme(storedTheme || (themeQuery.matches ? "dark" : "light"));
  if (toggle) toggle.addEventListener("click", function () {
    storedTheme = root.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(storedTheme);
    try { localStorage.setItem("theme", storedTheme); } catch (_) { /* Keep the current page preference. */ }
  });
  function followSystemTheme(event) { if (!storedTheme) applyTheme(event.matches ? "dark" : "light"); }
  if (themeQuery.addEventListener) themeQuery.addEventListener("change", followSystemTheme);
  else if (themeQuery.addListener) themeQuery.addListener(followSystemTheme);

  // Copy-address button: shown only when the browser can copy. The mailto link always works.
  var copy = document.querySelector(".copy-btn");
  var copyStatus = document.getElementById("copy-status");
  if (copy && navigator.clipboard && navigator.clipboard.writeText) {
    copy.hidden = false;
    var resetTimer = null;
    copy.addEventListener("click", function () {
      navigator.clipboard.writeText(copy.dataset.copy).then(function () {
        copy.textContent = "Copied";
        if (copyStatus) copyStatus.textContent = "Address copied";
      }, function () {
        copy.textContent = "Copy failed";
        if (copyStatus) copyStatus.textContent = "Could not copy the address";
      }).then(function () {
        clearTimeout(resetTimer);
        resetTimer = setTimeout(function () { copy.textContent = "Copy address"; if (copyStatus) copyStatus.textContent = ""; }, 2200);
      });
    });
  }

  // Clicks to our Chrome Web Store listings. The tag is the existing gtag snippet;
  // if that snippet is absent, there is nothing to send. Other listings are ignored.
  var storeProducts = {
    biellalamlbfmgljmpfppaebblmmhokn: "clipstay",
    lehddjgolnpdbmmijbefdffhblbgiejj: "pagestay"
  };

  function storeProduct(url) {
    var parts = url.pathname.split("/");
    var i;
    for (i = 0; i < parts.length; i++) {
      if (storeProducts[parts[i]]) return storeProducts[parts[i]];
    }
    return "";
  }

  function isStoreListing(url) {
    if (url.hostname === "chromewebstore.google.com") return true;
    return url.hostname === "chrome.google.com" && url.pathname.indexOf("/webstore") === 0;
  }

  function linkLocation(link) {
    var path = window.location.pathname.replace(/^\/+|\/+$/g, "");
    var section = "page";
    if (link.closest(".product-hero")) section = "hero";
    else if (link.closest(".prose")) section = "article";
    else if (link.closest(".button-row")) section = "cta";
    return (path || "home") + "/" + section;
  }

  document.addEventListener("click", function (event) {
    var target = event.target;
    var link = target && target.closest ? target.closest("a[href]") : null;
    if (!link || typeof window.gtag !== "function") return;
    var url;
    try { url = new URL(link.href); } catch (error) { return; }
    if (!isStoreListing(url)) return;
    var product = storeProduct(url);
    if (product !== "clipstay" && product !== "pagestay") return;
    window.gtag("event", "cws_click", {
      product: product,
      link_location: linkLocation(link),
      link_url: link.href,
      transport_type: "beacon"
    });
  });
})();
