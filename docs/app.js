/**
 * Shared JavaScript utilities for AI Benchmarker
 */

// sidebar section collapse/expand
function toggleSection(id) {
  const el = document.getElementById(id);
  if (el) el.classList.toggle('open');
}
function toggleSubSection(id) {
  const el = document.getElementById(id);
  if (el) el.classList.toggle('open');
}

// Format large numbers
function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

// Format date
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

// Get relative time
function getRelativeTime(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);
  
  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
}

// Error handling
function handleError(error, container) {
  console.error('Error:', error);
  if (container) {
    container.innerHTML = `
      <div class="card" style="text-align: center; padding: 48px; background: var(--surface);">
        <h3>Unable to load data</h3>
        <p style="color: var(--text-secondary); margin-top: 8px;">
          Please try refreshing the page or check back later.
        </p>
      </div>
    `;
  }
}

// ─── Sliding nav indicator ────────────────────────────────────────────────────
function initNavIndicator() {
  const nav = document.querySelector('.nav');
  if (!nav) return;

  // Create indicator element
  const indicator = document.createElement('div');
  indicator.className = 'nav-indicator';
  nav.appendChild(indicator);

  function moveToLink(link) {
    if (!link) { indicator.classList.remove('visible'); return; }
    const navRect = nav.getBoundingClientRect();
    const linkRect = link.getBoundingClientRect();
    const pad = 14; // matches nav-link padding
    indicator.style.left  = (linkRect.left - navRect.left + pad) + 'px';
    indicator.style.width = (linkRect.width - pad * 2) + 'px';
    indicator.classList.add('visible');
  }

  const activeLink = nav.querySelector('.nav-link.active');
  // Set initial position without transition
  indicator.style.transition = 'none';
  moveToLink(activeLink);
  requestAnimationFrame(() => {
    indicator.style.transition = '';
  });

  // Hover: slide to hovered link
  nav.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('mouseenter', () => moveToLink(link));
    link.addEventListener('mouseleave', () => moveToLink(activeLink));
  });
}

// ─── Hamburger mobile menu ────────────────────────────────────────────────────
function initHamburger() {
  const hamburger = document.getElementById('nav-hamburger');
  const drawer    = document.getElementById('nav-drawer');
  if (!hamburger || !drawer) return;

  hamburger.addEventListener('click', () => {
    const open = hamburger.classList.toggle('open');
    if (open) {
      drawer.style.display = 'flex';
      requestAnimationFrame(() => drawer.classList.add('open'));
    } else {
      drawer.classList.remove('open');
      drawer.addEventListener('transitionend', () => {
        if (!drawer.classList.contains('open')) drawer.style.display = 'none';
      }, { once: true });
    }
  });

  // Close on outside click
  document.addEventListener('click', e => {
    if (!hamburger.contains(e.target) && !drawer.contains(e.target)) {
      hamburger.classList.remove('open');
      drawer.classList.remove('open');
      drawer.addEventListener('transitionend', () => {
        if (!drawer.classList.contains('open')) drawer.style.display = 'none';
      }, { once: true });
    }
  });
}

// ─── Sidebar expand/collapse (overlay mode — content does NOT shift) ──────────
function initSidebar() {
  const sidebar = document.getElementById('left-sidebar');
  if (!sidebar) return;
  const isMobileViewport = () => window.matchMedia('(max-width: 768px)').matches;

  let enterTimer = null;
  let leaveTimer = null;

  // Use CSS containment for paint optimization
  sidebar.style.contain = 'layout style';

  sidebar.addEventListener('mouseenter', () => {
    if (isMobileViewport()) return;
    clearTimeout(leaveTimer);
    enterTimer = setTimeout(() => {
      sidebar.classList.add('expanded');
    }, 80);
  });

  sidebar.addEventListener('mouseleave', () => {
    if (isMobileViewport()) return;
    clearTimeout(enterTimer);
    leaveTimer = setTimeout(() => {
      sidebar.classList.remove('expanded');
    }, 150);
  });

  const ensureMobileControls = () => {
    let overlay = document.getElementById('sidebar-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'sidebar-overlay';
      overlay.className = 'sidebar-overlay';
      document.body.appendChild(overlay);
    }

    let btn = document.getElementById('sidebar-mobile-toggle');
    if (!btn) {
      const header = document.querySelector('.header-content');
      if (!header) return;
      btn = document.createElement('button');
      btn.id = 'sidebar-mobile-toggle';
      btn.className = 'mobile-menu-btn';
      btn.setAttribute('aria-label', 'Open menu');
      btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M2 4h14M2 9h14M2 14h14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>';
      header.appendChild(btn);
    }

    const openSidebar = () => {
      sidebar.classList.add('open');
      overlay.classList.add('open');
    };
    const closeSidebar = () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('open');
    };

    btn.onclick = null;
    btn.addEventListener('click', () => (sidebar.classList.contains('open') ? closeSidebar() : openSidebar()));
    overlay.onclick = closeSidebar;

    const sync = () => {
      if (isMobileViewport()) {
        sidebar.classList.add('expanded');
        btn.style.display = 'flex';
      } else {
        btn.style.display = 'none';
        closeSidebar();
        sidebar.classList.remove('expanded');
      }
    };
    sync();
    window.addEventListener('resize', sync);
  };

  ensureMobileControls();
}

