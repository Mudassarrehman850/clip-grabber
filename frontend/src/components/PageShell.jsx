import React from 'react';
import SiteNav from './SiteNav';
import Footer from './Footer';

export default function PageShell({ title, subtitle, children }) {
  return (
    <div className="min-h-screen bg-bg-page">
      <div className="max-w-3xl mx-auto px-4 sm:px-6">
        <SiteNav />
        <main className="pb-20">
          <header className="py-10 sm:py-14 text-center space-y-3">
            <h1 className="text-3xl sm:text-4xl font-display font-bold tracking-tight text-text-primary">{title}</h1>
            {subtitle && <p className="text-sm sm:text-base text-text-secondary max-w-xl mx-auto">{subtitle}</p>}
          </header>
          <article className="premium-card p-6 sm:p-10 space-y-6 text-sm text-text-secondary leading-relaxed">
            {children}
          </article>
        </main>
        <Footer />
      </div>
    </div>
  );
}
