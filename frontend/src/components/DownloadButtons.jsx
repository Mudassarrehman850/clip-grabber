import React, { useState } from 'react';

// ── Icons ──────────────────────────────────────────────────────────────────
const VideoIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/>
    </svg>
);
const AudioIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
    </svg>
);
const ImageIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
        <polyline points="21 15 16 10 5 21"/>
    </svg>
);
const ZipIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
);
const DownIcon = () => (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
    </svg>
);

const SpinIcon = () => (
    <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
        <path d="M21 12a9 9 0 11-6.219-8.56"/>
    </svg>
);

const TYPE_ICONS = { video: <VideoIcon />, audio: <AudioIcon />, image: <ImageIcon />, archive: <ZipIcon /> };

// ── Single button ──────────────────────────────────────────────────────────
function DLButton({ format, onDownload, isDownloading, isDisabled, downloadProgress }) {
    
    const isVideo = format.type === 'video';
    const isAudio = format.type === 'audio';
    const isArchive = format.type === 'archive';

    const accentClass = isVideo ? 'text-brand' : isAudio ? 'text-success' : isArchive ? 'text-indigo-400' : 'text-text-primary';

    return (
        <button
            onClick={() => !isDisabled && onDownload(format.id)}
            disabled={isDisabled}
            className={`group relative flex items-center justify-between w-full px-5 py-4 rounded-2xl border border-border-color bg-bg-card hover:border-brand/40 hover:bg-bg-input transition-all duration-300 shadow-sm hover:shadow-md ${isDisabled && !isDownloading ? 'opacity-30 grayscale' : 'hover:-translate-y-1'}`}
        >
            {isDownloading && downloadProgress > 0 && (
                <div 
                    className="absolute inset-x-0 bottom-0 top-0 bg-brand/10 transition-all duration-500 rounded-2xl"
                    style={{ width: `${downloadProgress}%` }}
                />
            )}

            <div className="relative flex items-center gap-3">
                <div className={`flex-shrink-0 ${accentClass}`}>
                    {isDownloading ? <SpinIcon /> : (TYPE_ICONS[format.type] || <VideoIcon />)}
                </div>
                <div className="flex flex-col items-start leading-tight">
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-bold tracking-tight text-text-primary">
                            {isDownloading 
                                ? (downloadProgress > 0 ? `${downloadProgress}%` : 'Preparing...') 
                                : format.label}
                        </span>
                    </div>
                    {format.size && !isDownloading && (
                        <span className="text-[0.6rem] font-black uppercase tracking-widest opacity-40">{format.size}</span>
                    )}
                </div>
            </div>

            {!isDownloading && (
                <div className="flex-shrink-0 text-text-muted group-hover:text-brand transition-colors">
                    <DownIcon />
                </div>
            )}
        </button>
    );
}

