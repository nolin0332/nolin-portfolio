(function () {
  // JotForm conversational agent (chatbot widget)
  // Share URL: https://www.jotform.com/agent/019f01f41cb1710687a41b71d271cc48dd5d
  const AGENT_ID = "019f01f41cb1710687a41b71d271cc48dd5d";
  const AGENT_CHAT_BG = "#F4FEFF";
  const FOOTER_TEXT_COLOR = "#00433A";
  const CONTACT_LINE = "CTO: Molly Youngblood : +1 (904) 314-4057";
  const DEFAULT_RADIUS = "20px";
  const COVER_ID = "jf-jotform-branding-cover";
  // From widget bottom up to the red line (just below Chat/Voice labels).
  const BRANDING_STRIP_HEIGHT = 28;
  const COVER_DROP_CM = 10;
  const COVER_ANIMATION_MS = 550;

  if (document.querySelector('script[data-jotform-agent="1"]')) {
    return;
  }

  let refreshQueued = false;
  let lastCoverKey = "";
  let pollTimer = null;
  let chatWasOpen = false;
  let coverDropPx = null;

  const style = document.createElement("style");
  style.textContent =
    '[id^="JotformAgent-"],.jf-agent-root,.jf-agent-chat-button,.jf-agent-widget,' +
    'iframe[src*="jotform.com"],iframe[src*="agent.jotform.com"]{z-index:100000!important;}' +
    'iframe[data-jf-branding-clip="1"]{' +
    "clip-path:inset(0 0 " +
    BRANDING_STRIP_HEIGHT +
    "px 0)!important;" +
    "}" +
    '[id^="JotformAgent-"] a[href*="jotform"],' +
    '.jf-agent-root a[href*="jotform"]{' +
    "pointer-events:none!important;cursor:default!important;" +
    "}" +
    "#" +
    COVER_ID +
    "{" +
    "position:fixed;display:none;left:0;top:0;width:0;height:0;" +
    "z-index:2147483647;pointer-events:auto;cursor:default;" +
    "border-top-left-radius:0;border-top-right-radius:0;" +
    "overflow:hidden;box-sizing:border-box;" +
    "align-items:flex-end;justify-content:center;padding:0 10px 5px;" +
    "background:" +
    AGENT_CHAT_BG +
    ";" +
    "}" +
    "#" +
    COVER_ID +
    ".jf-cover-slide{" +
    "transition:top " +
    COVER_ANIMATION_MS +
    "ms cubic-bezier(0.22,1,0.36,1)," +
    "height " +
    COVER_ANIMATION_MS +
    "ms cubic-bezier(0.22,1,0.36,1);" +
    "will-change:top,height;" +
    "}" +
    "#" +
    COVER_ID +
    ".jf-cover-start .jf-branding-contact{" +
    "opacity:0;" +
    "}" +
    "#" +
    COVER_ID +
    ".jf-cover-slide:not(.jf-cover-start) .jf-branding-contact{" +
    "opacity:1;" +
    "transition:opacity 180ms ease " +
    Math.round(COVER_ANIMATION_MS * 0.55) +
    "ms;" +
    "}" +
    "#" +
    COVER_ID +
    " .jf-branding-contact{" +
    "font:500 13px/1.3 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;" +
    "color:" +
    FOOTER_TEXT_COLOR +
    ";" +
    "letter-spacing:0.01em;text-align:center;white-space:nowrap;" +
    "overflow:hidden;text-overflow:ellipsis;max-width:100%;" +
    "}";
  document.head.appendChild(style);

  function walkAll(root, visit) {
    if (!root) {
      return;
    }
    visit(root);
    if (!root.querySelectorAll) {
      return;
    }
    root.querySelectorAll("*").forEach(function (el) {
      visit(el);
      if (el.shadowRoot) {
        walkAll(el.shadowRoot, visit);
      }
    });
  }

  function getCoverDropPx() {
    if (coverDropPx !== null) {
      return coverDropPx;
    }

    var probe = document.createElement("div");
    probe.style.height = COVER_DROP_CM + "cm";
    probe.style.position = "absolute";
    probe.style.visibility = "hidden";
    probe.style.pointerEvents = "none";
    document.body.appendChild(probe);
    coverDropPx = probe.getBoundingClientRect().height;
    document.body.removeChild(probe);
    return coverDropPx;
  }

  function pickRadius(node) {
    var computed = window.getComputedStyle(node);
    var bl = computed.borderBottomLeftRadius;
    var br = computed.borderBottomRightRadius;
    var all = computed.borderRadius;

    if (!bl || bl === "0px") {
      bl = all || DEFAULT_RADIUS;
    }
    if (!br || br === "0px") {
      br = all || DEFAULT_RADIUS;
    }

    return {
      bl: ensureMinRadius(bl),
      br: ensureMinRadius(br),
    };
  }

  function ensureMinRadius(value) {
    var amount = parseFloat(value);
    if (isNaN(amount) || amount < 12) {
      return DEFAULT_RADIUS;
    }
    return value;
  }

  function getCoverEl() {
    var cover = document.getElementById(COVER_ID);
    if (!cover) {
      cover = document.createElement("div");
      cover.id = COVER_ID;
      var label = document.createElement("span");
      label.className = "jf-branding-contact";
      label.textContent = CONTACT_LINE;
      cover.appendChild(label);
      cover.addEventListener(
        "click",
        function (event) {
          event.preventDefault();
          event.stopPropagation();
        },
        true,
      );
      document.body.appendChild(cover);
    }
    return cover;
  }

  function findChatIframe() {
    var best = null;
    var bestArea = 0;

    document.querySelectorAll('iframe[src*="jotform"]').forEach(function (iframe) {
      var rect = iframe.getBoundingClientRect();
      if (rect.width < 120 || rect.height < 80) {
        return;
      }
      var area = rect.width * rect.height;
      if (area > bestArea) {
        bestArea = area;
        best = iframe;
      }
    });

    return best;
  }

  function findWidgetShell(iframe) {
    var shell = null;
    var node = iframe;

    while (node && node !== document.body) {
      var rect = node.getBoundingClientRect();
      if (rect.width >= 240 && rect.height >= 280) {
        shell = node;
      }
      node = node.parentElement;
    }

    return shell;
  }

  function isBrandingElement(el) {
    if (!el || el.id === COVER_ID || el.tagName === "IFRAME") {
      return false;
    }
    if (el.dataset.jfBrandingHidden === "1") {
      return false;
    }

    var text = (el.textContent || "").replace(/\s+/g, " ").trim();
    var isBrandingText =
      /powered by jotform/i.test(text) && text.length <= 90 && el.children.length <= 6;
    var isBrandingLink =
      el.tagName === "A" &&
      /jotform/i.test(el.getAttribute("href") || "") &&
      /ai|agent|powered|brand/i.test(
        ((el.textContent || "") + " " + (el.getAttribute("href") || "")).toLowerCase(),
      );

    return isBrandingText || isBrandingLink;
  }

  function disableBrandingLinks(root) {
    if (!root) {
      return;
    }

    walkAll(root, function (el) {
      if (!isBrandingElement(el)) {
        return;
      }

      var rect = el.getBoundingClientRect();
      if (rect.width < 20 || rect.height < 8) {
        return;
      }

      el.dataset.jfBrandingHidden = "1";
      el.style.setProperty("pointer-events", "none", "important");
      el.style.setProperty("cursor", "default", "important");
      el.style.setProperty("visibility", "hidden", "important");
      el.style.setProperty("opacity", "0", "important");
      el.style.setProperty("height", "0", "important");
      el.style.setProperty("overflow", "hidden", "important");
      el.style.setProperty("margin", "0", "important");
      el.style.setProperty("padding", "0", "important");

      if (el.tagName === "A") {
        el.setAttribute("tabindex", "-1");
      }
    });
  }

  function applyIframeBrandingClip(iframe, isOpen) {
    if (!iframe) {
      return;
    }

    if (isOpen) {
      if (iframe.dataset.jfBrandingClip === "1") {
        return;
      }
      iframe.dataset.jfBrandingClip = "1";
      iframe.style.setProperty(
        "clip-path",
        "inset(0 0 " + BRANDING_STRIP_HEIGHT + "px 0)",
        "important",
      );
      return;
    }

    if (iframe.dataset.jfBrandingClip !== "1") {
      return;
    }
    delete iframe.dataset.jfBrandingClip;
    iframe.style.removeProperty("clip-path");
  }

  function isWidgetExpanded(iframe, shellRect) {
    if (!iframe || !shellRect) {
      return false;
    }

    var iframeRect = iframe.getBoundingClientRect();
    return iframeRect.width >= 140 && iframeRect.height >= 100 && shellRect.height >= 140;
  }

  function isChatFullyOpen(iframe, shellRect) {
    if (!iframe || !shellRect) {
      return false;
    }

    var iframeRect = iframe.getBoundingClientRect();
    return iframeRect.width >= 160 && iframeRect.height >= 200 && shellRect.height >= 280;
  }

  function coverKey(rect, radiusBL, radiusBR, visible) {
    return (
      (visible ? "1" : "0") +
      ":" +
      Math.round(rect.left) +
      ":" +
      Math.round(rect.top) +
      ":" +
      Math.round(rect.width) +
      ":" +
      Math.round(rect.height) +
      ":" +
      radiusBL +
      ":" +
      radiusBR
    );
  }

  function applyCoverGeometry(cover, rect, radiusBL, radiusBR) {
    cover.style.left = Math.round(rect.left) + "px";
    cover.style.top = Math.round(rect.top) + "px";
    cover.style.width = Math.round(rect.width) + "px";
    cover.style.height = Math.round(rect.height) + "px";
    cover.style.borderBottomLeftRadius = radiusBL || DEFAULT_RADIUS;
    cover.style.borderBottomRightRadius = radiusBR || DEFAULT_RADIUS;
    cover.style.borderTopLeftRadius = "0";
    cover.style.borderTopRightRadius = "0";
    cover.style.boxShadow = "none";
  }

  function buildCoverRect(shellRect, phase) {
    var finalTop = shellRect.bottom - BRANDING_STRIP_HEIGHT;

    if (phase === "start") {
      var drop = getCoverDropPx();
      var startTop = finalTop - drop;
      return {
        left: shellRect.left,
        top: startTop,
        width: shellRect.width,
        height: shellRect.bottom - startTop,
      };
    }

    return {
      left: shellRect.left,
      top: finalTop,
      width: shellRect.width,
      height: BRANDING_STRIP_HEIGHT,
    };
  }

  function playCoverSlideIn(cover, shellRect, radiusBL, radiusBR) {
    cover.classList.remove("jf-cover-start");
    cover.classList.add("jf-cover-slide");
    applyCoverGeometry(cover, buildCoverRect(shellRect, "start"), radiusBL, radiusBR);
    cover.classList.add("jf-cover-start");

    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        applyCoverGeometry(cover, buildCoverRect(shellRect, "end"), radiusBL, radiusBR);
        cover.classList.remove("jf-cover-start");
      });
    });
  }

  function showCover(shellRect, radiusBL, radiusBR, animate) {
    var finalRect = buildCoverRect(shellRect, "end");
    var key = coverKey(finalRect, radiusBL, radiusBR, true);
    if (key === lastCoverKey && !animate) {
      return;
    }
    lastCoverKey = key;

    var cover = getCoverEl();
    cover.style.display = "flex";

    if (animate) {
      playCoverSlideIn(cover, shellRect, radiusBL, radiusBR);
      return;
    }

    cover.classList.remove("jf-cover-slide", "jf-cover-start");
    applyCoverGeometry(cover, finalRect, radiusBL, radiusBR);
  }

  function hideCover() {
    if (lastCoverKey === "hidden") {
      return;
    }
    lastCoverKey = "hidden";

    var cover = document.getElementById(COVER_ID);
    if (cover) {
      cover.classList.remove("jf-cover-slide", "jf-cover-start");
      cover.style.display = "none";
    }
  }

  function applyBrandingCover() {
    var iframe = findChatIframe();
    var shell = iframe ? findWidgetShell(iframe) : null;

    if (!iframe || !shell) {
      hideCover();
      applyIframeBrandingClip(iframe, false);
      return;
    }

    disableBrandingLinks(shell);

    var shellRect = shell.getBoundingClientRect();
    var expanded = isWidgetExpanded(iframe, shellRect);
    var fullyOpen = isChatFullyOpen(iframe, shellRect);
    applyIframeBrandingClip(iframe, expanded);

    if (!expanded) {
      chatWasOpen = false;
      hideCover();
      return;
    }

    var radius = pickRadius(shell);
    var shouldAnimate = fullyOpen && !chatWasOpen;
    if (fullyOpen) {
      chatWasOpen = true;
    }

    showCover(shellRect, radius.bl, radius.br, shouldAnimate);
  }

  function scheduleRefresh() {
    if (refreshQueued) {
      return;
    }
    refreshQueued = true;
    requestAnimationFrame(function () {
      refreshQueued = false;
      applyBrandingCover();
    });
  }

  function startShortPolling() {
    if (pollTimer) {
      return;
    }

    var attempts = 0;
    pollTimer = window.setInterval(function () {
      scheduleRefresh();
      attempts += 1;
      if (attempts >= 12) {
        window.clearInterval(pollTimer);
        pollTimer = null;
      }
    }, 1000);
  }

  scheduleRefresh();

  new MutationObserver(function (mutations) {
    for (var i = 0; i < mutations.length; i += 1) {
      var target = mutations[i].target;
      if (target && target.id === COVER_ID) {
        continue;
      }
      if (target && target.closest && target.closest("#" + COVER_ID)) {
        continue;
      }
      scheduleRefresh();
      return;
    }
  }).observe(document.documentElement, {
    childList: true,
    subtree: true,
  });

  window.addEventListener("resize", scheduleRefresh, { passive: true });
  window.addEventListener("scroll", scheduleRefresh, { passive: true, capture: true });

  const script = document.createElement("script");
  script.src =
    "https://cdn.jotfor.ms/agent/embedjs/" +
    AGENT_ID +
    "/embed.js?skipWelcome=1&maximizable=1";
  script.defer = true;
  script.dataset.jotformAgent = "1";
  script.addEventListener("load", function () {
    [300, 800, 1500, 2500].forEach(function (delay) {
      window.setTimeout(scheduleRefresh, delay);
    });
    startShortPolling();
  });
  document.body.appendChild(script);
})();
