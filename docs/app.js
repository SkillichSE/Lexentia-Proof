/**
 * Shared JavaScript utilities for AI Benchmarker
 */

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

document.addEventListener('DOMContentLoaded', () => {
  initNavIndicator();
  initHamburger();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { formatNumber, formatDate, getRelativeTime, handleError };
}
