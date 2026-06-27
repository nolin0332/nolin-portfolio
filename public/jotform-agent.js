(function () {
  // JotForm conversational agent (chatbot widget)
  // Share URL: https://www.jotform.com/agent/019f01f41cb1710687a41b71d271cc48dd5d
  const AGENT_ID = "019f01f41cb1710687a41b71d271cc48dd5d";
  // From this agent's Jotform embed theme (chat panel background).
  const AGENT_CHAT_BG = "#F4FEFF";
  const FOOTER_TEXT_COLOR = "#00433A";
  const CONTACT_LINE = "CTO: Molly Youngblood : +1 (904) 314-4057";
  const DEFAULT_RADIUS = "20px";
  const COVER_ID = "jf-jotform-branding-cover";
  const MIN_COVER_HEIGHT = 48;
  const COVER_OVERLAP_UP = 14;

  if (document.querySelector('script[data-jotform-agent="1"]')) {
    return;
  }

  const style = document.createElement("style");
  style.textContent =
    '[id^="JotformAgent-"],.jf-agent-root,.jf-agent-chat-button,.jf-agent-widget,' +
    'iframe[src*="jotform.com"],iframe[src*="agent.jotform.com"]{z-index:100000!important;}' +
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
    "align-items:flex-end;justify-content:center;padding:0 10px 7px;" +
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

  function isVisibleColor(value) {
    return (
      value &&
      value !== "transparent" &&
      value !== "rgba(0, 0, 0, 0)" &&
      value !== "initial"
    );
  }

  function parseRgb(value) {
    var match = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
    if (!match) {
      return null;
    }
    return {
      r: Number(match[1]),
      g: Number(match[2]),
      b: Number(match[3]),
    };
  }

  function isNearWhite(rgb) {
    return rgb.r >= 250 && rgb.g >= 250 && rgb.b >= 250;
  }

  function pickFooterBackground(shell, widgetRect) {
    var footerBandTop = widgetRect.bottom - 96;
    var bestColor = null;
    var bestArea = 0;

    walkAll(shell, function (el) {
      if (el.id === COVER_ID || el.tagName === "IFRAME") {
        return;
      }

      var rect = el.getBoundingClientRect();
      if (rect.width < 40 || rect.height < 8) {
        return;
      }
      if (rect.bottom < widgetRect.bottom - 2 || rect.top < footerBandTop) {
        return;
      }

      var bg = window.getComputedStyle(el).backgroundColor;
      if (!isVisibleColor(bg)) {
        return;
      }

      var rgb = parseRgb(bg);
      if (rgb && isNearWhite(rgb)) {
        return;
      }

      var area = rect.width * rect.height;
      if (area >= bestArea) {
        bestArea = area;
        bestColor = bg;
      }
    });

    return bestColor || AGENT_CHAT_BG;
  }

  function pickRadius(node) {
    var style = window.getComputedStyle(node);
    var bl = style.borderBottomLeftRadius;
    var br = style.borderBottomRightRadius;
    var all = style.borderRadius;

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
      cover.addEventListener(
        "mousedown",
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
      if (rect.width < 160 || rect.height < 200) {
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

  function getWidgetTheme(iframe) {
    var shell = findWidgetShell(iframe);
    if (!shell) {
      return null;
    }

    var rect = shell.getBoundingClientRect();
    var radius = pickRadius(shell);
    return {
      rect: rect,
      background: pickFooterBackground(shell, rect),
      radiusBL: radius.bl,
      radiusBR: radius.br,
    };
  }

  function disableBrandingLinks() {
    walkAll(document.body, function (el) {
      if (el.id === COVER_ID || el.tagName === "IFRAME") {
        return;
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

      if (!isBrandingText && !isBrandingLink) {
        return;
      }

      var rect = el.getBoundingClientRect();
      if (rect.width < 20 || rect.height < 8) {
        return;
      }

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
        el.removeAttribute("href");
      }
    });
  }

  function showCover(rect, theme) {
    var cover = getCoverEl();
    theme = theme || {};

    cover.style.display = "flex";
    cover.style.left = Math.round(rect.left) + "px";
    cover.style.top = Math.round(rect.top) + "px";
    cover.style.width = Math.round(rect.width) + "px";
    cover.style.height = Math.round(rect.height) + "px";
    cover.style.background = theme.background || AGENT_CHAT_BG;
    cover.style.borderBottomLeftRadius = theme.radiusBL || DEFAULT_RADIUS;
    cover.style.borderBottomRightRadius = theme.radiusBR || DEFAULT_RADIUS;
    cover.style.borderTopLeftRadius = "0";
    cover.style.borderTopRightRadius = "0";
    cover.style.boxShadow =
      "0 -1px 0 0 " + (theme.background || AGENT_CHAT_BG);
    cover.style.pointerEvents = "auto";
    cover.style.cursor = "default";
  }

  function hideCover() {
    var cover = document.getElementById(COVER_ID);
    if (cover) {
      cover.style.display = "none";
    }
  }

  function buildCoverRect(theme) {
    var height = MIN_COVER_HEIGHT + COVER_OVERLAP_UP;
    return {
      left: theme.rect.left,
      top: theme.rect.bottom - height,
      width: theme.rect.width,
      height: height,
    };
  }

  function applyBrandingCover() {
    var iframe = findChatIframe();
    var theme = iframe ? getWidgetTheme(iframe) : null;
    disableBrandingLinks();

    if (!iframe || !theme) {
      hideCover();
      return;
    }

    showCover(buildCoverRect(theme), theme);
  }

  function refreshBrandingHide() {
    applyBrandingCover();
  }

  refreshBrandingHide();
  new MutationObserver(refreshBrandingHide).observe(document.documentElement, {
    childList: true,
    subtree: true,
    attributes: true,
  });
  window.addEventListener("resize", refreshBrandingHide);
  window.addEventListener("scroll", refreshBrandingHide, true);

  const script = document.createElement("script");
  script.src =
    "https://cdn.jotfor.ms/agent/embedjs/" +
    AGENT_ID +
    "/embed.js?skipWelcome=1&maximizable=1";
  script.defer = true;
  script.dataset.jotformAgent = "1";
  script.addEventListener("load", function () {
    [300, 800, 1500, 2500, 4000].forEach(function (delay) {
      window.setTimeout(refreshBrandingHide, delay);
    });
    window.setInterval(refreshBrandingHide, 750);
  });
  document.body.appendChild(script);
})();
