import React, { useState, useEffect } from 'react';
import { getHistoryFromStorage, clearHistory, PLATFORMS } from '../utils/helpers';

function HistoryItem({ item, onSelect }) {
  const [imgErr, setImgErr] = useState(false);
  const platformInfo = PLATFORMS[item.platform];
  const timeAgo = getTimeAgo(item.timestamp);

  return (
    <button
      onClick={() => onSelect(item.url)}
      className="flex items-center gap-4 w-full text-left p-3.5 rounded-2xl bg-bg-card border border-border-color hover:bg-bg-input hover:border-brand/30 transition-all duration-300 group shadow-sm hover:shadow-md"
    >
      {/* Thumbnail */}
      <div className="flex-shrink-0 w-16 h-12 rounded-xl overflow-hidden bg-bg-input border border-border-color shadow-inner">
        {item.thumbnail && !imgErr ? (
          <img
            src={item.thumbnail}
            alt=""
            onError={() => setImgErr(true)}
            className="w-full h-full object-cover transition-transform group-hover:scale-110"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-xl bg-brand/5"
            style={{ color: platformInfo?.color || 'var(--brand)' }}>
            {item.platform === 'youtube' ? '📺' : item.platform === 'instagram' ? '📸' : '♪'}
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm text-text-primary truncate font-bold leading-tight group-hover:text-brand transition-colors">
          {item.title || 'Untitled'}
        </p>
        <div className="flex items-center gap-2.5 mt-1.5">
          {platformInfo && (
            <span className={`text-[0.6rem] px-1.5 py-0.5 rounded-md font-bold uppercase tracking-wider border ${platformInfo.bgClass}`}>
              {platformInfo.name}
            </span>
          )}
          <span className="text-text-muted text-[0.65rem] font-bold">{timeAgo}</span>
        </div>
      </div>

      {/* Arrow */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-bg-input border border-border-color group-hover:bg-brand group-hover:text-white transition-all">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 18l6-6-6-6" />
        </svg>
      </div>
    </button>
  );
}

function getTimeAgo(timestamp) {
  if (!timestamp) return '';
  const diff = Date.now() - timestamp;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function HistoryPanel({ onSelect }) {
  const [history, setHistory] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    setHistory(getHistoryFromStorage());
  }, [isOpen]);

  const handleClear = () => {
    if (window.confirm('Are you sure you want to clear your download history?')) {
        clearHistory();
        setHistory([]);
    }
  };

  if (history.length === 0 && !isOpen) return null;

  return (
    <div className="w-full max-w-2xl mx-auto mt-12 space-y-4 animate-fade-in text-center">
      {/* Toggle button */}
      <button
        onClick={() => setIsOpen((v) => !v)}
        className="inline-flex items-center gap-2.5 px-6 py-2.5 rounded-full bg-bg-card border border-border-color text-xs font-bold text-text-secondary hover:text-brand hover:border-brand/40 transition-all duration-300 shadow-sm"
      >
        <svg
          width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"
          className={`transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
        Recent Downloads ({history.length})
      </button>

      {isOpen && (
        <div className="pt-4 space-y-3 animate-fade-in">
          {history.length > 0 ? (
            <>
                <div className="flex flex-col gap-3">
                    {history.map((item, i) => (
                    <HistoryItem
                        key={item.url + i}
                        item={item}
                        onSelect={(url) => {
                            onSelect(url);
                            setIsOpen(false);
                        }}
                    />
                    ))}
                </div>
                <button
                    onClick={handleClear}
                    className="text-[0.7rem] font-bold text-error/60 hover:text-error transition-colors px-4 py-2 uppercase tracking-widest"
                >
                    Clear History
                </button>
            </>
          ) : (
             <div className="py-10 px-6 rounded-3xl border-2 border-dashed border-border-color/50 text-text-muted">
                <p className="text-sm font-bold">Your history is currently empty</p>
                <p className="text-xs mt-1">Files you analyze will appear here for quick access</p>
             </div>
          )}
        </div>
      )}
    </div>
  );
}