// ── Main export ────────────────────────────────────────────────────────────
export default function DownloadButtons({ formats, onDownload, downloadingFormatId, downloadProgress, title, webpage_url }) {
    const [showQR, setShowQR] = useState(false);

    if (!formats || formats.length === 0) return null;

    const isAnyDownloading = !!downloadingFormatId;
    const mainFormats = formats.filter(f => !f.id?.startsWith('slide_'));
    const slideFormats = formats.filter(f => f.id && f.id.startsWith('slide_'));

    // QR Encoding for mobile download
    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(webpage_url || window.location.href)}&bgcolor=ffffff&color=111111`;

    return (
        <div className="w-full max-w-2xl mx-auto mt-10 space-y-10 animate-fade-in px-2">
            
            {/* Download Grid */}
            <div className="space-y-6">
                <div className="flex items-center gap-4">
                    <h3 className="text-[0.65rem] font-black text-brand uppercase tracking-[0.3em] whitespace-nowrap">Extraction Results</h3>
                    <div className="h-px w-full bg-gradient-to-r from-brand/20 to-transparent"></div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {mainFormats.map((f) => (
                        <DLButton 
                            key={f.id} 
                            format={f} 
                            onDownload={(id) => onDownload(id, title)}
                            isDownloading={downloadingFormatId === f.id}
                            isDisabled={isAnyDownloading}
                            downloadProgress={downloadingFormatId === f.id ? downloadProgress : 0} 
                        />
                    ))}
                </div>
            </div>

            {/* Slides Section */}
            {slideFormats.length > 0 && (
                <div className="space-y-6">
                    <div className="flex items-center gap-4">
                        <h3 className="text-[0.65rem] font-black text-text-muted uppercase tracking-[0.3em] whitespace-nowrap">Individual Slides</h3>
                        <div className="h-px w-full bg-gradient-to-r from-border-color/30 to-transparent"></div>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {slideFormats.map(f => (
                            <DLButton 
                                key={f.id} 
                                format={f} 
                                onDownload={(id) => onDownload(id, title)}
                                isDownloading={downloadingFormatId === f.id}
                                isDisabled={isAnyDownloading}
                                downloadProgress={downloadingFormatId === f.id ? downloadProgress : 0} 
                            />
                        ))}
                    </div>
                </div>
            )}

            {/* Extra Feature Section: QR Code */}
            <div className={`p-8 rounded-[2.5rem] bg-bg-card border-2 transition-all duration-500 ${showQR ? 'border-brand shadow-2xl scale-[1.02]' : 'border-border-color hover:border-brand/30 shadow-lg hover:shadow-xl'}`}>
                <div className="flex flex-col sm:flex-row items-center gap-8">
                    <div className="flex-1 text-center sm:text-left space-y-3">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand/10 border border-brand/20">
                            <span className="w-2 h-2 rounded-full bg-brand animate-pulse"></span>
                            <span className="text-[0.6rem] font-black uppercase tracking-[0.1em] text-brand">New Extra Feature</span>
                        </div>
                        <h4 className="text-xl font-bold text-text-primary tracking-tight">Download on your Phone?</h4>
                        <p className="text-sm font-medium text-text-secondary leading-relaxed max-w-sm">
                            Scan this QR code to instantly open this link on your mobile device. No cables, no clouds—just scan and download.
                        </p>
                        {!showQR && (
                            <button 
                                onClick={() => setShowQR(true)}
                                className="mt-2 px-6 py-2.5 rounded-2xl bg-brand text-white text-xs font-black uppercase tracking-widest hover:bg-brand-hover shadow-lg shadow-brand/20 transition-all"
                            >
                                Generate Mobile QR
                            </button>
                        )}
                    </div>

                    {showQR && (
                        <div className="relative group p-4 bg-white rounded-3xl shadow-inner animate-scale-up">
                            <img src={qrUrl} alt="Quick scan download" className="w-40 h-40 rounded-xl" />
                            <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-white/40 backdrop-blur-sm rounded-3xl">
                                <span className="text-[0.6rem] font-bold text-black uppercase tracking-widest">Scan Me</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Global Progress */}
            {isAnyDownloading && (
                <div className="p-8 rounded-[2.5rem] bg-bg-card border-2 border-brand/30 shadow-2xl overflow-hidden animate-fade-in">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex flex-col">
                            <span className="text-[0.65rem] font-black uppercase tracking-[0.3em] text-brand">Server Processing</span>
                            <span className="text-sm font-bold text-text-primary mt-0.5">Merging streams & finalizing...</span>
                        </div>
                        <span className="text-lg font-black text-brand">{downloadProgress > 0 ? `${downloadProgress}%` : ''}</span>
                    </div>
                    <div className="relative h-3 w-full bg-bg-input rounded-full overflow-hidden shadow-inner">
                        <div 
                            className="h-full bg-brand transition-all duration-1000 ease-out shadow-[0_0_20px_rgba(99,102,241,0.6)]"
                            style={{ width: `${downloadProgress > 0 ? downloadProgress : 15}%` }}
                        />
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
                    </div>
                    <p className="mt-4 text-center text-[0.6rem] font-bold text-text-muted uppercase tracking-[0.2em] animate-pulse">
                        Please don't close this tab
                    </p>
                </div>
            )}
        </div>
    );
}
