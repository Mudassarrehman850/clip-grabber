import React, { useEffect } from 'react';

export default function Modal({ isOpen, onClose, title, children }) {
  // Handle escape key to close
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleEsc);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleEsc);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-[1000] flex items-center justify-center p-4 sm:p-6 animate-fade-in"
      aria-modal="true"
      role="dialog"
    >
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-all"
        onClick={onClose}
      />

      {/* Modal Content */}
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-hidden rounded-3xl premium-card border-brand/20 bg-bg-card shadow-2xl animate-scale-up">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-border-color bg-bg-input/30">
          <h3 className="text-[0.65rem] font-black uppercase tracking-[0.3em] text-brand">
            {title}
          </h3>
          <button 
            onClick={onClose}
            className="p-2 rounded-xl text-text-muted hover:bg-bg-input hover:text-brand transition-all"
            aria-label="Close"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="overflow-y-auto p-8 custom-scrollbar max-h-[calc(90vh-80px)]">
          <div className="prose prose-sm dark:prose-invert max-w-none text-text-secondary font-medium leading-[1.8]">
            {children}
          </div>
        </div>

        {/* Footer/Gradient Blur */}
        <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-bg-card to-transparent pointer-events-none" />
      </div>
    </div>
  );
}
