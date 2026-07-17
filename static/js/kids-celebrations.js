/* Kids World celebration effects — confetti, fireworks, treasure chest,
   coin collection, and a reusable glow pulse. Exposes window.KidsCelebrations
   so any page (quiz results, lesson completion, achievements) can call e.g.
   KidsCelebrations.confetti() when School-theme students hit a milestone. */
(function () {
  const COLORS = ['#38BDF8', '#FDE047', '#EC4899', '#4ADE80', '#A78BFA', '#FB923C'];

  function getLayer() {
    return document.getElementById('kwFxLayer');
  }

  function confetti(count) {
    const layer = getLayer();
    if (!layer) return;
    count = count || 60;
    for (let i = 0; i < count; i++) {
      const piece = document.createElement('div');
      piece.className = 'kw-confetti-piece';
      piece.style.left = Math.random() * 100 + 'vw';
      piece.style.background = COLORS[Math.floor(Math.random() * COLORS.length)];
      piece.style.animationDuration = (2 + Math.random() * 1.5) + 's';
      piece.style.animationDelay = (Math.random() * 0.4) + 's';
      layer.appendChild(piece);
      piece.addEventListener('animationend', function () { piece.remove(); });
    }
    if (window.KidsSound) window.KidsSound.play('celebration');
  }

  function fireworks(bursts) {
    const layer = getLayer();
    if (!layer) return;
    bursts = bursts || 3;
    for (let b = 0; b < bursts; b++) {
      setTimeout(function () {
        const cx = 15 + Math.random() * 70;
        const cy = 15 + Math.random() * 40;
        const particles = 18;
        for (let i = 0; i < particles; i++) {
          const angle = (i / particles) * Math.PI * 2;
          const dist = 60 + Math.random() * 40;
          const p = document.createElement('div');
          p.className = 'kw-firework-particle';
          p.style.left = cx + 'vw';
          p.style.top = cy + 'vh';
          p.style.background = COLORS[Math.floor(Math.random() * COLORS.length)];
          p.style.setProperty('--fx-x', Math.cos(angle) * dist + 'px');
          p.style.setProperty('--fx-y', Math.sin(angle) * dist + 'px');
          layer.appendChild(p);
          p.addEventListener('animationend', function () { p.remove(); });
        }
      }, b * 350);
    }
    if (window.KidsSound) window.KidsSound.play('achievement');
  }

  const TREASURE_CHEST_SVG =
    '<svg viewBox="0 0 48 40" xmlns="http://www.w3.org/2000/svg">' +
    '<path d="M2 16 Q24 2 46 16" fill="#B45309" stroke="#78350F" stroke-width="2"/>' +
    '<rect x="2" y="16" width="44" height="22" rx="4" fill="#B45309"/>' +
    '<rect x="2" y="16" width="44" height="8" fill="#92400E"/>' +
    '<rect x="20" y="16" width="8" height="10" rx="2" fill="#FDE047" stroke="#B45309" stroke-width="1.5"/>' +
    '</svg>';

  function treasureChest() {
    const layer = getLayer();
    if (!layer) return;
    const chest = document.createElement('div');
    chest.className = 'kw-treasure-chest';
    chest.innerHTML = TREASURE_CHEST_SVG;
    layer.appendChild(chest);
    chest.addEventListener('animationend', function () {
      setTimeout(function () { chest.remove(); }, 600);
    });
    if (window.KidsSound) window.KidsSound.play('reward');
  }

  function coinBurst(count) {
    const layer = getLayer();
    if (!layer) return;
    count = count || 6;
    const originX = 50, originY = 60;
    for (let i = 0; i < count; i++) {
      const coin = document.createElement('div');
      coin.className = 'kw-coin';
      coin.innerHTML = '<i class="bi bi-coin"></i>';
      coin.style.left = originX + 'vw';
      coin.style.top = originY + 'vh';
      coin.style.setProperty('--fx-x', (Math.random() * 80 - 40) + 'px');
      coin.style.setProperty('--fx-y', (-80 - Math.random() * 40) + 'px');
      layer.appendChild(coin);
      coin.addEventListener('animationend', function () { coin.remove(); });
    }
    if (window.KidsSound) window.KidsSound.play('reward');
  }

  function glow(el, ms) {
    if (!el) return;
    el.classList.add('kw-glow');
    if (ms) setTimeout(function () { el.classList.remove('kw-glow'); }, ms);
  }

  window.KidsCelebrations = { confetti, fireworks, treasureChest, coinBurst, glow };
})();
