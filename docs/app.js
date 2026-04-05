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

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { formatNumber, formatDate, getRelativeTime, handleError };
}
