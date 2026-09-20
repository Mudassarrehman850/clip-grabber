import React from 'react';
import { Link } from 'react-router-dom';
import ThemeToggle from './ThemeToggle';

const PlatformPill = ({ name, color, icon }) => (
  <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[0.65rem] font-semibold border transition-all duration-300 hover:scale-105"
    style={{ 
        background: `var(--bg-card)`, 
        borderColor: `var(--border-color)`,
        color: color 
    }}>
    {icon}
    {name}
  </span>
);

export default function Header() {
  return (
    <header className="relative pt-12 pb-10 sm:pt-16 sm:pb-12 text-center overflow-visible">
      
      {/* Controls: nav links, theme toggle */}
      <div className="absolute top-4 right-0 sm:top-6 flex items-center gap-4">
        <div className="hidden sm:flex items-center gap-4 text-xs font-semibold text-text-secondary uppercase tracking-wider">
          <Link to="/about" className="hover:text-brand transition-colors">About</Link>
          <Link to="/faq" className="hover:text-brand transition-colors">FAQ</Link>
        </div>
        <ThemeToggle />
      </div>

      <div className="flex flex-col items-center justify-center space-y-6">
        {/* Logo Container */}
        <div className="relative group">
          <div className="absolute -inset-4 bg-gradient-to-r from-brand to-indigo-400 rounded-3xl opacity-20 blur-2xl group-hover:opacity-30 transition duration-500"></div>
          <div className="relative w-16 h-16 sm:w-20 sm:h-20 flex items-center justify-center rounded-2xl bg-bg-card border border-border-color shadow-xl">
            <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="var(--brand)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </div>
        </div>

        <div className="space-y-3">
          <h1 className="text-4xl sm:text-6xl font-bold tracking-tight text-text-primary">
            Clip<span className="text-brand">Grabber</span>
          </h1>
          <p className="max-w-md mx-auto text-sm sm:text-base text-text-secondary font-medium leading-relaxed">
            The professional way to save your favorite social media content. Fast, free, and secure.
          </p>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
          <PlatformPill name="YouTube" color="#ef4444" />
          <PlatformPill name="Instagram" color="#ec4899" />
          <PlatformPill name="TikTok" color="#06b6d4" />
          <PlatformPill name="Facebook" color="#3b82f6" />
          <PlatformPill name="Pinterest" color="#ef4444" />
        </div>
      </div>
    </header>
  );
}
