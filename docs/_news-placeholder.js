<script>
async function loadNews() {
  try {
    const response = await fetch('data/results/news.json');
    const data = await response.json();
    
    document.getElementById('last-update').textContent = 
      `Last checked: ${new Date(data.updated).toLocaleString()}`;
    
    allNews = data.items || [];
    
    if (allNews.length === 0) {
      document.getElementById('news-feed').innerHTML = `
        <div style="text-align: center; padding: 64px 24px;">
          <div style="font-size: 4rem; margin-bottom: 20px; opacity: 0.3;">📰</div>
          <h3 style="color: var(--md-on-surface); margin-bottom: 12px;">No news yet</h3>
          <p style="color: var(--md-on-surface-var); max-width: 500px; margin: 0 auto; line-height: 1.6;">
            Our news aggregator checks AI provider blogs daily. News will appear here once we find relevant updates 
            about model releases, deprecations, or API changes.
          </p>
          <p style="color: var(--md-on-surface-low); font-size: 0.875rem; margin-top: 20px;">
            Sources monitored: Groq, Google AI, HuggingFace, Together AI
          </p>
        </div>
      `;
      return;
    }
    
    displayNews();
  } catch (error) {
    console.error('Error loading news:', error);
    document.getElementById('news-feed').innerHTML = `
      <div style="text-align: center; padding: 64px 24px;">
        <div style="font-size: 4rem; margin-bottom: 20px;">⚠️</div>
        <h3 style="color: var(--md-on-surface);">Unable to load news</h3>
        <p style="color: var(--md-on-surface-var); margin-top: 12px;">
          Please check back later or view our 
          <a href="https://github.com/SkillichSE/Klyxe" target="_blank" style="color: var(--md-primary);">GitHub repository</a> 
          for updates.
        </p>
      </div>
    `;
  }
}
</script>