document.addEventListener('DOMContentLoaded', () => {
  initNavIndicator();
  initHamburger();
  initSidebar();
  initLegacyAuthWidget();
  handleOAuthCallback();
});

// Handle OAuth callback and redirect to production if needed
function handleOAuthCallback() {
  const hash = window.location.hash;
  if (hash && hash.includes('access_token')) {
    // We're on localhost but got auth callback - redirect to production with same hash
    if (window.location.origin.includes('localhost')) {
      const prodUrl = 'https://klyxe-ai.vercel.app/' + hash;
      window.location.replace(prodUrl);
      return;
    }
    // On production - exchange token and clear hash
    exchangeTokenAndClearHash();
  }
}

async function exchangeTokenAndClearHash() {
  const sb = await window.ensureSupabase();
  if (!sb) return;
  try {
    // Supabase automatically handles the hash on init, just clear it
    history.replaceState(null, '', window.location.pathname);
    await window.initLegacyAuthWidget?.();
  } catch (err) {
    console.error('Auth exchange failed:', err);
  }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { formatNumber, formatDate, getRelativeTime, handleError };
}

// Auth widget for sidebar
(function () {
  let supabaseClient = null;
  let currentUser = null;

  async function getPublicConfig() {
    try {
      const res = await fetch("/api/public-config");
      if (!res.ok) throw new Error("config fetch failed");
      return res.json();
    } catch (e) {
      return {};
    }
  }

  async function ensureSupabase() {
    if (supabaseClient) return supabaseClient;
    const cfg = await getPublicConfig();
    if (!cfg.supabaseUrl || !cfg.supabaseAnonKey || !window.supabase) return null;
    supabaseClient = window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseAnonKey);
    return supabaseClient;
  }
  window.ensureSupabase = ensureSupabase;

  async function refreshAuthUi() {
    const status = document.getElementById("sidebar-auth-status");
    const login = document.getElementById("sidebar-auth-login");
    const logout = document.getElementById("sidebar-auth-logout");
    if (!status || !login || !logout) return;
    try {
      const sb = await ensureSupabase();
      if (!sb) {
        status.textContent = "auth unavailable";
        return;
      }
      const { data: { user } } = await sb.auth.getUser();
      currentUser = user || null;
      if (currentUser) {
        status.textContent = currentUser.email || "signed in";
        login.style.display = "none";
        logout.style.display = "";
      } else {
        status.textContent = "not signed in";
        login.style.display = "";
        logout.style.display = "none";
      }
    } catch (err) {
      status.textContent = err.message || "auth error";
    }
  }

  async function onLogin() {
    const sb = await ensureSupabase();
    if (!sb) return;
    const redirectUrl = window.location.origin + window.location.pathname;
    await sb.auth.signInWithOAuth({
      provider: "github",
      options: { redirectTo: redirectUrl }
    });
  }

  async function onLogout() {
    const sb = await ensureSupabase();
    if (!sb) return;
    await sb.auth.signOut();
    await refreshAuthUi();
  }

  window.initLegacyAuthWidget = function () {
    const login = document.getElementById("sidebar-auth-login");
    const logout = document.getElementById("sidebar-auth-logout");
    if (login) login.addEventListener('click', () => void onLogin());
    if (logout) logout.addEventListener('click', () => void onLogout());
    void refreshAuthUi();
  };
})();
