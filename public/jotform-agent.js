(function () {
  // JotForm conversational agent (chatbot widget)
  // Share URL: https://www.jotform.com/agent/019f01f41cb1710687a41b71d271cc48dd5d
  const AGENT_ID = "019f01f41cb1710687a41b71d271cc48dd5d";

  if (document.querySelector('script[data-jotform-agent="1"]')) {
    return;
  }

  const style = document.createElement("style");
  style.textContent =
    '[id^="JotformAgent-"],.jf-agent-root,.jf-agent-chat-button,.jf-agent-widget,' +
    'iframe[src*="jotform.com"],iframe[src*="agent.jotform.com"]{z-index:100000!important;}';
  document.head.appendChild(style);

  const script = document.createElement("script");
  script.src =
    "https://cdn.jotfor.ms/agent/embedjs/" +
    AGENT_ID +
    "/embed.js?skipWelcome=1&maximizable=1";
  script.defer = true;
  script.dataset.jotformAgent = "1";
  document.body.appendChild(script);
})();
