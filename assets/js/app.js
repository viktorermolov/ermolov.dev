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
})();
