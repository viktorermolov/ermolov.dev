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

  var form = document.getElementById("contact-form");
  if (!form) return;
  form.noValidate = true;
  var status = document.getElementById("form-status");
  var submit = form.querySelector("button[type=submit]");
  var submitLabel = submit.querySelector("span");
  submit.disabled = false;
  var verification = document.getElementById("contact-verification");
  var verificationStatus = document.getElementById("verification-status");
  var message = form.elements.message;
  var messageCount = document.getElementById("message-count");
  var context = form.querySelector(".form-context");
  var sitekey = form.dataset.sitekey || "";
  var endpoint = form.dataset.endpoint;
  var activeCta = "direct";
  var busy = false;
  var challengeToken = "";
  var widget = null;
  var challengeLoader = null;
  var attempts = new Map();
  var lastSuccessfulContent = null;
  var source = { utmSource: "", utmMedium: "", utmCampaign: "", referrer: "", cta: "direct" };

  function limited(value, length) {
    // Attribution is untrusted and optional: malformed URL text must not block a real inquiry.
    var clean = Array.from(String(value || "")).filter(function (character) {
      var code = character.charCodeAt(0);
      return character.length > 1 || code < 0xD800 || code > 0xDFFF;
    }).join("").replace(/[\u0000-\u001F\u007F]/g, "").trim();
    return clean.slice(0, length).replace(/[\uD800-\uDBFF]$/, "");
  }
  try {
    var search = new URLSearchParams(window.location.search);
    source.utmSource = limited(search.get("utm_source"), 80);
    source.utmMedium = limited(search.get("utm_medium"), 80);
    source.utmCampaign = limited(search.get("utm_campaign"), 80);
    if (document.referrer) {
      var referrerHost = limited(new URL(document.referrer).hostname, 120).toLowerCase();
      source.referrer = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/.test(referrerHost) ? referrerHost : "";
    }
  } catch (_) { /* Attribution never prevents an inquiry. */ }

  function showStatus(text, state, focus) {
    status.textContent = text;
    status.dataset.state = state || "";
    if (focus) status.focus({ preventScroll: true });
  }
  function showFieldError(name, text) {
    var input = form.elements[name];
    if (!input) return;
    input.setAttribute("aria-invalid", "true");
    var error = document.getElementById(name + "-error");
    if (error) error.textContent = text;
    if (input.closest(".form-context")) context.open = true;
  }
  function clearErrors() {
    form.querySelectorAll("[aria-invalid]").forEach(function (input) { input.removeAttribute("aria-invalid"); });
    form.querySelectorAll(".field-error").forEach(function (error) { error.textContent = ""; });
  }
  function validate() {
    clearErrors();
    var valid = true;
    var email = form.elements.email;
    if (!email.value.trim() || !email.validity.valid) {
      showFieldError("email", "Enter an email address I can reply to.");
      valid = false;
    }
    if (message.value.trim().length < 1 || message.value.length > 2500) {
      showFieldError("message", "Please write between 1 and 2,500 characters about your project.");
      valid = false;
    }
    if (!form.checkValidity()) valid = false;
    if (!valid) {
      showStatus("Please check the highlighted fields. Your note is still here.", "error", false);
      var first = form.querySelector("[aria-invalid=true], :invalid");
      if (first) {
        if (first.closest(".form-context")) context.open = true;
        first.focus();
      }
    }
    return valid;
  }
  function freshId() {
    if (window.crypto.randomUUID) return window.crypto.randomUUID();
    var bytes = window.crypto.getRandomValues(new Uint8Array(16));
    bytes[6] = (bytes[6] & 15) | 64;
    bytes[8] = (bytes[8] & 63) | 128;
    var hex = Array.from(bytes, function (byte) { return byte.toString(16).padStart(2, "0"); }).join("");
    return hex.slice(0, 8) + "-" + hex.slice(8, 12) + "-" + hex.slice(12, 16) + "-" + hex.slice(16, 20) + "-" + hex.slice(20);
  }
  function canonicalData() {
    return {
      email: form.elements.email.value.trim(),
      message: message.value.trim(),
      name: form.elements.name.value.trim(),
      service: form.elements.service.value,
      budget: form.elements.budget.value.trim(),
      timeline: form.elements.timeline.value.trim(),
      website: form.elements.website.value.trim(),
      source: Object.assign({}, source, { cta: limited(activeCta, 40) })
    };
  }
  function resetChallenge() {
    challengeToken = "";
    if (widget !== null && window.turnstile) {
      try { window.turnstile.reset(widget); } catch (_) { /* The email fallback stays available. */ }
    }
  }
  function loadChallenge() {
    if (!sitekey) return Promise.reject(new Error("not_configured"));
    if (challengeLoader) return challengeLoader;
    challengeLoader = new Promise(function (resolve, reject) {
      var timeout;
      var script;
      var settled = false;
      function failed() {
        if (settled) return;
        settled = true;
        window.clearTimeout(timeout);
        if (script) script.remove();
        challengeLoader = null;
        verificationStatus.textContent = "Spam protection couldn’t load. Try sending again, or use the email address alongside this form.";
        reject(new Error("verification_unavailable"));
      }
      function render() {
        if (settled) return;
        window.clearTimeout(timeout);
        try {
          widget = window.turnstile.render(verification, {
            sitekey: sitekey,
            action: "contact",
            theme: root.dataset.theme || "auto",
            size: "flexible",
            callback: function (token) { challengeToken = token; verificationStatus.textContent = ""; },
            "expired-callback": function () { challengeToken = ""; },
            "error-callback": function () {
              challengeToken = "";
              verificationStatus.textContent = "Please retry the verification below. You can also email me directly.";
            },
            "timeout-callback": function () { challengeToken = ""; verificationStatus.textContent = "Verification timed out. Please try it again."; }
          });
          settled = true;
          resolve();
        } catch (_) { failed(); }
      }
      if (window.turnstile) { render(); return; }
      verificationStatus.textContent = "Loading spam protection…";
      window.ermolovTurnstileReady = render;
      script = document.createElement("script");
      script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?onload=ermolovTurnstileReady&render=explicit";
      script.async = true;
      script.defer = true;
      script.onerror = failed;
      timeout = window.setTimeout(failed, 15000);
      document.head.appendChild(script);
    }).catch(function (error) {
      challengeLoader = null;
      throw error;
    });
    return challengeLoader;
  }
  function preloadChallenge() { if (sitekey) loadChallenge().catch(function () {}); }
  form.addEventListener("focusin", preloadChallenge, { once: true });
  if ("IntersectionObserver" in window) {
    var challengeObserver = new IntersectionObserver(function (entries) {
      if (entries.some(function (entry) { return entry.isIntersecting; })) {
        preloadChallenge();
        challengeObserver.disconnect();
      }
    }, { rootMargin: "600px" });
    challengeObserver.observe(form);
    var sticky = document.querySelector(".mobile-contact");
    var stickyObserver = new IntersectionObserver(function (entries) {
      if (sticky) sticky.classList.toggle("is-hidden", entries[0].isIntersecting);
    }, { threshold: 0 });
    stickyObserver.observe(document.getElementById("contact"));
  }
  document.querySelectorAll("[data-cta]").forEach(function (link) {
    link.addEventListener("click", function () {
      activeCta = limited(link.dataset.cta, 40);
      if (link.dataset.service) {
        form.elements.service.value = link.dataset.service;
        context.open = true;
      }
      if (link.getAttribute("href") === "#contact") preloadChallenge();
    });
  });
  function updateCount() { messageCount.textContent = message.value.length.toLocaleString("en-US") + " / 2,500"; }
  form.addEventListener("input", function (event) {
    updateCount();
    if (event.target.getAttribute("aria-invalid")) {
      event.target.removeAttribute("aria-invalid");
      var error = document.getElementById(event.target.name + "-error");
      if (error) error.textContent = "";
    }
    if (!busy && lastSuccessfulContent !== null) submitLabel.textContent = "Send project inquiry";
  });
  updateCount();

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    if (busy || !validate()) return;
    if (!sitekey || !endpoint || endpoint !== "/api/leads") {
      showStatus("The form is temporarily unavailable. Please use the email address alongside it; your note is still here.", "error", true);
      return;
    }
    var data = canonicalData();
    var content = JSON.stringify(data);
    if (content === lastSuccessfulContent) {
      showStatus("Your inquiry has already been received. I’ll aim to reply within two business days.", "success", true);
      return;
    }
    busy = true;
    submit.disabled = true;
    submitLabel.textContent = "Preparing your inquiry…";
    form.setAttribute("aria-busy", "true");
    var timer;
    try {
      await loadChallenge();
      if (!challengeToken) {
        showStatus("Please complete the spam verification above, then send your inquiry. Your note is still here.", "error", true);
        return;
      }
      if (!attempts.has(content)) attempts.set(content, freshId());
      data.submissionId = attempts.get(content);
      data.turnstileToken = challengeToken;
      var controller = new AbortController();
      timer = window.setTimeout(function () { controller.abort(); }, 20000);
      submitLabel.textContent = "Sending your inquiry…";
      showStatus("Sending your inquiry…", "pending", false);
      var response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify(data),
        signal: controller.signal
      });
      var result;
      try { result = await response.json(); } catch (_) { throw new Error("invalid_response"); }
      if (response.ok && result.ok === true && typeof result.id === "string") {
        lastSuccessfulContent = content;
        showStatus("Thanks — your inquiry is received. I’ll aim to reply within two business days. You can keep this page open for a copy of your note.", "success", true);
        submitLabel.textContent = "Inquiry received ✓";
        resetChallenge();
        return;
      }
      var code = result.error && result.error.code;
      resetChallenge();
      if (code === "validation_error") {
        var fields = result.error.fields || {};
        Object.keys(fields).forEach(function (name) {
          showFieldError(name, name === "email" ? "Check your email address." : name === "message" ? "Please write between 1 and 2,500 characters." : "Please check this field.");
        });
        showStatus("Please check the highlighted fields and try again. Your note is still here.", "error", true);
      } else if (code === "challenge_required" || code === "challenge_failed") {
        showStatus("Please complete the refreshed spam verification, then try again. Your note is still here.", "error", true);
      } else if (code === "rate_limited" || response.status === 429) {
        showStatus("A few inquiries arrived at once. Please wait a minute and try again, or email me directly. Your note is still here.", "error", true);
      } else if (code === "submission_conflict") {
        showStatus("This inquiry couldn’t be confirmed safely. Please email me directly with your note; it’s still here.", "error", true);
      } else {
        showStatus("The form is temporarily unavailable. Try again shortly or email me directly. Your note is still here.", "error", true);
      }
    } catch (_) {
      resetChallenge();
      showStatus("I couldn’t confirm that your inquiry arrived. Check your connection and try again, or email me directly. Your note is still here.", "error", true);
    } finally {
      if (timer) window.clearTimeout(timer);
      busy = false;
      submit.disabled = false;
      form.removeAttribute("aria-busy");
      if (lastSuccessfulContent !== content) submitLabel.textContent = "Send project inquiry";
    }
  });
})();
