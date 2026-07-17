/* GROWTH JOURNEY — Intermediate theme animated background driver.
   Only runs when .intermediate-world-bg is present on the page (see
   templates/base.html, gated on active_theme.key == 'intermediate').
   Handles three independent things the CSS can't do on its own:
     1. Day/night cycle, read from the real local clock (data-tod).
     2. Randomized weather rotation (data-weather).
     3. Mouse-position parallax (--iw-mx / --iw-my custom properties) plus
        a transient "interactive" state for the wave/glow/scatter flourishes. */
(function () {
  var scene = document.querySelector('.intermediate-world-bg');
  if (!scene) return;

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- Day / night, from the real clock ------------------------------ */
  function timeOfDay() {
    var hour = new Date().getHours();
    if (hour >= 5 && hour < 11) return 'morning';
    if (hour >= 11 && hour < 17) return 'afternoon';
    if (hour >= 17 && hour < 20) return 'evening';
    return 'night';
  }

  function applyTimeOfDay() {
    scene.setAttribute('data-tod', timeOfDay());
  }

  applyTimeOfDay();
  setInterval(applyTimeOfDay, 60 * 1000);

  /* ---- Weather, randomly rotated on an interval ----------------------- */
  var weathers = ['sunny', 'cloudy', 'rain', 'rainbow', 'winter', 'autumn'];

  function pickWeather(exclude) {
    var options = weathers.filter(function (w) { return w !== exclude; });
    return options[Math.floor(Math.random() * options.length)];
  }

  function applyWeather(next) {
    scene.setAttribute('data-weather', next);
  }

  applyWeather(pickWeather());
  if (!reduceMotion) {
    setInterval(function () {
      applyWeather(pickWeather(scene.getAttribute('data-weather')));
    }, 55 * 1000);
  }

  /* ---- Mouse parallax + interactive flourishes ------------------------ */
  if (reduceMotion) return;

  var rafPending = false;
  var lastX = 0.5;
  var lastY = 0.5;
  var idleTimer = null;

  function updateParallax() {
    rafPending = false;
    var mx = (lastX - 0.5) * 2;
    var my = (lastY - 0.5) * 2;
    scene.style.setProperty('--iw-mx', mx.toFixed(3));
    scene.style.setProperty('--iw-my', my.toFixed(3));
  }

  window.addEventListener('mousemove', function (e) {
    lastX = e.clientX / window.innerWidth;
    lastY = e.clientY / window.innerHeight;
    if (!rafPending) {
      rafPending = true;
      requestAnimationFrame(updateParallax);
    }

    scene.classList.add('iw-mouse-active');
    clearTimeout(idleTimer);
    idleTimer = setTimeout(function () {
      scene.classList.remove('iw-mouse-active');
    }, 1200);
  }, { passive: true });
})();
