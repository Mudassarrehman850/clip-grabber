import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="relative z-10 py-16 mt-16 border-t border-border-color">
      <div className="max-w-4xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-center">

          <div className="space-y-4 text-center md:text-left">
            <div className="text-2xl font-display font-bold tracking-tight text-text-primary">
              Clip<span className="text-brand">Grabber</span>
            </div>
            <p className="text-xs font-medium text-text-muted leading-relaxed max-w-sm mx-auto md:mx-0">
              A free, no-signup toolkit for saving publicly available media from YouTube, Instagram, TikTok,
              Facebook, and Pinterest.
            </p>
          </div>

          <div className="space-y-6 text-center md:text-right">
            <div className="flex flex-wrap items-center justify-center md:justify-end gap-x-6 gap-y-2 text-[0.7rem] font-semibold text-text-secondary uppercase tracking-widest">
              <Link to="/about" className="hover:text-brand transition-colors">About</Link>
              <Link to="/faq" className="hover:text-brand transition-colors">FAQ</Link>
              <Link to="/terms" className="hover:text-brand transition-colors">Terms of Service</Link>
              <Link to="/privacy" className="hover:text-brand transition-colors">Privacy Policy</Link>
              <Link to="/contact" className="hover:text-brand transition-colors">Contact</Link>
            </div>

            <p className="text-[0.65rem] font-medium text-text-muted opacity-70">
              © {currentYear} ClipGrabber. Not affiliated with TikTok, Instagram, YouTube, Facebook, or Pinterest.
            </p>
          </div>

        </div>
      </div>
    </footer>
  );
}
