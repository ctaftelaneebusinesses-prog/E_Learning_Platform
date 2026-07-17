(function () {
  const POLL_INTERVAL_MS = 8000;
  const UNREAD_COUNT_URL = '/messages/unread-count/';

  let lastUnreadCount = null;
  let lastSubjectSeen = null;

  function updateBadges(count) {
    document.querySelectorAll('[data-broadcast-badge]').forEach((el) => {
      el.textContent = count;
      el.classList.toggle('d-none', count === 0);
    });
  }

  function showToast(latest) {
    const container = document.getElementById('broadcastToastContainer');
    if (!container || !latest) return;

    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-bg-primary border-0';
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">
          📩 New message from ${latest.sender}: ${latest.subject}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    `;
    container.appendChild(toast);

    if (window.bootstrap && window.bootstrap.Toast) {
      const bsToast = new window.bootstrap.Toast(toast, { delay: 6000 });
      bsToast.show();
      toast.addEventListener('hidden.bs.toast', () => toast.remove());
    } else {
      setTimeout(() => toast.remove(), 6000);
    }
  }

  async function poll() {
    try {
      const res = await fetch(UNREAD_COUNT_URL, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
      if (!res.ok) return;
      const data = await res.json();

      updateBadges(data.unread_count);

      const isFirstPoll = lastUnreadCount === null;
      const subjectChanged = data.latest && data.latest.subject !== lastSubjectSeen;
      if (!isFirstPoll && data.unread_count > lastUnreadCount && subjectChanged) {
        showToast(data.latest);
      }

      lastUnreadCount = data.unread_count;
      if (data.latest) lastSubjectSeen = data.latest.subject;
    } catch (e) {
      /* network hiccup — will retry on next tick */
    }
  }

  poll();
  setInterval(poll, POLL_INTERVAL_MS);
})();
