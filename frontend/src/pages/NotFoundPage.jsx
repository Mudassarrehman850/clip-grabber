import React from 'react';
import { Link } from 'react-router-dom';
import PageShell from '../components/PageShell';

export default function NotFoundPage() {
  return (
    <PageShell title="Page not found" subtitle="The page you're looking for doesn't exist.">
      <p className="text-center">
        <Link to="/" className="text-brand underline font-semibold">Back to the downloader</Link>
      </p>
    </PageShell>
  );
}
