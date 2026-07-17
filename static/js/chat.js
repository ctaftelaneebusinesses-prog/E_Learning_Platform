(function () {
  const root = document.querySelector('.chat-app');
  if (!root) return;

  const messagesEl = root.querySelector('.chat-messages');
  const form = root.querySelector('#chatForm');
  const textarea = root.querySelector('#messageInput');
  const fileInput = root.querySelector('#fileInput');
  const attachBtn = root.querySelector('#attachBtn');
  const micBtn = root.querySelector('#micBtn');
  const attachPreview = root.querySelector('#attachPreview');
  const onlineDot = root.querySelector('.online-dot');
  const onlineSubtitle = root.querySelector('.chat-subtitle');

  const pollUrl = root.dataset.pollUrl;
  const reactUrlTemplate = root.dataset.reactUrlTemplate;
  const reactionEmojis = JSON.parse(root.dataset.reactionEmojis || '[]');
  const csrftoken = form.querySelector('[name=csrfmiddlewaretoken]').value;

  const renderedIds = new Set();
  let lastId = 0;
  let pendingFile = null;
  let mediaRecorder = null;
  let recordedChunks = [];
  let recordingStart = null;
  let recordingTimer = null;
  let indicatorEl = null;

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
  }

  const TICK_ICONS = {
    sent: '<svg viewBox="0 0 16 15" fill="none"><path d="M15 3L5.5 12.5L1 8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    delivered: '<svg viewBox="0 0 20 15" fill="none"><path d="M14 3L6 11L2.5 7.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/><path d="M19 3L11 11" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    read: '<svg viewBox="0 0 20 15" fill="none"><path d="M14 3L6 11L2.5 7.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/><path d="M19 3L11 11" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  };

  function reactionPickerHtml(msgId) {
    return reactionEmojis.map((e) => `<button type="button" data-emoji="${e}" data-msg-id="${msgId}">${e}</button>`).join('');
  }

  function reactionsHtml(reactions) {
    if (!reactions || !reactions.length) return '';
    return reactions.map((r) => `<span class="reaction-chip">${r.emoji} ${r.count > 1 ? r.count : ''}</span>`).join('');
  }

  function bubbleHtml(msg) {
    const rowClass = msg.is_me ? 'is-me' : 'is-other';
    let inner = '';
    if (msg.message) inner += `<div class="msg-text">${escapeHtml(msg.message)}</div>`;
    if (msg.attachment_url) {
      if (msg.is_image) {
        inner += `<a href="${msg.attachment_url}" target="_blank" rel="noopener"><img class="msg-attachment-image" src="${msg.attachment_url}" alt="attachment"></a>`;
      } else {
        inner += `<a class="msg-attachment-file" href="${msg.attachment_url}" target="_blank" rel="noopener"><i class="bi bi-paperclip"></i> ${escapeHtml(msg.attachment_name || 'File')}</a>`;
      }
    }
    if (msg.voice_note_url) {
      inner += `<div class="msg-voice-note"><audio controls src="${msg.voice_note_url}"></audio></div>`;
    }

    const tickHtml = msg.is_me
      ? `<span class="tick tick-${msg.tick_state || 'sent'}" data-tick-for="${msg.id}">${TICK_ICONS[msg.tick_state || 'sent']}</span>`
      : '';

    return `
      <div class="msg-row ${rowClass}" data-msg-id="${msg.id}">
        <div class="msg-group">
          <div class="msg-bubble">${inner}</div>
          <div class="msg-reactions" data-reactions-for="${msg.id}">${reactionsHtml(msg.reactions)}</div>
          <div class="msg-meta">
            <span class="msg-time">${msg.time_display}</span>
            ${tickHtml}
          </div>
          <div class="reaction-picker">${reactionPickerHtml(msg.id)}</div>
        </div>
      </div>`.trim();
  }

  function appendMessage(msg, scroll) {
    if (!msg || renderedIds.has(msg.id)) return;
    renderedIds.add(msg.id);
    lastId = Math.max(lastId, msg.id);
    const wrapper = document.createElement('div');
    wrapper.innerHTML = bubbleHtml(msg);
    messagesEl.appendChild(wrapper.firstChild);
    if (scroll !== false) messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function updateTick(id, tickState) {
    const el = messagesEl.querySelector(`[data-tick-for="${id}"]`);
    if (!el) return;
    el.className = `tick tick-${tickState}`;
    el.innerHTML = TICK_ICONS[tickState];
  }

  function setOnline(isOnline) {
    if (onlineDot) onlineDot.classList.toggle('is-online', isOnline);
    if (onlineSubtitle) {
      onlineSubtitle.textContent = isOnline ? 'Online' : 'Offline';
      onlineSubtitle.classList.toggle('is-online', isOnline);
    }
  }

  messagesEl.querySelectorAll('[data-msg-id]').forEach((el) => {
    const id = parseInt(el.dataset.msgId, 10);
    renderedIds.add(id);
    lastId = Math.max(lastId, id);
  });
  messagesEl.scrollTop = messagesEl.scrollHeight;

  async function poll() {
    try {
      const res = await fetch(`${pollUrl}?since=${lastId}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
      if (!res.ok) return;
      const data = await res.json();
      data.messages.forEach((m) => appendMessage(m, true));
      (data.pending_ticks || []).forEach((t) => updateTick(t.id, t.tick_state));
      setOnline(data.other_online);
    } catch (e) {
      /* network hiccup — will retry on next tick */
    }
  }

  poll();
  setInterval(poll, 4000);

  const themeBtn = root.querySelector('#themeBtn');
  const themePicker = root.querySelector('#themePicker');
  if (themeBtn && themePicker) {
    const themeStorageKey = `chatTheme:${pollUrl}`;
    const swatches = themePicker.querySelectorAll('.theme-swatch');

    function applyTheme(theme) {
      if (theme && theme !== 'default') {
        root.dataset.theme = theme;
      } else {
        delete root.dataset.theme;
      }
      swatches.forEach((s) => s.classList.toggle('is-active', (s.dataset.theme || 'default') === (theme || 'default')));
    }

    applyTheme(localStorage.getItem(themeStorageKey) || 'default');

    themeBtn.addEventListener('click', () => {
      themePicker.hidden = !themePicker.hidden;
    });

    themePicker.addEventListener('click', (e) => {
      const btn = e.target.closest('.theme-swatch');
      if (!btn) return;
      const theme = btn.dataset.theme || 'default';
      applyTheme(theme);
      localStorage.setItem(themeStorageKey, theme);
      themePicker.hidden = true;
    });

    document.addEventListener('click', (e) => {
      if (!themePicker.hidden && !themePicker.contains(e.target) && e.target !== themeBtn && !themeBtn.contains(e.target)) {
        themePicker.hidden = true;
      }
    });
  }

  function clearAttachment() {
    pendingFile = null;
    fileInput.value = '';
    attachPreview.hidden = true;
    attachPreview.innerHTML = '';
  }

  function showAttachmentPreview(file) {
    attachPreview.hidden = false;
    if (file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      attachPreview.innerHTML = `<img src="${url}" alt=""><span>${escapeHtml(file.name)}</span><button type="button" class="remove-attach">&times;</button>`;
    } else {
      attachPreview.innerHTML = `<i class="bi bi-file-earmark"></i><span>${escapeHtml(file.name)}</span><button type="button" class="remove-attach">&times;</button>`;
    }
    attachPreview.querySelector('.remove-attach').addEventListener('click', clearAttachment);
  }

  attachBtn.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) {
      pendingFile = fileInput.files[0];
      showAttachmentPreview(pendingFile);
    }
  });

  textarea.addEventListener('paste', (e) => {
    const items = e.clipboardData && e.clipboardData.items;
    if (!items) return;
    for (const item of items) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (file) {
          pendingFile = file;
          showAttachmentPreview(file);
        }
        e.preventDefault();
        break;
      }
    }
  });

  textarea.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
  });

  async function sendPayload(formData) {
    const res = await fetch(window.location.pathname, {
      method: 'POST',
      body: formData,
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.message || null;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = textarea.value.trim();
    if (!text && !pendingFile) return;

    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', csrftoken);
    formData.append('message', text);
    if (pendingFile) formData.append('attachment', pendingFile);

    textarea.value = '';
    textarea.style.height = 'auto';
    clearAttachment();

    const msg = await sendPayload(formData);
    appendMessage(msg, true);
  });

  function formatTimer(ms) {
    const s = Math.floor(ms / 1000);
    return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  }

  async function startRecording() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert('Voice recording is not supported in this browser.');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      recordedChunks = [];
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) recordedChunks.push(e.data); };
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        clearInterval(recordingTimer);
        if (indicatorEl) indicatorEl.remove();
        micBtn.classList.remove('recording');
        micBtn.innerHTML = '<i class="bi bi-mic"></i>';

        const blob = new Blob(recordedChunks, { type: 'audio/webm' });
        if (blob.size === 0) return;
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', csrftoken);
        formData.append('message', '');
        formData.append('voice_note', blob, 'voice-note.webm');
        const msg = await sendPayload(formData);
        appendMessage(msg, true);
      };
      mediaRecorder.start();
      recordingStart = Date.now();
      micBtn.classList.add('recording');
      micBtn.innerHTML = '<i class="bi bi-stop-fill"></i>';

      indicatorEl = document.createElement('div');
      indicatorEl.className = 'recording-indicator';
      indicatorEl.innerHTML = '<span class="rec-dot"></span><span class="rec-timer">0:00</span> Recording…';
      form.parentElement.insertBefore(indicatorEl, form);
      recordingTimer = setInterval(() => {
        indicatorEl.querySelector('.rec-timer').textContent = formatTimer(Date.now() - recordingStart);
      }, 500);
    } catch (err) {
      alert('Microphone permission was denied.');
    }
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
  }

  micBtn.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      stopRecording();
    } else {
      startRecording();
    }
  });

  const picLightbox = document.querySelector('#picLightbox');
  if (picLightbox) {
    const picLightboxImg = document.querySelector('#picLightboxImg');
    const picLightboxName = document.querySelector('#picLightboxName');
    const picLightboxClose = document.querySelector('#picLightboxClose');
    const picLightboxBackdrop = document.querySelector('#picLightboxBackdrop');

    function openPicLightbox(url, name) {
      picLightboxImg.src = url;
      picLightboxName.textContent = name || '';
      picLightbox.hidden = false;
    }

    function closePicLightbox() {
      picLightbox.hidden = true;
      picLightboxImg.src = '';
    }

    document.querySelectorAll('[data-view-pic]').forEach((el) => {
      el.addEventListener('click', () => openPicLightbox(el.dataset.viewPic, el.dataset.viewName));
    });

    picLightboxClose.addEventListener('click', closePicLightbox);
    picLightboxBackdrop.addEventListener('click', closePicLightbox);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !picLightbox.hidden) closePicLightbox();
    });
  }

  messagesEl.addEventListener('click', async (e) => {
    const btn = e.target.closest('.reaction-picker button');
    if (!btn) return;
    const msgId = btn.dataset.msgId;
    const emoji = btn.dataset.emoji;
    const url = reactUrlTemplate.replace('999999999', msgId);
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': csrftoken },
      body: new URLSearchParams({ emoji }),
    });
    if (!res.ok) return;
    const data = await res.json();
    const target = messagesEl.querySelector(`[data-reactions-for="${msgId}"]`);
    if (target) target.innerHTML = reactionsHtml(data.reactions);
  });
})();
