/* Kids World button ripple + click sound, delegated so it also covers
   buttons rendered after page load (AJAX-updated dashboard widgets etc). */
(function () {
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.btn, .kw-claim-btn');
    if (!btn) return;

    const rect = btn.getBoundingClientRect();
    const ripple = document.createElement('span');
    const size = Math.max(rect.width, rect.height);
    ripple.className = 'kw-ripple';
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
    ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';

    if (getComputedStyle(btn).position === 'static') {
      btn.style.position = 'relative';
    }
    btn.appendChild(ripple);
    ripple.addEventListener('animationend', function () { ripple.remove(); });

    if (window.KidsSound) window.KidsSound.play('click');
  });
})();
