document.addEventListener("DOMContentLoaded", function () {

  const icon = document.getElementById("chatbot-icon");
  const box = document.getElementById("chatbot-box");
  const closeBtn = document.getElementById("chat-close-btn");
  const sendBtn = document.getElementById("send-btn");
  const input = document.getElementById("chat-input");
  const messages = document.getElementById("chat-messages");

  if (!icon || !box) return;

  let opened = false;

  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : null;
  }

  function addTextMessage(text, role) {
    const wrapper = document.createElement("div");
    wrapper.className = `chat-msg chat-${role}`;
    wrapper.textContent = text;
    messages.appendChild(wrapper);
    messages.scrollTop = messages.scrollHeight;
    return wrapper;
  }

  function renderAIResponse(text) {
    const wrapper = document.createElement("div");
    wrapper.className = "chat-msg chat-ai";

    let currentSection = null;
    let hasSection = false;

    text.split("\n").forEach(line => {

        if (line.startsWith("SECTION:")) {
        hasSection = true;
        currentSection = document.createElement("div");
        currentSection.className = "chat-section";

        const title = document.createElement("div");
        title.className = "chat-section-title";
        title.innerText = line.replace("SECTION:", "").trim();

        currentSection.appendChild(title);
        wrapper.appendChild(currentSection);
        }
        else if (line.startsWith("-") && currentSection) {
        const item = document.createElement("div");
        item.className = "chat-section-item";
        item.innerText = line.replace("-", "").trim();
        currentSection.appendChild(item);
        }
    });

    // 🔐 SAFETY FALLBACK (VERY IMPORTANT)
    if (!hasSection) {
        wrapper.innerText = text;
    }

    return wrapper;
    }

  function openChat() {
    box.classList.remove("d-none");

    if (window.KidsSound) window.KidsSound.play("click");

    if (!opened) {
      opened = true;
      addTextMessage("Hi! I'm your AI Mentor. Ask me about a career path, or anything about Craftlanee.", "ai");
    }
    input.focus();
  }

  icon.onclick = () => {
    if (box.classList.contains("d-none")) {
      openChat();
    } else {
      box.classList.add("d-none");
    }
  };

  if (closeBtn) {
    closeBtn.onclick = () => box.classList.add("d-none");
  }

  function sendMessage() {
    const text = input.value.trim();
    if (!text || sendBtn.disabled) return;

    addTextMessage(text, "user");
    input.value = "";
    sendBtn.disabled = true;

    if (window.KidsSound) window.KidsSound.play("click");

    const typing = document.createElement("div");
    typing.className = "chat-msg chat-ai chat-typing";
    typing.innerHTML = "<span></span><span></span><span></span>";
    messages.appendChild(typing);
    messages.scrollTop = messages.scrollHeight;

    fetch("/mentor-ai/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      credentials: "same-origin",
      body: JSON.stringify({ message: text })
    })
    .then(res => {
      if (!res.ok) throw new Error("Request failed");
      return res.json();
    })
    .then(data => {
      typing.remove();
      messages.appendChild(renderAIResponse(data.reply));
      messages.scrollTop = messages.scrollHeight;
    })
    .catch(() => {
      typing.remove();
      addTextMessage("Something went wrong. Please try again.", "ai");
    })
    .finally(() => {
      sendBtn.disabled = false;
      input.focus();
    });
  }

  sendBtn.onclick = sendMessage;

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  });
});
