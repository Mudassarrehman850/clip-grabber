import React from 'react';
import PageShell from '../components/PageShell';

export default function AboutPage() {
  return (
    <PageShell
      title="About ClipGrabber"
      subtitle="A free, no-signup toolkit for saving publicly available media from the platforms you already use."
    >
      <p>
        ClipGrabber lets you download videos, photos, reels, and audio from YouTube, Instagram, TikTok,
        Facebook, and Pinterest by pasting a link. There's no account to create, no software to install,
        and no watermark added by us — you get the same file the platform serves, in the format you choose.
      </p>
      <h2 className="text-text-primary font-display font-bold text-lg">Why it exists</h2>
      <p>
        Most "downloader" sites bury a simple utility under intrusive redirects, fake download buttons, and
        popunder ads. ClipGrabber is built the other way around: one input box, a clear list of formats, and
        nothing standing between you and your file.
      </p>
      <h2 className="text-text-primary font-display font-bold text-lg">How it works, technically</h2>
      <p>
        When you submit a link, our backend uses <code>yt-dlp</code> (and a small set of platform-specific
        fallbacks) to read the public metadata for that post — title, available formats, thumbnail — without
        downloading anything yet. Only when you click a specific format does the server fetch and convert the
        actual media file, stream it back to your browser, and then delete its local copy.
      </p>
      <h2 className="text-text-primary font-display font-bold text-lg">What we don't do</h2>
      <p>
        We don't support downloading private or login-gated content, we don't store your download history on
        our servers, and we don't strip or add watermarks beyond what the source platform already applies.
        See our <a href="/privacy" className="text-brand underline">Privacy Policy</a> for details on data handling.
      </p>
    </PageShell>
  );
}
