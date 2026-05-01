import React, { useEffect, useRef } from 'react';

// Your AdSense publisher ID — replace with real one after approval
// Format: ca-pub-XXXXXXXXXXXXXXXX
const ADSENSE_CLIENT = process.env.REACT_APP_ADSENSE_CLIENT || '';

/**
 * AdSlot — renders a Google AdSense ad unit.
 * Falls back to a placeholder box when ADSENSE_CLIENT is not set
 * so the layout doesn't break during development.
 *
 * Usage:
 *   <AdSlot slot="1234567890" style="banner" />
 *   <AdSlot slot="0987654321" style="rectangle" />
 */
export default function AdSlot({ slot, format = 'auto', style: adStyle = 'banner', className = '' }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!ADSENSE_CLIENT || !slot) return;
    try {
      if (window.adsbygoogle) {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      }
    } catch (e) {}
  }, [slot]);

  // Placeholder during dev / before AdSense approval
  if (!ADSENSE_CLIENT || !slot) {
    return (
      <div
        className={`ad-slot ad-slot-${adStyle} ${className}`}
        data-ad-slot={slot}
      >
        Ad · {adStyle}
      </div>
    );
  }

  const heightMap = { banner: 90, rectangle: 250, leaderboard: 90 };

  return (
    <div className={`overflow-hidden rounded-xl ${className}`} style={{ minHeight: heightMap[adStyle] || 90 }}>
      <ins
        ref={ref}
        className="adsbygoogle"
        style={{ display: 'block', width: '100%', height: heightMap[adStyle] || 90 }}
        data-ad-client={ADSENSE_CLIENT}
        data-ad-slot={slot}
        data-ad-format={format}
        data-full-width-responsive="true"
      />
    </div>
  );
}
