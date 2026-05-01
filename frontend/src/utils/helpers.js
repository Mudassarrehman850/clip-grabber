export const PLATFORMS = {
  youtube: {
    name: 'YouTube',
    color: '#ff4444',
    bgClass: 'badge-youtube',
  },
  instagram: {
    name: 'Instagram',
    color: '#f472b6',
    bgClass: 'badge-instagram',
  },
  tiktok: {
    name: 'TikTok',
    color: '#22d3ee',
    bgClass: 'badge-tiktok',
  },
  facebook: {
    name: 'Facebook',
    color: '#4f9eff',
    bgClass: 'badge-facebook',
  },
  pinterest: {
    name: 'Pinterest',
    color: '#ff4b55',
    bgClass: 'badge-pinterest',
  },
};

export function detectPlatformClient(url) {
  if (!url) return null;
  const lower = url.toLowerCase();
  if (lower.includes('youtube.com') || lower.includes('youtu.be')) return 'youtube';
  if (lower.includes('instagram.com')) return 'instagram';
  if (lower.includes('tiktok.com')) return 'tiktok';
  if (lower.includes('facebook.com') || lower.includes('fb.watch')) return 'facebook';
  if (lower.includes('pinterest.com') || lower.includes('pin.it')) return 'pinterest';
  return null;
}

export function formatNumber(n) {
  if (!n && n !== 0) return null;
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export function formatDate(dateStr) {
  if (!dateStr || dateStr.length !== 8) return null;
  const year = dateStr.slice(0, 4);
  const month = dateStr.slice(4, 6);
  const day = dateStr.slice(6, 8);
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  return `${months[parseInt(month) - 1]} ${parseInt(day)}, ${year}`;
}

export function getFormatButtonClass(type) {
  switch (type) {
    case 'audio':   return 'btn-download-audio';
    case 'image':   return 'btn-download-image';
    case 'archive': return 'btn-download-nowm';
    case 'video':
    default:        return 'btn-download-video';
  }
}

export function triggerBrowserDownload(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

export function getHistoryFromStorage() {
  try {
    const raw = localStorage.getItem('sdl_history');
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

export function addToHistory(item) {
  try {
    const history = getHistoryFromStorage();
    const exists = history.find(h => h.url === item.url);
    if (exists) return;
    localStorage.setItem('sdl_history', JSON.stringify([item, ...history].slice(0, 20)));
  } catch {}
}

export function clearHistory() {
  try { localStorage.removeItem('sdl_history'); } catch {}
}
