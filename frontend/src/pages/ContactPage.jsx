import React from 'react';
import PageShell from '../components/PageShell';

export default function ContactPage() {
  return (
    <PageShell title="Contact" subtitle="Questions, bug reports, or feature requests — reach out directly.">
      <div className="grid grid-cols-1 gap-4">
        <a
          href="mailto:mudassar1rehman@gmail.com"
          className="group block p-6 rounded-2xl bg-brand/[0.03] border border-brand/15 hover:border-brand/40 transition-colors text-center"
        >
          <p className="text-[0.65rem] font-bold uppercase tracking-[0.2em] text-brand mb-1">Direct Email</p>
          <p className="text-lg font-semibold text-text-primary">mudassar1rehman@gmail.com</p>
        </a>

        <a
          href="https://www.linkedin.com/in/mudassar-rehman-2558253b2"
          target="_blank"
          rel="noreferrer"
          className="group block p-6 rounded-2xl bg-[#0077B5]/[0.03] border border-[#0077B5]/15 hover:border-[#0077B5]/40 transition-colors text-center"
        >
          <p className="text-[0.65rem] font-bold uppercase tracking-[0.2em] text-[#0077B5] mb-1">LinkedIn</p>
          <p className="text-lg font-semibold text-text-primary">Connect with the developer</p>
        </a>
      </div>
      <p className="text-xs text-text-muted text-center pt-2">
        Typical response time is within 24 hours.
      </p>
    </PageShell>
  );
}
