import React from 'react';
import PageShell from '../components/PageShell';

export default function PrivacyPage() {
  return (
    <PageShell title="Privacy Policy" subtitle="Last updated 2026">
      <h2 className="text-text-primary font-display font-bold text-lg">What we collect</h2>
      <p>
        ClipGrabber does not require an account and does not collect names, emails, or payment details for
        using the downloader. When you submit a link, the URL and the resulting media are processed on our
        server only long enough to extract metadata or fulfil your download — files are deleted automatically
        shortly after being served, and are not retained, backed up, or reviewed by us afterward.
      </p>
      <h2 className="text-text-primary font-display font-bold text-lg">Server logs</h2>
      <p>
        Like most web services, our hosting provider's infrastructure may log basic request metadata (IP
        address, timestamp, requested endpoint) for operational purposes such as abuse prevention and
        debugging. These logs are not used to build user profiles or sold to third parties.
      </p>
      <h2 className="text-text-primary font-display font-bold text-lg">Local storage</h2>
      <p>
        Your theme preference (light/dark) and your recent-downloads list are stored only in your browser's
        <code> localStorage</code> — this data never leaves your device and is not visible to us. You can clear
        it at any time from the History panel or by clearing your browser's site data.
      </p>
      <h2 className="text-text-primary font-display font-bold text-lg">Third-party services</h2>
      <p>
        Thumbnails and media are fetched directly from the source platform (YouTube, Instagram, TikTok,
        Facebook, Pinterest) via our server. If ad networks such as Google AdSense or Adsterra are enabled on
        this deployment, they may set their own cookies and collect data under their own privacy policies —
        we don't control that data collection and encourage you to review those networks' policies directly.
      </p>
      <h2 className="text-text-primary font-display font-bold text-lg">Contact</h2>
      <p>
        Questions about this policy can be sent via the <a href="/contact" className="text-brand underline">Contact page</a>.
      </p>
    </PageShell>
  );
}
