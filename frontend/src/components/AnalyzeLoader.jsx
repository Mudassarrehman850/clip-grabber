import React from 'react';

export default function AnalyzeLoader() {
  return (
    <div className="w-full max-w-2xl mx-auto mt-8 animate-fade-in">
      <div className="premium-card p-6 overflow-hidden bg-bg-card/50">
        <div className="flex flex-col sm:flex-row gap-6">
          {/* Thumbnail skeleton */}
          <div className="flex-shrink-0 w-full sm:w-44 h-44 rounded-2xl bg-bg-input animate-pulse" />
          
          {/* Info skeleton */}
          <div className="flex-1 space-y-4 py-2">
            <div className="flex gap-2">
                <div className="h-5 w-20 bg-bg-input rounded-full animate-pulse" />
                <div className="h-5 w-16 bg-bg-input rounded-full animate-pulse" />
            </div>
            <div className="h-7 w-[90%] bg-bg-input rounded-xl animate-pulse" />
            <div className="h-7 w-[60%] bg-bg-input rounded-xl animate-pulse" />
            
            <div className="pt-4 flex items-center gap-3">
                <div className="h-10 w-10 bg-bg-input rounded-full animate-pulse" />
                <div className="space-y-1">
                    <div className="h-3 w-20 bg-bg-input rounded-lg animate-pulse" />
                    <div className="h-3 w-12 bg-bg-input rounded-lg animate-pulse" />
                </div>
            </div>

            <div className="flex gap-3 mt-auto pt-4 border-t border-border-color">
                <div className="h-4 w-16 bg-bg-input rounded-lg animate-pulse" />
                <div className="h-4 w-16 bg-bg-input rounded-lg animate-pulse" />
            </div>
          </div>
        </div>
      </div>

      {/* Status text */}
      <div className="flex items-center justify-center gap-3 mt-6">
        <svg className="animate-spin text-brand" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
          <path d="M21 12a9 9 0 11-6.219-8.56"/>
        </svg>
        <span className="text-[0.65rem] font-black uppercase tracking-[0.2em] text-text-muted">Extracting HD Media Info...</span>
      </div>
    </div>
  );
}
