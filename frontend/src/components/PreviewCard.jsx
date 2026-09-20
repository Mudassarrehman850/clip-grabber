import React, { useState } from 'react';
import { PLATFORMS, formatNumber, formatDate } from '../utils/helpers';

const API_BASE = process.env.REACT_APP_API_URL || '';

function resolveThumbnail(url) {
  if (!url) return null;
  if (url.startsWith('/api/')) return `${API_BASE}${url}`;
  return url;
}

// ── Icons ──────────────────────────────────────────────────────────────────

const PlatformIcon = ({ platform, className = "w-10 h-10" }) => {
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

const VideoIcon = ({ className = "w-4 h-4" }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/>
    </svg>
);

const ImageIcon = ({ className = "w-4 h-4" }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
    </svg>
);

// ── Components ─────────────────────────────────────────────────────────────

const PlatformBadge = ({ platform, contentType }) => {
  const info = PLATFORMS[platform] || {};
  const labels = {
    video: 'Video', short: 'Short', reel: 'Reel',
    post: 'Post', tv: 'IGTV', profile: 'Profile', carousel: 'Carousel',
  };
  return (
    <div className="flex items-center gap-2 flex-wrap mb-1">
      <span className={`badge ${info.bgClass || ''} flex items-center gap-1.5`}>
        <PlatformIcon platform={platform} className="w-3 h-3" />
        {info.name}
      </span>
      {contentType && (
        <span className="badge bg-bg-input border-border-color text-text-secondary">
          {labels[contentType] || contentType}
        </span>
      )}
    </div>
  );
};

const Stat = ({ icon, value, label }) => {
  if (!value && value !== 0) return null;
  return (
    <div className="flex items-center gap-1.5 text-xs text-text-muted">
      <span className="text-sm">{icon}</span>
      <span className="font-semibold text-text-secondary">{value}</span>
      {label && <span>{label}</span>}
    </div>
  );
};

export default function PreviewCard({ metadata, platform }) {
  const [imgErr, setImgErr] = useState(false);
  const platformInfo = PLATFORMS[platform] || {};

  const isCarousel  = metadata.is_carousel || metadata.content_type === 'carousel';
  const slideCount  = metadata.slide_count || 1;
  const thumbSrc    = resolveThumbnail(metadata.thumbnail);

  return (
    <div className="w-full max-w-2xl mx-auto mt-8 premium-card overflow-hidden animate-fade-in">
      <div className="flex flex-col sm:flex-row gap-6 p-5 sm:p-6">
        
        {/* Thumbnail Section */}
        <div className="relative group flex-shrink-0">
          <div className="w-full sm:w-44 h-44 sm:h-44 rounded-2xl overflow-hidden bg-bg-input border border-border-color shadow-inner">
            {thumbSrc && !imgErr ? (
              <img
                src={thumbSrc}
                alt={metadata.title}
                onError={() => setImgErr(true)}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                crossOrigin="anonymous"
                loading="lazy"
                width={176}
                height={176}
              />
            ) : (
                <div className="w-full h-full flex flex-col items-center justify-center opacity-20"
                    style={{ background: platformInfo.color || 'var(--brand)' }}>
                    <PlatformIcon platform={platform} className="w-12 h-12" />
                </div>
            )}
            
            {/* Duration / Carousel Badges */}
            <div className="absolute bottom-3 right-3 flex flex-col gap-2">
                {metadata.duration && (
                    <div className="px-2 py-1 bg-black/80 backdrop-blur-md text-white text-[0.6rem] font-bold rounded-lg shadow-lg">
                        {metadata.duration}
                    </div>
                )}
                {isCarousel && (
                    <div className="px-2 py-1 bg-brand text-white text-[0.6rem] font-bold rounded-lg shadow-lg flex items-center gap-1">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
                            <rect x="3" y="3" width="7" height="18" rx="1"/><rect x="14" y="3" width="7" height="18" rx="1"/>
                        </svg>
                        {slideCount}
                    </div>
                )}
            </div>
          </div>
          
          <div className="absolute -inset-2 bg-brand/5 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10"></div>
        </div>

        {/* Content Section */}
        <div className="flex-1 flex flex-col min-w-0">
          <PlatformBadge platform={platform} contentType={metadata.content_type} />
          
          <h3 className="text-xl font-bold text-text-primary leading-tight line-clamp-2 mt-1 mb-3" title={metadata.title}>
            {metadata.title || 'Untitled Content'}
          </h3>

          {metadata.uploader && metadata.uploader !== 'Unknown' && (
            <div className="flex items-center gap-3 mb-4 group cursor-default">
              <div className="w-10 h-10 rounded-full flex items-center justify-center overflow-hidden bg-brand/10 text-brand border border-brand/20">
                <span className="text-sm font-black uppercase">{(metadata.uploader[0] || '?')}</span>
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-bold text-text-primary group-hover:text-brand transition-colors">@{metadata.uploader}</span>
                <span className="text-[0.65rem] text-text-muted font-black uppercase tracking-widest">Channel / Profile</span>
              </div>
            </div>
          )}

          <div className="flex flex-wrap items-center gap-4 mt-auto pt-4 border-t border-border-color/50">
            <Stat icon="👁️" value={formatNumber(metadata.view_count)} label="Views" />
            <Stat icon="❤️" value={formatNumber(metadata.like_count)} label="Likes" />
            <Stat icon="📅" value={formatDate(metadata.upload_date)} />
          </div>
        </div>
      </div>

      {/* Description */}
      {metadata.description && (
        <div className="px-6 py-4 bg-bg-input/10 border-t border-border-color/50">
            <p className="text-xs text-text-secondary leading-relaxed line-clamp-3 italic">
                {metadata.description}
            </p>
        </div>
      )}

      {/* Slide Strip for Carousels */}
      {isCarousel && metadata.slides && metadata.slides.length > 1 && (
        <div className="bg-bg-input/20 p-6 border-t border-border-color">
            <div className="flex items-center justify-between mb-4">
                <h4 className="text-[0.65rem] font-black text-text-muted uppercase tracking-[0.3em]">Individual Slides</h4>
                <div className="h-px flex-1 mx-4 bg-border-color/50" />
                <span className="text-[0.6rem] font-black px-2 py-0.5 rounded bg-bg-card border border-border-color text-text-secondary">
                    {metadata.slides.length} SLIDES
                </span>
            </div>
            <div className="flex gap-3 overflow-x-auto pb-4 custom-scrollbar">
                {metadata.slides.map((slide, i) => (
                    <SlideThumbnail key={i} slide={slide} index={i} platformColor={platformInfo.color} />
                ))}
            </div>
        </div>
      )}
    </div>
  );
}

function SlideThumbnail({ slide, index, platformColor }) {
  const [err, setErr] = useState(false);
  const src = resolveThumbnail(slide.thumbnail);

  return (
    <div className="flex-shrink-0 relative group">
      <div className="w-24 h-24 rounded-2xl overflow-hidden bg-bg-input border-2 border-transparent group-hover:border-brand transition-all shadow-md">
        {src && !err ? (
          <img
            src={src}
            alt={`Slide ${index + 1}`}
            onError={() => setErr(true)}
            className="w-full h-full object-cover transition-transform group-hover:scale-110"
            crossOrigin="anonymous"
            loading="lazy"
            width={96}
            height={96}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-xl bg-brand/5" style={{ color: platformColor }}>
            {slide.type === 'video' ? <VideoIcon className="w-6 h-6" /> : <ImageIcon className="w-6 h-6" />}
          </div>
        )}
        
        {slide.type === 'video' && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/10">
                <div className="w-8 h-8 rounded-full bg-white/30 backdrop-blur-sm flex items-center justify-center shadow-lg">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="white">
                        <polygon points="5 3 19 12 5 21 5 3"/>
                    </svg>
                </div>
            </div>
        )}
      </div>
      
      <div className="absolute top-2 left-2 w-6 h-6 rounded-lg bg-black/50 backdrop-blur-md border border-white/20 flex items-center justify-center text-[0.65rem] font-black text-white shadow-sm">
        {index + 1}
      </div>
    </div>
  );
}
