(function () {
  const csrfInput = document.querySelector('#csrfHolder [name=csrfmiddlewaretoken]');
  const csrftoken = csrfInput ? csrfInput.value : '';

  document.querySelectorAll('.msg-card').forEach((card) => {
    card.addEventListener('click', async () => {
      const full = card.querySelector('.msg-card-full');
      const preview = card.querySelector('.msg-card-preview');
      if (full) full.classList.toggle('d-none');
      if (preview) preview.classList.toggle('d-none');

      if (!card.classList.contains('msg-card-unread')) return;

      const entryId = card.dataset.entryId;
      try {
        const res = await fetch(`/messages/inbox/${entryId}/read/`, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': csrftoken },
        });
        if (!res.ok) return;
        const data = await res.json();
        card.classList.remove('msg-card-unread');
        const dot = card.querySelector('.msg-unread-dot');
        if (dot) dot.remove();
        document.querySelectorAll('[data-broadcast-badge]').forEach((el) => {
          el.textContent = data.unread_count;
          el.classList.toggle('d-none', data.unread_count === 0);
        });
      } catch (e) {
        /* network hiccup */
      }
    });
  });
})();
