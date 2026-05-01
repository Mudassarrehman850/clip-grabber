import React, { useState, useRef, useEffect } from 'react';
import { detectPlatformClient, PLATFORMS } from '../utils/helpers';

const PlatformIcon = ({ platform, className = "w-5 h-5" }) => {
  const icons = {
    youtube: (
      <svg className={className} viewBox="0 0 24 24" fill="currentColor">
        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
      </svg>
    ),
    instagram: (
      <svg className={className} viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/>
      </svg>
    ),
    tiktok: (
      <svg className={className} viewBox="0 0 24 24" fill="currentColor">
        <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>
      </svg>
    ),
    facebook: (
      <svg className={className} viewBox="0 0 24 24" fill="currentColor">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
      </svg>
    ),
    pinterest: (
      <svg className={className} viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 0 1 .083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/>
      </svg>
    ),
  };
  return icons[platform] || (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
    </svg>
  );
};


export default function URLInput({ onSubmit, isLoading, onReset, hasResult }) {
  const [inputUrl, setInputUrl] = useState('');
  const [detectedPlatform, setDetectedPlatform] = useState(null);
  const inputRef = useRef(null);

  useEffect(() => {
    const p = detectPlatformClient(inputUrl);
    setDetectedPlatform(p);
  }, [inputUrl]);

  const handlePaste = (e) => {
    e.preventDefault();
    // Immediate detection on paste
    const pasted = e.clipboardData.getData('text');
    if (pasted) {
      const p = detectPlatformClient(pasted);
      setDetectedPlatform(p);
      if (p) {
        setInputUrl(pasted);
        setTimeout(() => onSubmit(pasted), 50);
      }
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputUrl.trim()) {
      onSubmit(inputUrl.trim());
    }
  };

  const handleClear = () => {
    setInputUrl('');
    setDetectedPlatform(null);
    if (hasResult) onReset();
    inputRef.current?.focus();
  };

  const platformInfo = detectedPlatform ? PLATFORMS[detectedPlatform] : null;

  return (
    <div className="w-full max-w-2xl mx-auto space-y-4 animate-fade-in">
      <form onSubmit={handleSubmit}>
        <div className="relative flex flex-col sm:flex-row items-stretch sm:items-center p-2 rounded-3xl bg-bg-card border border-border-color shadow-xl focus-within:border-brand/40 focus-within:ring-4 focus-within:ring-brand-alpha transition-all duration-300">
          
          {/* Platform Indicator */}
          <div className="flex items-center pl-3 pr-2 py-2 sm:py-0 border-b sm:border-b-0 sm:border-r border-border-color/50 mr-2">
             <div className="flex items-center gap-2">
                <div 
                    className={`w-10 h-10 rounded-xl flex items-center justify-center transition-colors duration-300 ${platformInfo ? '' : 'bg-bg-input text-text-muted'}`}
                    style={{ color: platformInfo ? platformInfo.color : undefined }}
                >
                    <PlatformIcon platform={detectedPlatform} className="w-6 h-6" />
                </div>
                {platformInfo && (
                    <span className="text-xs font-bold text-text-primary uppercase tracking-wider hidden sm:inline ml-1">
                        {platformInfo.name}
                    </span>
                )}
             </div>
          </div>

          {/* Input */}
          <input
            ref={inputRef}
            type="text"
            value={inputUrl}
            onChange={(e) => setInputUrl(e.target.value)}
            onPaste={handlePaste}
            placeholder="Paste your link here..."
            disabled={isLoading}
            className="flex-1 bg-transparent py-4 px-3 text-text-primary placeholder:text-text-muted focus:outline-none text-base font-medium"
            autoComplete="off"
            spellCheck="false"
          />

          {/* Action Buttons */}
          <div className="flex items-center gap-2 pl-2 pr-1">
            {inputUrl && !isLoading && (
              <button
                type="button"
                onClick={handleClear}
                className="p-3 rounded-2xl text-text-muted hover:bg-bg-input hover:text-text-primary transition-all"
                title="Clear"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            )}

            <button
              type="submit"
              disabled={isLoading || !inputUrl.trim()}
              className="flex items-center justify-center px-8 py-3.5 sm:py-3 rounded-2xl btn-primary disabled:opacity-50"
            >
              {isLoading ? (
                <div className="flex items-center gap-3">
                    <svg className="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                        <path d="M21 12a9 9 0 11-6.219-8.56"/>
                    </svg>
                </div>
              ) : (
                <span className="font-bold tracking-wide">Analyze</span>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Supported platforms hint (Icons restored) */}
      <div className="flex flex-wrap items-center justify-center gap-6 px-4 py-2">
        {Object.entries(PLATFORMS).map(([key, p]) => (
            <div 
                key={key} 
                className={`flex items-center gap-2 text-[0.65rem] font-bold uppercase tracking-widest transition-all duration-300 ${detectedPlatform === key ? 'opacity-100 scale-110' : 'opacity-30'}`}
                style={{ color: detectedPlatform === key ? p.color : undefined }}
            >
                <PlatformIcon platform={key} className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">{p.name}</span>
            </div>
        ))}
      </div>
    </div>
  );
}
