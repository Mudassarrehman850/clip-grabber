import React, { useState } from 'react';
import PageShell from '../components/PageShell';

const FAQ_ITEMS = [
  { q: 'Is ClipGrabber free to use?', a: 'Yes, completely free. No signup, no limits, no hidden fees.' },
  { q: 'Is it safe to use?', a: "Yes. We don't store your downloads server-side beyond the few minutes it takes to serve them, and we don't require any personal information to use the tool." },
  { q: 'Why is Instagram not working?', a: 'Instagram regularly changes its anti-bot measures. Public reels and posts work in most cases; if a specific link fails, try again in a moment or check that the post is public.' },
  { q: 'Can I download private videos?', a: 'No. ClipGrabber only works with publicly accessible content. Private videos and stories behind a login wall are not supported.' },
  { q: 'What formats are supported?', a: 'MP4 for video, MP3 for audio, JPG/WebP for images, and ZIP for Instagram carousels (multi-image posts).' },
  { q: 'Why did my download time out?', a: "Some platforms throttle or slow down automated requests. If a download times out, wait a minute and try again — our server also has a hard time limit to avoid hanging forever on a stuck request." },
  { q: 'Is this legal?', a: 'Downloading publicly available content for personal use is generally acceptable. Always respect copyright and each platform\'s terms of service, and credit creators when re-sharing anything.' },
];

function FAQItem({ q, a }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="premium-card overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-5 py-4 text-left text-sm font-semibold text-text-primary hover:text-brand transition-colors"
      >
        {q}
        <span className={`flex-shrink-0 w-6 h-6 rounded-full border border-border-color flex items-center justify-center transition-transform duration-200 ${open ? 'rotate-180' : ''}`}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </span>
      </button>
      {open && <div className="px-5 pb-5 text-sm text-text-secondary leading-relaxed">{a}</div>}
    </div>
  );
}

export default function FaqPage() {
  return (
    <PageShell title="Frequently Asked Questions" subtitle="Everything you need to know before you paste a link.">
      <div className="space-y-3">
        {FAQ_ITEMS.map((item) => (
          <FAQItem key={item.q} {...item} />
        ))}
      </div>
    </PageShell>
  );
}

export { FAQ_ITEMS };
