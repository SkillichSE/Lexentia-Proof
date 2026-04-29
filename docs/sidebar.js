// lex-sidebar web component — single source of truth for all pages
// usage: <lex-sidebar></lex-sidebar>
// active link is detected automatically via window.location.pathname

const SIDEBAR_LINKS = [
  {
    section: 'Data', id: 'sec-data',
    links: [
      { href: 'index.html',     label: 'Rankings',  icon: '<rect x="2" y="10" width="3" height="4" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="6.5" y="7" width="3" height="7" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="11" y="4" width="3" height="10" rx="1" stroke="currentColor" stroke-width="1.5"/>' },
      { href: 'trends.html',    label: 'Trends',    icon: '<path d="M2 12L6 8L9 10L14 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>' },
      { href: 'providers.html', label: 'Providers', icon: '<circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/><path d="M2 8h12M8 2c-2 1.5-3 3.5-3 6s1 4.5 3 6" stroke="currentColor" stroke-width="1.2" fill="none"/>' },
      { href: 'search.html',    label: 'Search',    icon: '<circle cx="7" cy="7" r="4.5" stroke="currentColor" stroke-width="1.5"/><path d="M10.5 10.5L13 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>' },
      { href: 'uptime.html',    label: 'Uptime',    icon: '<circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/><path d="M8 5v3.5l2.5 1.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>' },
    ]
  },
  {
    section: 'Tools', id: 'sec-tools',
    links: [
      { href: 'chat.html',       label: 'Chat',             icon: '<path d="M13 3H3a1 1 0 00-1 1v7a1 1 0 001 1h2v2.5l3-2.5h5a1 1 0 001-1V4a1 1 0 00-1-1z" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linejoin="round"/>' },
      { href: 'playground.html', label: 'Playground',       icon: '<rect x="2" y="3" width="12" height="9" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M5 7l2 2-2 2M9 11h2" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' },
      { href: 'model.html',      label: 'Model',            icon: '<circle cx="8" cy="6" r="2.5" stroke="currentColor" stroke-width="1.5"/><path d="M3 13c0-2.76 2.24-5 5-5s5 2.24 5 5" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/>' },
    ]
  },
  {
    section: 'Learn', id: 'sec-learn',
    links: [
      { href: 'lab.html',  label: 'Lab',  icon: '<path d="M6 2v5L3 12a1 1 0 00.9 1.5h8.2A1 1 0 0013 12L10 7V2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M5 2h6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>' },
      { href: 'news.html', label: 'News', icon: '<rect x="2" y="3" width="12" height="10" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M5 7h6M5 10h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>' },
    ]
  },
];

const CHEVRON = `<svg class="chevron" viewBox="0 0 16 16" fill="none"><path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;

function icon(inner) {
  return `<svg width="14" height="14" viewBox="0 0 16 16" fill="none">${inner}</svg>`;
}

function currentPage() {
  const p = window.location.pathname;
  const file = p.substring(p.lastIndexOf('/') + 1) || 'index.html';
  // github pages trailing slash -> index.html
  return file === '' ? 'index.html' : file;
}

class LexSidebar extends HTMLElement {
  connectedCallback() {
    this.className = 'left-sidebar';
    this.id = 'left-sidebar';
    const page = currentPage();

    let html = '<nav class="sidebar-nav">';

    for (const { section, id, links } of SIDEBAR_LINKS) {
      const items = links.map(({ href, label, icon: ic }) => {
        const active = href === page ? ' active' : '';
        return `<a href="${href}" class="sidebar-link${active}">${icon(ic)}<span class="link-label">${label}</span></a>`;
      }).join('\n');

      html += `
      <div class="sidebar-section open" id="${id}">
        <div class="sidebar-section-header" onclick="toggleSection('${id}')"><span>${section}</span>${CHEVRON}</div>
        <div class="sidebar-items">
          ${items}
        </div>
      </div>`;
    }

    const aboutActive = page === 'about.html' ? ' active' : '';
    html += `
      <div class="sidebar-footer-links">
        <a href="about.html" class="sidebar-link${aboutActive}">
          ${icon('<circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/><path d="M8 7v5M8 5v.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>')}
          <span class="link-label">About</span>
        </a>
      </div>`;

    html += `
      <div id="sidebar-auth-widget" style="margin-top:14px;padding:10px;border:1px solid rgba(148,163,184,.18);border-radius:10px;background:rgba(2,6,23,.45);">
        <div style="font-size:11px;color:var(--text-secondary);margin-bottom:6px;">author account</div>
        <div id="sidebar-auth-status" style="font-size:12px;color:var(--text-secondary);margin-bottom:8px;">not signed in</div>
        <button id="sidebar-auth-login" class="btn btn-sm" style="width:100%;margin-bottom:6px;">sign in github</button>
        <button id="sidebar-auth-logout" class="btn btn-sm btn-ghost" style="width:100%;display:none;">sign out</button>
      </div>`;

    html += '</nav>';
    this.innerHTML = html;
    if (window.initLegacyAuthWidget) window.initLegacyAuthWidget();
  }
}

customElements.define('lex-sidebar', LexSidebar);