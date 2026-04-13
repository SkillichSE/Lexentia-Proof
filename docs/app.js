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

let currentMode = 'proof'; // 'proof' or 'lab'
let currentSubsection = 'rankings'; // for lab: 'library', 'presets', 'insights'
let originalMainContent = ''; // to store the original proof content

const promptsData = [
  {
    title: "Креативный писатель",
    systemPrompt: "You are a creative writing assistant. Help users generate engaging stories, poems, and creative content. Be imaginative and inspiring.",
    optimizedFor: ["Grok-1", "Llama 3.3"],
    tags: ["Креатив", "Письмо"]
  },
  {
    title: "Логический анализатор",
    systemPrompt: "You are a logical reasoning expert. Analyze arguments, identify fallacies, and provide structured reasoning for complex problems.",
    optimizedFor: ["Nemotron 3", "Claude 3.5"],
    tags: ["Логика", "Анализ"]
  },
  {
    title: "Кодер Python",
    systemPrompt: "You are an expert Python developer. Write clean, efficient, and well-documented code. Explain your solutions step by step.",
    optimizedFor: ["DeepSeek Coder", "CodeLlama"],
    tags: ["Код", "Python"]
  },
  {
    title: "Математический помощник",
    systemPrompt: "You are a mathematics tutor. Explain concepts clearly, solve problems step-by-step, and provide proofs when appropriate.",
    optimizedFor: ["GPT-4o", "Mathstral"],
    tags: ["Математика", "Обучение"]
  },
  {
    title: "Технический писатель",
    systemPrompt: "You are a technical writer. Create clear, concise documentation, tutorials, and explanations for technical concepts.",
    optimizedFor: ["Llama 3.3", "Nemotron 3"],
    tags: ["Технический", "Документация"]
  },
  {
    title: "Анализ данных",
    systemPrompt: "You are a data analyst. Help with data interpretation, statistical analysis, and visualization recommendations.",
    optimizedFor: ["Claude 3.5", "GPT-4o"],
    tags: ["Данные", "Анализ"]
  }
];

function switchMode(mode) {
  currentMode = mode;
  const logo = document.querySelector('.logo');
  const nav = document.querySelector('.nav');
  const heroHeadline = document.querySelector('.hero-headline');
  const heroSub = document.querySelector('#hero-sub-text');
  const modeBtns = document.querySelectorAll('.mode-btn');
  
  modeBtns.forEach(btn => btn.classList.remove('active'));
  document.querySelector(`[data-mode="${mode}"]`).classList.add('active');
  
  if (mode === 'proof') {
    logo.innerHTML = '<img src="media/L_logo.png" alt="Lexentia Proof logo" class="logo-icon">Lexentia Proof';
    heroHeadline.textContent = 'Lexentia Proof';
    heroSub.textContent = 'Free AI models, ranked daily';
    nav.innerHTML = `
      <a href="index.html" class="nav-link active">Rankings</a>
      <a href="about.html" class="nav-link">About</a>
      <a href="search.html" class="nav-link">Search</a>
      <a href="providers.html" class="nav-link">Providers</a>
      <a href="trends.html" class="nav-link">Trends</a>
      <a href="news.html" class="nav-link">News</a>
    `;
    // Restore original content
    const main = document.querySelector('main');
    if (main && originalMainContent) {
      main.innerHTML = originalMainContent;
    }
  } else {
    logo.innerHTML = '<img src="media/L_logo.png" alt="Lexentia Lab logo" class="logo-icon">Lexentia Lab';
    heroHeadline.textContent = 'Lexentia Lab';
    heroSub.textContent = 'AI Research & Tools';
    nav.innerHTML = `
      <a href="#" class="nav-link active" data-sub="library">Library</a>
      <a href="#" class="nav-link" data-sub="presets">Presets</a>
      <a href="#" class="nav-link" data-sub="insights">Insights</a>
    `;
    loadLabContent('library');
  }
  
  initNavIndicator();
}

function switchSubsection(sub) {
  currentSubsection = sub;
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => link.classList.remove('active'));
  document.querySelector(`[data-sub="${sub}"]`).classList.add('active');
  loadLabContent(sub);
}

function loadLabContent(sub) {
  const main = document.querySelector('main') || document.body;
  let content = '';
  
  if (sub === 'library') {
    content = '<div class="lab-section"><h2>Library</h2><div class="prompts-grid">';
    promptsData.forEach(prompt => {
      content += `
        <div class="card prompt-card">
          <h3>${prompt.title}</h3>
          <p class="prompt-text">${prompt.systemPrompt}</p>
          <div class="prompt-meta">
            <div class="optimized-for">Optimized for: ${prompt.optimizedFor.join(', ')}</div>
            <div class="tags">${prompt.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}</div>
          </div>
          <button class="copy-btn" onclick="copyToClipboard('${prompt.systemPrompt.replace(/'/g, "\\'")}')">Copy</button>
        </div>
      `;
    });
    content += '</div></div>';
    main.innerHTML = content;
  } else if (sub === 'presets') {
    content = '<div class="lab-section"><h2>Presets</h2><div class="presets-list">';
    // Load presets
    const presetFiles = ['llama-3.3-groq.json', 'grok-1-xai.json', 'nemotron-3-together.json'];
    let loaded = 0;
    presetFiles.forEach(file => {
      fetch(`content/presets/${file}`)
        .then(res => res.json())
        .then(data => {
          content += `
            <div class="card preset-card">
              <h3>${data.model} on ${data.provider}</h3>
              <p>${data.description}</p>
              <pre>${JSON.stringify(data.parameters, null, 2)}</pre>
              <button class="copy-btn" onclick="copyToClipboard('${JSON.stringify(data.parameters)}')">Copy JSON</button>
            </div>
          `;
          loaded++;
          if (loaded === presetFiles.length) {
            main.innerHTML = content + '</div></div>';
          }
        });
    });
  } else if (sub === 'insights') {
    content = '<div class="lab-section"><h2>Insights</h2><div class="articles-list">';
    // Load articles
    const articleFiles = ['nemotron-3-breakthrough.md', 'token-optimization-tips.md'];
    let loaded = 0;
    articleFiles.forEach(file => {
      fetch(`content/articles/${file}`)
        .then(res => res.text())
        .then(md => {
          const html = marked.parse(md);
          content += `<div class="card article-card">${html}</div>`;
          loaded++;
          if (loaded === articleFiles.length) {
            main.innerHTML = content + '</div></div>';
          }
        });
    });
  }
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    // Show feedback
    alert('Copied to clipboard!');
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initNavIndicator();
  initHamburger();
  
  // Save original content
  const main = document.querySelector('main');
  if (main) {
    originalMainContent = main.innerHTML;
  }
  
  // Mode switcher
  document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', () => switchMode(btn.dataset.mode));
  });
  
  // Subsection switcher for lab
  document.addEventListener('click', e => {
    if (e.target.classList.contains('nav-link') && e.target.dataset.sub) {
      e.preventDefault();
      switchSubsection(e.target.dataset.sub);
    }
  });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { formatNumber, formatDate, getRelativeTime, handleError };
}
