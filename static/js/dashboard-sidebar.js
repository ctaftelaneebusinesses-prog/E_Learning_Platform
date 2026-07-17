(function () {
  var MOBILE_QUERY = '(max-width: 991.98px)';

  document.addEventListener('DOMContentLoaded', function () {
    var layout = document.getElementById('dashLayout');
    if (!layout) return;

    var panel = layout.dataset.panel || 'dash';
    var storageKey = 'craftlanee-' + panel + '-sidebar-collapsed';
    var scrollKey = 'craftlanee-' + panel + '-sidebar-scroll';
    var collapseBtn = document.getElementById('dashSidebarCollapseBtn');
    var mobileToggle = document.getElementById('dashMobileToggle');
    var overlay = document.getElementById('dashSidebarOverlay');
    var sidebarNav = document.querySelector('.dash-sidebar-nav');

    // Restore collapsed state on desktop
    if (localStorage.getItem(storageKey) === '1' && !window.matchMedia(MOBILE_QUERY).matches) {
      layout.classList.add('collapsed');
    }

    // Restore sidebar scroll position so it doesn't reset to the top on
    // every full-page navigation, and keep it up to date as the user scrolls.
    if (sidebarNav) {
      var savedScroll = sessionStorage.getItem(scrollKey);
      if (savedScroll !== null) {
        sidebarNav.scrollTop = parseInt(savedScroll, 10) || 0;
      }

      sidebarNav.addEventListener('scroll', function () {
        sessionStorage.setItem(scrollKey, sidebarNav.scrollTop);
      });

      // Also capture the scroll position right before navigating away, in
      // case the browser doesn't fire a final 'scroll' event beforehand.
      window.addEventListener('beforeunload', function () {
        sessionStorage.setItem(scrollKey, sidebarNav.scrollTop);
      });
    }

    function closeMobile() {
      layout.classList.remove('mobile-open');
    }

    if (collapseBtn) {
      collapseBtn.addEventListener('click', function () {
        var collapsed = layout.classList.toggle('collapsed');
        localStorage.setItem(storageKey, collapsed ? '1' : '0');
      });
    }

    if (mobileToggle) {
      mobileToggle.addEventListener('click', function () {
        layout.classList.add('mobile-open');
      });
    }

    if (overlay) {
      overlay.addEventListener('click', closeMobile);
    }

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMobile();
    });

    window.addEventListener('resize', function () {
      if (!window.matchMedia(MOBILE_QUERY).matches) {
        closeMobile();
      }
    });
  });
})();
