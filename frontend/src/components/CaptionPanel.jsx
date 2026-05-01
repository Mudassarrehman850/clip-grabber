import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// ── Icons ──────────────────────────────────────────
const CopyIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
    </svg>
);
const CheckIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="20 6 9 17 4 12"/>
    </svg>
);
const ExportIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
    </svg>
);
const HashIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
        <line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/>
        <line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/>
    </svg>
);
const AtIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
        <circle cx="12" cy="12" r="4"/><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-3.92 7.94"/>
    </svg>
);
const ClockIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
        <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
    </svg>
);
const LinkIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
    </svg>
);

// ── Pill component ─────────────────────────────────
function Pill({ children, color, onClick }) {
  return (
    <span
      onClick={onClick}
      className="inline-flex items-center px-3 py-1 rounded-lg text-[0.65rem] font-bold cursor-pointer transition-all duration-200 hover:scale-105 active:scale-95 border"
      style={{ background: `${color}10`, color, borderColor: `${color}30` }}
    >
      {children}
    </span>
  );
}

// ── Section ────────────────────────────────────────
function Section({ icon, title, count, children, accentColor }) {
  const [open, setOpen] = useState(false);
  if (!count) return null;
  return (
    <div className="border-t border-border-color">
      <button
        onClick={() => setOpen(v => !v)}
        className="w-full flex items-center justify-between px-6 py-4 text-[0.65rem] font-black uppercase tracking-[0.2em] transition-all hover:bg-bg-input group"
        style={{ color: open ? accentColor : 'var(--text-muted)' }}
      >
        <span className="flex items-center gap-3">
          <span style={{ color: accentColor }}>{icon}</span>
          {title}
          <span className="font-mono opacity-40 lowercase tracking-normal">({count})</span>
        </span>
        <svg  width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"
            className={`transition-transform duration-300 ${open ? 'rotate-180 text-brand' : 'opacity-40'}`}>
            <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button>
      {open && (
        <div className="px-6 pb-6 animate-fade-in">
          {children}
        </div>
      )}
    </div>
  );
}

