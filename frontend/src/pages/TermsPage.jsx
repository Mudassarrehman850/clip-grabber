import React from 'react';
import PageShell from '../components/PageShell';

export default function TermsPage() {
  return (
    <PageShell title="Terms of Service" subtitle="Last updated 2026">
      <h2 className="text-text-primary font-display font-bold text-lg">1. Acceptance of terms</h2>
      <p>
        By accessing and using ClipGrabber, you agree to be bound by these terms. The service allows you to
        download publicly available media for personal, non-commercial use only.
      </p>
      <h2 className="text-text-primary font-display font-bold text-lg">2. Acceptable use</h2>
      <p>
        You may not use ClipGrabber to infringe upon the intellectual property rights of others, to download
        private or login-gated content, to automate bulk scraping of a platform, or to redistribute downloaded
        content commercially without the rights holder's permission. You are solely responsible for ensuring
        you have the right to download and use any content you process through this service.
      </p>
      <h2 className="text-text-primary font-display font-bold text-lg">3. No warranty</h2>
      <p>
        ClipGrabber depends on third-party platforms that can change their site structure or anti-bot measures
        at any time without notice, which may cause downloads to fail temporarily or permanently. The service
        is provided "as is" without warranty of uptime, accuracy, or continued support for any given platform.
      </p>
      <h2 className="text-text-primary font-display font-bold text-lg">4. Limitation of liability</h2>
      <p>
        In no event shall ClipGrabber or its operator be liable for any damages arising out of the use or
        inability to use this service, including but not limited to lost data, lost downloads, or copyright
        claims arising from your use of downloaded content.
      </p>
      <h2 className="text-text-primary font-display font-bold text-lg">5. Changes</h2>
      <p>
        These terms may be updated from time to time; continued use of the service after changes are posted
        constitutes acceptance of the revised terms.
      </p>
    </PageShell>
  );
}
