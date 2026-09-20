import React, { useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useDownloader } from '../hooks/useDownloader';
import URLInput from '../components/URLInput';
import PreviewCard from '../components/PreviewCard';
import DownloadButtons from '../components/DownloadButtons';
import AnalyzeLoader from '../components/AnalyzeLoader';
import ErrorMessage from '../components/ErrorMessage';
import HistoryPanel from '../components/HistoryPanel';
import Header from '../components/Header';
import Footer from '../components/Footer';
import CaptionPanel from '../components/CaptionPanel';
import AdSlot from '../components/AdSlot';

// ── Ad slot IDs — replace with your real AdSense slot IDs ──
const AD_SLOTS = {
  topBanner:    process.env.REACT_APP_AD_SLOT_TOP    || '',
  bottomBanner: process.env.REACT_APP_AD_SLOT_BOTTOM || '',
};

export default function HomePage() {
  const { state, analyze, download, reset } = useDownloader();
  const { status, metadata, error, downloadingFormatId, downloadProgress } = state;

  const handleAnalyze   = useCallback((url) => analyze(url), [analyze]);
  const handleDownload  = useCallback((formatId, title) => download(formatId, title || metadata?.title || 'download'), [download, metadata]);
  const handleHistory   = useCallback((url) => analyze(url), [analyze]);
  const isLoading       = status === 'analyzing';
  const hasResult       = ['ready', 'downloading', 'error'].includes(status);

  return (
    <div className="min-h-screen bg-bg-page relative overflow-x-hidden">
      {/* Dynamic Background Elements */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-brand/5 blur-[120px] rounded-full animate-pulse-slow"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-brand/10 blur-[100px] rounded-full animate-pulse-slow" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6">
        
        {/* ── TOP BANNER AD ── */}
        <div className="pt-4 sm:pt-6">
          <AdSlot slot={AD_SLOTS.topBanner} style="banner" className="mb-4" />
        </div>

        <Header />

        <main className="space-y-12 pb-20">
            <URLInput
                onSubmit={handleAnalyze}
                isLoading={isLoading}
                onReset={reset}
                hasResult={hasResult}
            />

            {status === 'analyzing' && <AnalyzeLoader />}

            {status === 'error' && (
                <ErrorMessage error={error} code={state.errorCode} onDismiss={reset} />
            )}

            {(status === 'ready' || status === 'downloading') && metadata && (
                <div className="space-y-10 animate-fade-in">
                    <PreviewCard metadata={metadata} platform={metadata.platform} />

                    <DownloadButtons
                        formats={metadata.formats || []}
                        onDownload={handleDownload}
                        downloadingFormatId={downloadingFormatId}
                        downloadProgress={downloadProgress}
                        title={metadata.title}
                    />
                    <CaptionPanel metadata={metadata} url={state.url} />
                </div>
            )}

            <HistoryPanel onSelect={handleHistory} />

            <AdSlot slot={AD_SLOTS.bottomBanner} style="banner" />

            {status === 'idle' && <HowItWorks />}

            <MonetizationSection />

            <SEOContent />
        </main>

        <Footer />
      </div>
    </div>
  );
}

// ── How it works ──────────────────────────────────────────────
function HowItWorks() {
  const steps = [
    { num: '01', title: 'Paste Link',  desc: 'Copy the URL from YouTube, Instagram, or TikTok.', icon: '🔗' },
    { num: '02', title: 'Quick Analysis',    desc: 'Our AI extracts the best quality formats for you.', icon: '⚡' },
    { num: '03', title: 'Save Media',   desc: 'Download your file in HD — fast and free.', icon: '💾' },
  ];

  const platforms = [
    { name: 'YouTube',   color: '#ef4444', items: ['Videos & Shorts', 'MP3 High Quality'] },
    { name: 'Instagram', color: '#ec4899', items: ['Reels & Posts', 'Carousels (All Slides)'] },
    { name: 'TikTok',    color: '#06b6d4', items: ['Videos (No Watermark)', 'Audios'] },
    { name: 'Facebook',  color: '#3b82f6', items: ['HD/SD Reels', 'Watch Videos'] },
    { name: 'Pinterest', color: '#ef4444', items: ['Image Pins', 'Video Pins'] },
  ];

  return (
    <div className="space-y-16 py-8">
      <div className="space-y-6">
        <SectionTitle>Seamless Experience</SectionTitle>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {steps.map(step => (
            <div key={step.num} className="premium-card p-8 group hover:border-brand/50 transition-all duration-500">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-bg-input border border-border-color text-2xl mb-6 group-hover:scale-110 group-hover:bg-brand/10 transition-all duration-500">
                    {step.icon}
                </div>
                <h3 className="text-lg font-bold text-text-primary mb-3">{step.title}</h3>
                <p className="text-sm text-text-secondary leading-relaxed font-medium">{step.desc}</p>
                <div className="mt-4 text-[0.65rem] font-black text-brand uppercase tracking-[0.2em]">Step {step.num}</div>
            </div>
            ))}
        </div>
      </div>

      <div className="space-y-6">
        <SectionTitle>Supported Formats</SectionTitle>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {platforms.map(p => (
            <div key={p.name} className="premium-card p-4 hover:border-brand/30 transition-all">
                <div className="flex items-center gap-2 mb-3">
                    <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
                    <span className="font-bold text-[0.7rem] uppercase tracking-wider" style={{ color: p.color }}>{p.name}</span>
                </div>
                <ul className="space-y-1.5">
                    {p.items.map(item => (
                        <li key={item} className="text-[0.6rem] text-text-muted font-bold flex items-center gap-1.5 opacity-60">
                            <span className="text-brand">→</span> {item}
                        </li>
                    ))}
                </ul>
            </div>
            ))}
        </div>
      </div>

      <div className="text-center">
        <Link to="/faq" className="inline-flex items-center gap-2 text-sm font-semibold text-brand hover:text-brand-hover transition-colors">
            Read the full FAQ
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
        </Link>
      </div>
    </div>
  );
}

// ── Monetization (donation + affiliate) ──────────────────────
function MonetizationSection() {
  return (
    <div className="premium-card p-10 text-center border-brand/10 bg-brand/[0.02]">
      <div className="max-w-xl mx-auto space-y-8">
        <div className="space-y-2">
            <h3 className="text-2xl font-black text-text-primary tracking-tight">Support ClipGrabber</h3>
            <p className="text-sm text-text-secondary font-medium">
                Our service is free and always will be. Small donations help us keep the servers running and ad-free in the future.
            </p>
        </div>
        
        <div className="flex flex-wrap items-center justify-center gap-4">
            <a href="https://buymeacoffee.com/REPLACE_WITH_YOUR_NAME" target="_blank" rel="noreferrer"
            className="flex items-center gap-3 px-8 py-4 rounded-2xl text-sm font-black transition-all hover:scale-105 active:scale-95 bg-[#FFDD00] text-black shadow-lg shadow-yellow-500/20">
            ☕ Buy me a coffee
            </a>
            <a href="https://ko-fi.com/REPLACE_WITH_YOUR_NAME" target="_blank" rel="noreferrer"
            className="flex items-center gap-3 px-8 py-4 rounded-2xl text-sm font-black transition-all hover:scale-105 active:scale-95 bg-bg-card border-2 border-border-color text-text-primary hover:border-brand/50">
            💙 Support on Ko-fi
            </a>
            <a href="https://www.linkedin.com/in/mudassar-rehman-2558253b2" target="_blank" rel="noreferrer"
            className="flex items-center gap-3 px-8 py-4 rounded-2xl text-sm font-black transition-all hover:scale-105 active:scale-95 bg-[#0077B5] text-white shadow-lg shadow-blue-500/20">
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
            Connect on LinkedIn
            </a>
        </div>

      </div>
    </div>
  );
}

// ── SEO content block ─────────────────────────────────────────
function SEOContent() {
  return (
    <article className="py-12 px-6 sm:px-12 premium-card border-none bg-transparent">
      <SectionTitle>Advanced Media Downloader</SectionTitle>
      <div className="mt-8 space-y-6 text-sm text-text-secondary font-medium leading-relaxed max-w-3xl mx-auto">
        <p>
          <strong className="text-text-primary underline decoration-brand/30 decoration-2 underline-offset-4">ClipGrabber</strong> is a high-performance, professional-grade social media toolkit designed for creators, marketers, and power users. We provide a seamless gateway to save visual and auditory inspiration from the world's leading platforms including YouTube, Instagram, TikTok, Facebook, and Pinterest.
        </p>
        <div className="grid sm:grid-cols-2 gap-8 py-4">
            <div className="space-y-3">
                <h4 className="font-black text-text-primary flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-brand"></span>
                    Quality First
                </h4>
                <p className="text-xs opacity-80">We prioritize 4K and 1080p source retrieval, ensuring that what you save is exactly what the creator intended to show. No compression artifacts or resolution downscaling when possible.</p>
            </div>
            <div className="space-y-3">
                <h4 className="font-black text-text-primary flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-brand"></span>
                    Privacy Focused
                </h4>
                <p className="text-xs opacity-80">Your data belongs to you. We don't track your downloads, we don't store your personal IP logs, and all processed files are purged from our RAM-based cycles immediately after download.</p>
            </div>
        </div>
        <p className="text-xs italic bg-bg-input/50 p-4 rounded-xl border-l-4 border-brand">
            ClipGrabber operates with high respect for intellectual property rights. Please use this tool for personal use and backup purposes only. Always credit creators when re-sharing content.
        </p>
      </div>
    </article>
  );
}


// ── Shared UI Utilities ───────────────────────────────────────

function SectionTitle({ children }) {
  return (
    <div className="flex items-center gap-4">
      <span className="text-[0.65rem] font-black text-brand uppercase tracking-[0.3em] whitespace-nowrap">{children}</span>
      <div className="h-px w-full bg-gradient-to-r from-brand/20 to-transparent" />
    </div>
  );
}