// ── Copy button ────────────────────────────────────
function CopyButton({ text, label = 'Copy', minimal = false }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* ignore */ }
  };

  if (minimal) {
      return (
        <button onClick={handleCopy} className={`p-1.5 rounded-md transition-all ${copied ? 'text-success' : 'text-text-muted hover:text-text-primary hover:bg-bg-input'}`}>
             {copied ? <CheckIcon /> : <CopyIcon />}
        </button>
      )
  }

  return (
    <button
      onClick={handleCopy}
      className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-[0.65rem] font-bold uppercase tracking-wider transition-all border ${copied ? 'bg-success/10 border-success/30 text-success' : 'bg-bg-input border-border-color text-text-secondary hover:border-brand/40 hover:text-brand'}`}
    >
      {copied ? <CheckIcon /> : <CopyIcon />}
      {copied ? 'Copied' : label}
    </button>
  );
}

// ── Main CaptionPanel ──────────────────────────────
export default function CaptionPanel({ metadata, url }) {
  const [exporting, setExporting] = useState(false);
  const [showFull, setShowFull] = useState(false);

  const caption = metadata?.caption;
  if (!caption && !metadata?.description) return null;

  const fullText = caption?.full_text || metadata?.description || '';
  const hashtags = caption?.hashtags || [];
  const mentions = caption?.mentions || [];
  const chapters = caption?.chapters || [];
  const links = caption?.urls || [];
  const wordCount = caption?.word_count || 0;
  const charCount = caption?.char_count || fullText.length;

  const hasContent = fullText || hashtags.length || mentions.length || chapters.length;
  if (!hasContent) return null;

  const PREVIEW_LENGTH = 300;
  const isLong = fullText.length > PREVIEW_LENGTH;
  const displayText = isLong && !showFull ? fullText.slice(0, PREVIEW_LENGTH) + '...' : fullText;

  const renderRichText = (text) => {
    const parts = text.split(/(#\w+|@[\w.]+|https?:\/\/[^\s]+)/g);
    return parts.map((part, i) => {
      if (part.startsWith('#')) return <span key={i} className="text-brand font-bold">{part}</span>;
      if (part.startsWith('@')) return <span key={i} className="text-indigo-400 font-bold">{part}</span>;
      if (part.startsWith('http')) return <a key={i} href={part} target="_blank" rel="noreferrer" className="text-brand underline decoration-brand/30 hover:text-brand-hover">{part}</a>;
      return <span key={i}>{part}</span>;
    });
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const resp = await axios.post(`${API_BASE}/api/caption/export`, { url }, { responseType: 'blob' });
      const blobUrl = window.URL.createObjectURL(resp.data);
      const a = document.createElement('a');
      a.href = blobUrl;
      const cd = resp.headers['content-disposition'] || '';
      const match = cd.match(/filename="?([^"]+)"?/);
      a.download = match ? match[1] : 'caption.txt';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(blobUrl);
    } catch { /* ignore */ }
    setExporting(false);
  };

  return (
    <div className="w-full max-w-2xl mx-auto mt-10 premium-card overflow-hidden animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-bg-input/30 border-b border-border-color">
        <div className="flex items-center gap-3">
          <span className="text-[0.65rem] font-black uppercase tracking-[0.2em] text-text-muted">Content Assets</span>
          {(wordCount > 0 || charCount > 0) && (
            <div className="h-4 w-px bg-border-color"></div>
          )}
          <span className="text-[0.65rem] font-bold text-text-muted/60 font-mono">
            {wordCount > 0 && `${wordCount}W`}
            {wordCount > 0 && charCount > 0 && ' · '}
            {charCount > 0 && `${charCount}C`}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <CopyButton text={fullText} label="Copy Text" />
          <button
            onClick={handleExport}
            disabled={exporting}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-[0.65rem] font-bold uppercase tracking-wider transition-all border bg-bg-card border-border-color text-text-secondary hover:border-brand/40 hover:text-brand disabled:opacity-40"
          >
            <ExportIcon />
            {exporting ? '...' : '.TXT'}
          </button>
        </div>
      </div>

      {/* Caption Content */}
      <div className="p-6">
        {fullText ? (
          <div className="space-y-4">
            <div className="rounded-2xl bg-bg-input/50 p-5 border border-border-color/50">
                <p className="text-sm text-text-primary font-medium leading-[1.8] whitespace-pre-line break-words">
                    {renderRichText(displayText)}
                </p>
            </div>
            {isLong && (
              <button
                onClick={() => setShowFull(v => !v)}
                className="w-full py-3 text-[0.65rem] font-black uppercase tracking-[0.2em] text-brand hover:text-brand-hover transition-colors rounded-xl border border-brand/10 hover:bg-brand/5"
              >
                {showFull ? 'Show Less' : `Read Full Caption (+${charCount - PREVIEW_LENGTH} characters)`}
              </button>
            )}
          </div>
        ) : (
          <div className="text-center py-8 px-4 rounded-2xl border-2 border-dashed border-border-color/50">
             <p className="text-xs font-bold text-text-muted uppercase tracking-widest">No caption found for this media</p>
          </div>
        )}
      </div>

      {/* Metadata Sections */}
      <div className="bg-bg-input/10">
          <Section icon={<HashIcon />} title="Hashtags" count={hashtags.length} accentColor="var(--brand)">
            <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                    {hashtags.map((tag, i) => (
                        <Pill key={i} color="var(--brand)" onClick={() => navigator.clipboard.writeText(`#${tag}`)}>
                        #{tag}
                        </Pill>
                    ))}
                </div>
                {hashtags.length > 1 && (
                <div className="flex justify-start">
                    <CopyButton text={hashtags.map(t => `#${t}`).join(' ')} label="Copy All Hashtags" />
                </div>
                )}
            </div>
          </Section>

          <Section icon={<AtIcon />} title="Mentions" count={mentions.length} accentColor="#818cf8">
            <div className="flex flex-wrap gap-2">
              {mentions.map((m, i) => (
                <Pill key={i} color="#818cf8" onClick={() => navigator.clipboard.writeText(`@${m}`)}>
                  @{m}
                </Pill>
              ))}
            </div>
          </Section>

          <Section icon={<ClockIcon />} title="Timeline Chapters" count={chapters.length} accentColor="#f59e0b">
            <div className="grid gap-2">
              {chapters.map((ch, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-bg-card border border-border-color hover:border-brand/30 transition-all group">
                  <div className="flex items-center gap-4">
                    <span className="font-mono text-xs font-bold text-brand">{ch.start_time_str}</span>
                    <span className="text-xs font-bold text-text-secondary group-hover:text-text-primary transition-colors">{ch.title}</span>
                  </div>
                  <CopyButton text={ch.start_time_str} minimal />
                </div>
              ))}
            </div>
          </Section>

          <Section icon={<LinkIcon />} title="Extracted Links" count={links.length} accentColor="#10b981">
            <div className="grid gap-2">
              {links.map((link, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-bg-card border border-border-color hover:border-brand/30 transition-all group overflow-hidden">
                  <a href={link} target="_blank" rel="noreferrer" className="text-xs font-bold text-brand truncate hover:underline flex-1 pr-4">
                    {link}
                  </a>
                  <CopyButton text={link} minimal />
                </div>
              ))}
            </div>
          </Section>
      </div>
    </div>
  );
}
