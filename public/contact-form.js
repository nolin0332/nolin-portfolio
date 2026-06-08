(function () {

  const form = document.getElementById("contact-form");

  if (!form) return;



  const statusEl = document.getElementById("contact-form-status");

  const submitBtn = document.getElementById("contact-submit");

  const defaultBtnLabel = submitBtn ? submitBtn.textContent.trim() : "Send message";

  const recipient = form.dataset.recipient || "michael.trent.dev@gmail.com";

  const web3Key = (form.dataset.web3Key || "").trim();

  const formsubmitId = (form.dataset.formsubmitId || "").trim();



  function isSuccess(data) {

    if (!data || typeof data !== "object") return false;

    const flag = data.success;

    return flag === true || flag === "true";

  }



  function setStatus(message, type) {

    if (!statusEl) return;

    statusEl.textContent = message;

    statusEl.classList.remove("is-success", "is-error", "is-sending", "is-visible");

    statusEl.removeAttribute("role");

    if (!message) return;



    statusEl.classList.add("is-visible");

    if (type === "success") {

      statusEl.classList.add("is-success");

      statusEl.setAttribute("role", "status");

    } else if (type === "error") {

      statusEl.classList.add("is-error");

      statusEl.setAttribute("role", "alert");

    } else if (type === "sending") {

      statusEl.classList.add("is-sending");

      statusEl.setAttribute("role", "status");

    }



    statusEl.scrollIntoView({ block: "nearest", behavior: "smooth" });

  }



  function setButtonLabel(label) {

    if (submitBtn) submitBtn.textContent = label;

  }



  function normalizeError(message) {

    const text = String(message || "").trim();

    if (!text) return "Unable to send message. Please try again.";

    if (/activation/i.test(text)) {

      return `Form not activated yet. Check ${recipient} for the FormSubmit activation email, click the link, then try again.`;

    }

    return text;

  }



  async function postJson(url, body) {

    const response = await fetch(url, {

      method: "POST",

      headers: { "Content-Type": "application/json", Accept: "application/json" },

      body: JSON.stringify(body),

    });

    const data = await response.json().catch(() => ({}));

    return { response, data };

  }



  async function sendViaWeb3Forms(name, email, message) {

    const { response, data } = await postJson("https://api.web3forms.com/submit", {

      access_key: web3Key,

      name,

      email,

      message,

      subject: `Portfolio message from ${name}`,

      from_name: name,

      replyto: email,

      botcheck: false,

    });

    if (response.ok && isSuccess(data)) return;

    throw new Error(data.message || "Web3Forms delivery failed.");

  }



  async function sendViaFormSubmit(name, email, message) {

    const endpointId = formsubmitId || recipient;

    const { response, data } = await postJson(

      `https://formsubmit.co/ajax/${encodeURIComponent(endpointId)}`,

      {

        name,

        email,

        message,

        _subject: `Portfolio message from ${name}`,

        _captcha: "false",

        _template: "table",

        _replyto: email,

      }

    );



    if (response.ok && isSuccess(data)) return;



    const serverMessage = data.message || data.error || "";

    if (/server error/i.test(serverMessage)) {

      throw new Error(

        `Email service error. If this is your first submission, check ${recipient} for a FormSubmit activation email and click the link.`

      );

    }



    throw new Error(normalizeError(serverMessage));

  }



  async function sendMessage(name, email, message) {

    if (web3Key) {

      await sendViaWeb3Forms(name, email, message);

      return;

    }

    await sendViaFormSubmit(name, email, message);

  }



  function stopScrollBubble(event) {

    event.stopPropagation();

  }



  ["wheel", "touchmove", "mousedown", "click", "focusin"].forEach((name) => {

    form.addEventListener(name, stopScrollBubble, { passive: true });

  });



  form.addEventListener("submit", async function (event) {

    event.preventDefault();



    const formData = new FormData(form);

    const name = String(formData.get("name") || "").trim();

    const fromEmail = String(formData.get("email") || "").trim();

    const message = String(formData.get("message") || "").trim();



    if (!name || !fromEmail || !message) {

      setStatus("Please fill in your name, email, and message.", "error");

      return;

    }



    if (submitBtn) submitBtn.disabled = true;

    setButtonLabel("Sending…");

    setStatus("Sending your message…", "sending");



    try {

      await sendMessage(name, fromEmail, message);

      form.reset();

      setButtonLabel("Message sent");

      setStatus("Success — your message was sent. I'll get back to you soon.", "success");

    } catch (error) {

      setButtonLabel("Send failed");

      setStatus(

        error instanceof Error

          ? `Failed — ${error.message}`

          : "Failed — something went wrong. Please try again.",

        "error"

      );

    } finally {

      if (submitBtn) {

        submitBtn.disabled = false;

        window.setTimeout(() => setButtonLabel(defaultBtnLabel), 2800);

      }

    }

  });

  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => {
      window.dispatchEvent(new Event("resize"));
    });
  });

})();

