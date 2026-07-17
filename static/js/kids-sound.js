/* Kids World sound manager — toggleable, persisted. Plays the short
   synthesized UI sounds at the paths declared in accounts/themes.py
   (static/audio/kids/*.wav). Missing files fail silently by design. */
(function () {
  const STORAGE_KEY = 'craftlanee-kids-sound-muted';
  const dataEl = document.getElementById('kw-sounds-data');
  const sounds = dataEl ? JSON.parse(dataEl.textContent) : {};
  const baseUrl = window.KIDS_THEME_STATIC_URL || '/static/';

  let muted = localStorage.getItem(STORAGE_KEY) === '1';

  const btn = document.getElementById('kwSoundToggleBtn');
  const icon = document.getElementById('kwSoundToggleIcon');

  function syncIcon() {
    if (!icon) return;
    icon.classList.toggle('bi-volume-up-fill', !muted);
    icon.classList.toggle('bi-volume-mute-fill', muted);
  }
  syncIcon();

  if (btn) {
    btn.addEventListener('click', function () {
      muted = !muted;
      localStorage.setItem(STORAGE_KEY, muted ? '1' : '0');
      syncIcon();
    });
  }

  function playSound(name) {
    if (muted) return;
    const path = sounds[name];
    if (!path) return;
    try {
      const audio = new Audio(baseUrl + path);
      audio.volume = 0.6;
      audio.play().catch(function () { /* no audio file yet — ignore */ });
    } catch (e) { /* Audio unsupported — ignore */ }
  }

  window.KidsSound = { play: playSound, isMuted: function () { return muted; } };
})();
