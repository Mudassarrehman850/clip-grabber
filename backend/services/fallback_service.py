import re
import requests
import html
import json

GENERIC_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Ch-Ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Upgrade-Insecure-Requests': '1',
}

def manual_extract(url, platform):
    """Fallback manual extraction using regex for FB and Pinterest."""
    if platform == 'facebook':
        return extract_fb_manual(url)
    if platform == 'pinterest':
        return extract_pin_manual(url)
    return None

def extract_fb_manual(url):
    """Manually extract Facebook video URLs from page source."""
    # Force mobile subdomain for easier scraping
    fetch_url = url.replace('www.facebook.com', 'm.facebook.com')
    try:
        resp = requests.get(fetch_url, headers=GENERIC_HEADERS, timeout=15)
        resp.raise_for_status()
        content = resp.text

        # Search for HD/SD sources in the JS blobs or meta tags
        hd_url = None
        sd_url = None

        # Pattern 1: browser_native_xx_url
        hd_match = re.search(r'browser_native_hd_url":"([^"]+)"', content)
        sd_match = re.search(r'browser_native_sd_url":"([^"]+)"', content)

        if not hd_match:
            # Pattern 2: simple hd_src/sd_src
            hd_match = re.search(r'"hd_src":"([^"]+)"', content)
            sd_match = re.search(r'"sd_src":"([^"]+)"', content)
        
        if hd_match:
            hd_url = html.unescape(hd_match.group(1)).replace('\\/', '/')
        if sd_match:
            sd_url = html.unescape(sd_match.group(1)).replace('\\/', '/')

        if not sd_url and not hd_url:
            # Try og:video as last resort
            og_match = re.search(r'property="og:video" content="([^"]+)"', content)
            if og_match:
                sd_url = html.unescape(og_match.group(1))

        if not sd_url and not hd_url:
            return None

        # Build dummy metadata object
        formats = []
        if hd_url:
            formats.append({'id': 'video_best', 'label': 'Video (HD Fallback)', 'ext': 'mp4', 'type': 'video', 'url': hd_url})
        if sd_url:
            formats.append({'id': 'video_sd', 'label': 'Video (SD Fallback)', 'ext': 'mp4', 'type': 'video', 'url': sd_url})

        # Get Title
        title_match = re.search(r'<title>(.*?)</title>', content)
        title = title_match.group(1) if title_match else 'Facebook Video'

        # Get Thumbnail
        thumb_match = re.search(r'property="og:image" content="([^"]+)"', content)
        thumb = html.unescape(thumb_match.group(1)) if thumb_match else None

        return {
            'title': title,
            'thumbnail': thumb,
            'uploader': 'Facebook User',
            'platform': 'facebook',
            'formats': formats,
            'webpage_url': url,
            'is_fallback': True
        }

    except Exception:
        return None

def extract_pin_manual(url):
    """Manually extract Pinterest Pin media."""
    try:
        resp = requests.get(url, headers=GENERIC_HEADERS, timeout=15)
        resp.raise_for_status()
        content = resp.text

        # Search for video in meta tags
        vid_match = re.search(r'property="og:video" content="([^"]+)"', content)
        img_match = re.search(r'property="og:image" content="([^"]+)"', content)
        
        formats = []
        if vid_match:
            vid_url = html.unescape(vid_match.group(1))
            formats.append({'id': 'video_best', 'label': 'Download Video (MP4)', 'ext': 'mp4', 'type': 'video', 'url': vid_url})
        
        if img_match:
            img_url = html.unescape(img_match.group(1))
            formats.append({'id': 'pin_image', 'label': 'Download Image (JPG)', 'ext': 'jpg', 'type': 'image', 'url': img_url})

        if not formats:
            # Try to find JSON blob
            json_match = re.search(r'<script type="application/json" id="__PINTEREST_ANYWHERE_DATA__">(.*?)</script>', content)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    # Extract logic for nested JSON could go here if needed, but meta tags are usually enough
                except:
                    pass

        if not formats:
            return None

        # Title
        title_match = re.search(r'<title>(.*?)</title>', content)
        title = title_match.group(1) if title_match else 'Pinterest Pin'

        return {
            'title': title,
            'thumbnail': formats[-1]['url'] if formats else None,
            'uploader': 'Pinterest User',
            'platform': 'pinterest',
            'formats': formats,
            'webpage_url': url,
            'is_fallback': True
        }
    except Exception:
        return None
