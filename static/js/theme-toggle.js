(function () {
  const STORAGE_KEY = 'craftlanee-color-scheme';
  const root = document.documentElement;
  const btn = document.getElementById('themeToggleBtn');
  const icon = document.getElementById('themeToggleIcon');

  function applyScheme(scheme) {
    if (scheme === 'dark') {
      root.setAttribute('data-theme', 'dark');
      if (icon) { icon.classList.remove('bi-moon-stars'); icon.classList.add('bi-sun'); }
    } else {
      root.setAttribute('data-theme', 'light');
      if (icon) { icon.classList.remove('bi-sun'); icon.classList.add('bi-moon-stars'); }
    }
  }

  const saved = localStorage.getItem(STORAGE_KEY);
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  applyScheme(saved || (prefersDark ? 'dark' : 'light'));

  if (btn) {
    btn.addEventListener('click', function () {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      applyScheme(next);
      localStorage.setItem(STORAGE_KEY, next);
    });
  }
})();
