import React from 'react';
import { Link } from 'react-router-dom';
import ThemeToggle from './ThemeToggle';

export default function SiteNav() {
  return (
    <nav className="flex items-center justify-between py-6">
      <Link to="/" className="text-xl font-display font-bold tracking-tight text-text-primary">
        Clip<span className="text-brand">Grabber</span>
      </Link>
      <div className="flex items-center gap-5">
        <Link to="/about" className="text-xs font-semibold text-text-secondary hover:text-brand transition-colors uppercase tracking-wider">About</Link>
        <Link to="/faq" className="text-xs font-semibold text-text-secondary hover:text-brand transition-colors uppercase tracking-wider">FAQ</Link>
        <Link to="/contact" className="text-xs font-semibold text-text-secondary hover:text-brand transition-colors uppercase tracking-wider">Contact</Link>
        <ThemeToggle />
      </div>
    </nav>
  );
}
