import React from 'react';

const ERROR_ICONS = {
  PRIVATE_CONTENT: '🔒',
  RATE_LIMITED: '⏱',
  EXTRACTION_FAILED: '⚠️',
  DOWNLOAD_FAILED: '💔',
  default: '✕',
};

const ERROR_TIPS = {
  PRIVATE_CONTENT: 'This content requires login or is set to private.',
  RATE_LIMITED: 'Platform is throttling requests. Try again in a minute.',
  default: null,
};

export default function ErrorMessage({ error, code, onDismiss }) {
  if (!error) return null;

  const icon = ERROR_ICONS[code] || ERROR_ICONS.default;
  const tip = ERROR_TIPS[code] || ERROR_TIPS.default;

  return (
    <div className="w-full max-w-2xl mx-auto mt-6 animate-fade-in p-5 rounded-2xl bg-error/5 border border-error/20 flex items-start gap-4">
      <div className="w-10 h-10 rounded-xl bg-error/10 flex items-center justify-center text-xl flex-shrink-0">
        {icon}
      </div>
      <div className="flex-1 min-w-0 py-0.5">
        <h4 className="text-[0.65rem] font-black uppercase tracking-[0.2em] text-error mb-1">Analysis Error</h4>
        <p className="text-sm font-bold text-text-primary leading-snug">{error}</p>
        {tip && <p className="text-xs font-medium text-text-muted mt-2 opacity-80">{tip}</p>}
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="p-2 rounded-lg text-text-muted hover:bg-error/5 hover:text-error transition-all"
          title="Dismiss"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}
