import yt_dlp
import os
import re
import time
import zipfile
import requests
from typing import Optional
from bs4 import BeautifulSoup

# Instaloader fallback for /p/ posts (imported lazily to avoid hard dep errors)
def _try_instaloader_metadata(url: str) -> dict:
    """Try extracting metadata via Instaloader. Returns dict or raises."""
    from services.instaloader_service import extract_post_metadata
    return extract_post_metadata(url)

def _try_instaloader_download(url: str, format_id: str) -> dict:
    """Try downloading via Instaloader. Returns file dict or raises."""
    from services.instaloader_service import download_post
    return download_post(url, format_id)

def _try_manual_fallback(url: str, platform: str) -> dict:
    """Try extracting via manual regex fallback."""
    from services.fallback_service import manual_extract
    return manual_extract(url, platform)

def _is_post_url(url: str) -> bool:
    """True if this is a /p/ post URL (not a reel, tv, story)."""
    import re as _re
    return bool(_re.search(r'/p/[A-Za-z0-9_-]+', url))


DOWNLOAD_FOLDER = '/tmp/social_dl_cache'

IG_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
}

GENERIC_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Ch-Ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
}

FB_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Dest': 'document',
}

PINTEREST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes (colors, cursor movement) from a string."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text).strip()


def _clean_error(e: Exception) -> str:
    """Return a clean, human-readable error string with no ANSI codes."""
    raw = str(e)
    cleaned = _strip_ansi(raw)
    # Remove yt-dlp prefix noise like "ERROR: [Instagram] shortcode: ..."
    cleaned = re.sub(r'^ERROR:\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^\[[\w]+\]\s*[\w]+:\s*', '', cleaned)
    return cleaned[:200]


def _get_ydl_opts_base(extra: dict = None) -> dict:
    opts = {
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'extract_flat': False,
        'socket_timeout': 45,
        'retries': 5,
        'http_headers': GENERIC_HEADERS.copy(),
        'nocheckcertificate': True,
        'geo_bypass': True,
        'add_header': [
            'Accept-Encoding: identity',
            'Connection: keep-alive'
        ],
    }
    if extra:
        opts.update(extra)
    return opts


def _get_ydl_opts_instagram(extra: dict = None) -> dict:
    """Instagram-specific ydl opts with mobile UA and relaxed options."""
    opts = _get_ydl_opts_base()
    opts['http_headers'] = IG_HEADERS.copy()
    # Allow extracting image-only posts
    opts['allow_playlist_files'] = True
    if extra:
        opts.update(extra)
    return opts


def _get_ydl_opts_facebook(extra: dict = None) -> dict:
    """Facebook-specific ydl opts with specific headers and optional cookies."""
    opts = _get_ydl_opts_base()
    opts['http_headers'] = FB_HEADERS.copy()
    
    # Check for cookie file (user can provide this if needed)
    cookie_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'facebook_cookies.txt')
    if os.path.exists(cookie_path):
        opts['cookiefile'] = cookie_path
        
    if extra:
        opts.update(extra)
    return opts


# ─────────────────────────────────────────────
#  METADATA EXTRACTION
# ─────────────────────────────────────────────

def extract_metadata(url: str, platform: str, content_type: str) -> dict:
    """
    Extract metadata from a URL without downloading the media.
    Handles: videos, images, carousels (multi-image), profiles.
    """
    # Force mobile subdomain for Facebook to bypass some bot detection
    if platform == 'facebook' and 'www.facebook.com' in url:
        url = url.replace('www.facebook.com', 'm.facebook.com')

    if platform == 'instagram':
        return _extract_instagram_metadata(url, content_type)

    ydl_opts = _get_ydl_opts_base({'skip_download': True, 'writeinfojson': False})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise ValueError("Could not extract media information")

            # Flatten playlist (take first entry)
            if info.get('_type') == 'playlist':
                entries = [e for e in (info.get('entries') or []) if e]
                if not entries:
                    raise ValueError("No media found in this URL")
                info = entries[0]

            return _build_metadata(info, platform, content_type)

    except yt_dlp.utils.DownloadError as e:
        mapped = _map_download_error(e)
        if platform in ('facebook', 'pinterest') and not isinstance(mapped, PermissionError):
            return _extract_og_metadata(url, platform, content_type)
        raise mapped
    except (ValueError, PermissionError, ConnectionError) as e:
        if platform in ('facebook', 'pinterest') and not isinstance(e, PermissionError):
            return _extract_og_metadata(url, platform, content_type)
        raise
    except Exception as e:
        if platform in ('facebook', 'pinterest'):
            return _extract_og_metadata(url, platform, content_type)
        raise ValueError(f"Failed to extract media info: {_clean_error(e)}")


def _extract_og_metadata(url: str, platform: str, content_type: str) -> dict:
    """Fallback metadata extractor using Open Graph tags — for FB posts & Pinterest pins."""
    if platform == 'pinterest':
        scrape_headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    else:
        scrape_headers = GENERIC_HEADERS
    resp = requests.get(url, headers=scrape_headers, timeout=20, allow_redirects=True)
    resp.raise_for_status()
    html = resp.text

    def og(prop):
        # Match both attribute orders, and handle unquoted/encoded content
        m = re.search(rf'<meta[^>]+property=["\']og:{prop}["\'][^>]+content=["\'](.*?)["\']', html, re.IGNORECASE)
        if not m:
            m = re.search(rf'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:{prop}["\']', html, re.IGNORECASE)
        val = m.group(1).strip() if m else None
        # Pinterest sometimes HTML-encodes the URL (& -> &amp;)
        if val:
            val = val.replace('&amp;', '&').replace('&#39;', "'").replace('&quot;', '"')
        return val

    title = og('title') or 'Untitled'
    thumbnail = og('image')
    description = og('description') or ''

    # Clean up Pinterest "rich" descriptions which sometimes contain HTML fragments
    if platform == 'pinterest' and description and '<' in description:
        description = re.sub(r'<[^>]+>', '', description).strip()

    # Pinterest fallback: extract directly from pinimg CDN links in the page
    if platform == 'pinterest' and (not thumbnail or 'logo' in thumbnail or 'favicon' in thumbnail):
        pinimg = re.search(r'(https://i\.pinimg\.com/[^\s"\'<>]+(?:jpg|jpeg|png|webp))', html, re.IGNORECASE)
        if pinimg:
            thumbnail = pinimg.group(1)

    # Determine if it's a video pin/post
    og_type = og('type') or ''
    is_video = 'video' in og_type or content_type in ('video', 'reel')

    if is_video:
        formats = [
            {'id': 'video_best', 'label': 'Download Video (MP4)', 'ext': 'mp4', 'type': 'video'},
        ]
        if platform == 'pinterest':
            formats.append({'id': 'pin_image', 'label': 'Download Thumbnail (JPG)', 'ext': 'jpg', 'type': 'image'})
    else:
        if platform == 'facebook':
            formats = [{'id': 'fb_image', 'label': 'Download Photo (JPG)', 'ext': 'jpg', 'type': 'image'}]
        else:
            formats = [{'id': 'pin_image', 'label': 'Download Image (JPG)', 'ext': 'jpg', 'type': 'image'}]

    return {
        'title': title,
        'thumbnail': thumbnail,
        'duration': None,
        'uploader': platform.capitalize(),
        'uploader_url': None,
        'view_count': None,
        'like_count': None,
        'comment_count': None,
        'repost_count': None,
        'upload_date': None,
        'upload_timestamp': None,
        'caption': {'full_text': description, 'hashtags': [], 'mentions': [], 'urls': [], 'word_count': 0, 'char_count': len(description), 'chapters': []},
        'description': description[:200],
        'platform': platform,
        'content_type': content_type,
        'formats': formats,
        'webpage_url': url,
        'is_carousel': False,
        'channel_follower_count': None,
        'categories': None,
        'tags': [],
    }


def _extract_instagram_metadata(url: str, content_type: str) -> dict:
    """
    Instagram-specific extraction.
    Tries yt-dlp first; falls back to Instaloader for /p/ posts.
    Handles: video posts/reels, single-image posts, carousel (multi-image) posts.
    """
    ydl_opts = _get_ydl_opts_instagram({'skip_download': True, 'writeinfojson': False})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            raise ValueError("_YTDLP_FAILED_")

        # ── Carousel (album) ────────────────────────────────────────────
        # yt-dlp returns _type='playlist' with entries for multi-image posts
        if info.get('_type') == 'playlist':
            entries = [e for e in (info.get('entries') or []) if e]
            if not entries:
                raise ValueError("No media found in this Instagram post")

            # Resolve lazy entries
            resolved = []
            for entry in entries:
                if entry.get('url') and not entry.get('formats'):
                    try:
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                            full = ydl2.extract_info(entry['url'], download=False)
                            if full:
                                resolved.append(full)
                            else:
                                resolved.append(entry)
                    except Exception:
                        resolved.append(entry)
                else:
                    resolved.append(entry)

            # Determine what types are in the carousel
            has_video = any(_entry_is_video(e) for e in resolved)
            slide_count = len(resolved)

            # Build slide previews for the frontend
            slides = []
            for i, entry in enumerate(resolved):
                slides.append({
                    'index': i,
                    'type': 'video' if _entry_is_video(entry) else 'image',
                    'thumbnail': entry.get('thumbnail') or _get_best_thumbnail(entry),
                    'url': entry.get('webpage_url') or entry.get('url', ''),
                })

            # Use the first entry's thumbnail as main thumbnail
            main_thumb = resolved[0].get('thumbnail') or _get_best_thumbnail(resolved[0])

            formats = _build_carousel_formats(resolved, has_video, slide_count)

            caption_data = _extract_caption(info, 'instagram')
            return {
                'title': info.get('title') or info.get('description', '')[:80] or f'Instagram Post ({slide_count} items)',
                'thumbnail': main_thumb,
                'duration': None,
                'uploader': info.get('uploader') or info.get('channel') or 'Instagram',
                'uploader_url': info.get('uploader_url'),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'comment_count': info.get('comment_count'),
                'upload_date': info.get('upload_date'),
                'upload_timestamp': info.get('timestamp'),
                'caption': caption_data,
                'description': (info.get('description') or '')[:200],
                'platform': 'instagram',
                'content_type': 'carousel',
                'is_carousel': True,
                'slide_count': slide_count,
                'slides': slides,
                'formats': formats,
                'webpage_url': url,
                'tags': info.get('tags') or [],
            }

        # ── Single post ──────────────────────────────────────────────────
        is_video = _entry_is_video(info)

        formats = _build_instagram_single_formats(info, is_video, content_type)

        meta = _build_metadata(info, 'instagram', content_type)
        meta['formats'] = formats
        meta['is_carousel'] = False
        meta['slide_count'] = 1
        return meta

    except (ValueError, PermissionError, ConnectionError) as e:
        # If yt-dlp failed on a /p/ post, try Instaloader fallback
        if _is_post_url(url) and not isinstance(e, PermissionError):
            try:
                return _try_instaloader_metadata(url)
            except (PermissionError, ValueError) as il_err:
                raise il_err
            except Exception:
                pass  # fall through to original error
        raise
    except yt_dlp.utils.DownloadError as e:
        mapped = _map_download_error(e)
        if _is_post_url(url) and not isinstance(mapped, PermissionError):
            try:
                return _try_instaloader_metadata(url)
            except (PermissionError, ValueError) as il_err:
                raise il_err
            except Exception:
                pass
        raise mapped
    except Exception as e:
        if _is_post_url(url):
            try:
                return _try_instaloader_metadata(url)
            except (PermissionError, ValueError) as il_err:
                raise il_err
            except Exception:
                pass
        raise ValueError(f"Failed to extract Instagram info: {_clean_error(e)}")


def _entry_is_video(entry: dict) -> bool:
    """Check if an info-dict entry contains video media."""
    if not entry:
        return False
    # Has formats with video codec
    for fmt in (entry.get('formats') or []):
        if fmt.get('vcodec') and fmt['vcodec'] != 'none':
            return True
    # Duration > 0 is a strong signal
    if entry.get('duration') and float(entry.get('duration') or 0) > 0:
        return True
    # ext is a video format
    if entry.get('ext') in ('mp4', 'webm', 'mov', 'm4v'):
        return True
    return False


def _build_instagram_single_formats(info: dict, is_video: bool, content_type: str) -> list:
    if content_type == 'profile':
        return [{'id': 'profile_pic', 'label': 'Profile Picture (HD)', 'ext': 'jpg', 'type': 'image'}]

    if is_video:
        return [
            {'id': 'video_best', 'label': 'Download Video (MP4)', 'ext': 'mp4', 'type': 'video'},
        ]
    else:
        # Pure image post
        return [
            {'id': 'ig_image', 'label': 'Download Image (JPG)', 'ext': 'jpg', 'type': 'image'},
        ]


def _build_carousel_formats(entries: list, has_video: bool, slide_count: int) -> list:
    """Build format list for a carousel post."""
    formats = []

    # Always offer "download all as ZIP"
    formats.append({
        'id': 'carousel_zip',
        'label': f'Download All ({slide_count} files) — ZIP',
        'ext': 'zip',
        'type': 'archive',
        'slide_count': slide_count,
    })

    # Offer individual slide downloads
    for i, entry in enumerate(entries):
        is_vid = _entry_is_video(entry)
        formats.append({
            'id': f'slide_{i}',
            'label': f'Slide {i+1} — {"Video (MP4)" if is_vid else "Image (JPG)"}',
            'ext': 'mp4' if is_vid else 'jpg',
            'type': 'video' if is_vid else 'image',
            'slide_index': i,
        })

    return formats


def _build_metadata(info: dict, platform: str, content_type: str) -> dict:
    duration = info.get('duration')
    duration_str = None
    if duration:
        mins = int(duration) // 60
        secs = int(duration) % 60
        duration_str = f"{mins}:{secs:02d}"

    formats = _extract_formats(info, platform, content_type)
    caption_data = _extract_caption(info, platform)

    return {
        'title': info.get('title') or info.get('description', '')[:80] or 'Untitled',
        'thumbnail': info.get('thumbnail') or _get_best_thumbnail(info),
        'duration': duration_str,
        'uploader': info.get('uploader') or info.get('channel') or info.get('creator') or 'Unknown',
        'uploader_url': info.get('uploader_url') or info.get('channel_url'),
        'view_count': info.get('view_count'),
        'like_count': info.get('like_count'),
        'comment_count': info.get('comment_count'),
        'repost_count': info.get('repost_count'),
        'upload_date': info.get('upload_date'),
        'upload_timestamp': info.get('timestamp'),
        'caption': caption_data,
        'description': (info.get('description') or '')[:200],
        'platform': platform,
        'content_type': content_type,
        'formats': formats,
        'webpage_url': info.get('webpage_url', ''),
        'is_carousel': False,
        'channel_follower_count': info.get('channel_follower_count'),
        'categories': info.get('categories'),
        'tags': info.get('tags') or [],
    }


def _extract_caption(info: dict, platform: str) -> dict:
    """
    Extract and structure the full caption/description.
    Returns: full_text, hashtags, mentions, urls, word_count, char_count, chapters.
    """
    raw = ''

    if platform == 'youtube':
        raw = info.get('description') or ''
    elif platform == 'instagram':
        raw = info.get('description') or info.get('title') or info.get('full_title') or ''
    elif platform == 'tiktok':
        raw = info.get('description') or info.get('title') or ''
    elif platform == 'facebook':
        raw = info.get('description') or info.get('title') or ''
    elif platform == 'pinterest':
        raw = info.get('description') or info.get('title') or ''

    raw = raw.strip()

    # Hashtags
    hashtags = list(dict.fromkeys(tag.lower() for tag in re.findall(r'#(\w+)', raw)))

    # @mentions
    mentions = list(dict.fromkeys(m.lower() for m in re.findall(r'@([\w.]+)', raw)))

    # URLs embedded in caption
    urls = re.findall(r'https?://[^\s\)\]\>\"\']+', raw)

    # Word count (exclude tags/mentions)
    clean = re.sub(r'[#@]\w+', '', raw)
    word_count = len(clean.split()) if clean.strip() else 0

    # YouTube chapters
    chapters = []
    if platform == 'youtube' and info.get('chapters'):
        for ch in info['chapters']:
            start = ch.get('start_time', 0)
            mins = int(start) // 60
            secs = int(start) % 60
            chapters.append({
                'title': ch.get('title', ''),
                'start_time': start,
                'start_time_str': f'{mins}:{secs:02d}',
                'end_time': ch.get('end_time'),
            })

    return {
        'full_text': raw,
        'hashtags': hashtags,
        'mentions': mentions,
        'urls': urls[:10],
        'word_count': word_count,
        'char_count': len(raw),
        'chapters': chapters,
    }


def _get_best_thumbnail(info: dict) -> Optional[str]:
    thumbnails = info.get('thumbnails') or []
    if not thumbnails:
        return None
    sorted_thumbs = sorted(
        thumbnails,
        key=lambda t: (t.get('width') or 0) * (t.get('height') or 0),
        reverse=True
    )
    return sorted_thumbs[0].get('url') if sorted_thumbs else None


def _extract_formats(info: dict, platform: str, content_type: str) -> list:
    formats = []

    if platform == 'youtube':
        formats.append({'id': 'video_best', 'label': 'Video (Best)', 'ext': 'mp4', 'type': 'video'})
        if content_type != 'short':
            formats.append({'id': 'video_720', 'label': 'Video (720p)', 'ext': 'mp4', 'type': 'video'})
            formats.append({'id': 'audio_320', 'label': 'Audio (320kbps MP3)', 'ext': 'mp3', 'type': 'audio'})
            formats.append({'id': 'audio_mp3', 'label': 'Audio (128kbps)', 'ext': 'mp3', 'type': 'audio'})
        formats.append({'id': 'thumbnail', 'label': 'Thumbnail (JPG)', 'ext': 'jpg', 'type': 'image'})
        return formats

    if platform == 'tiktok':
        formats.append({'id': 'video_best', 'label': 'Video (with watermark)', 'ext': 'mp4', 'type': 'video'})
        formats.append({'id': 'video_nowm', 'label': 'Video (No Watermark)', 'ext': 'mp4', 'type': 'video'})
        return formats

    if platform == 'instagram':
        if content_type == 'profile':
            return [{'id': 'profile_pic', 'label': 'Profile Picture (HD)', 'ext': 'jpg', 'type': 'image'}]
        formats.append({'id': 'video_best', 'label': 'Download Video (MP4)', 'ext': 'mp4', 'type': 'video'})
        return formats

    if platform == 'facebook':
        if content_type == 'photo':
            return [
                {'id': 'fb_image', 'label': 'Download Photo (JPG)', 'ext': 'jpg', 'type': 'image'},
            ]
        formats.append({'id': 'video_best', 'label': 'Video (HD)', 'ext': 'mp4', 'type': 'video'})
        formats.append({'id': 'video_sd', 'label': 'Video (SD)', 'ext': 'mp4', 'type': 'video'})
        return formats

    if platform == 'pinterest':
        # Always offer both — the image option doubles as thumbnail for video pins
        return [
            {'id': 'video_best', 'label': 'Download Video (MP4)', 'ext': 'mp4', 'type': 'video'},
            {'id': 'pin_image', 'label': 'Download Image (JPG)', 'ext': 'jpg', 'type': 'image'},
        ]

    # Fallback
    formats.append({'id': 'video_best', 'label': 'Download (Best)', 'ext': 'mp4', 'type': 'video'})
    return formats


# ─────────────────────────────────────────────
#  DOWNLOAD DISPATCH
# ─────────────────────────────────────────────

def download_media(url: str, format_id: str, platform: str, content_type: str,
                   slide_index: int = None) -> dict:
    """
    Download media and return { filepath, filename, ext, mime_type }.
    Handles all format_ids including Instagram carousel slides and ZIP.
    """
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    timestamp = str(int(time.time() * 1000))
    output_template = os.path.join(DOWNLOAD_FOLDER, f'{timestamp}_%(id)s.%(ext)s')

    try:
        if format_id == 'thumbnail':
            return _download_thumbnail(url, timestamp)

        if format_id == 'audio_320':
            return _download_audio(url, output_template, timestamp, quality='320')

        if format_id == 'audio_mp3':
            return _download_audio(url, output_template, timestamp, quality='128')

        if format_id == 'video_720':
            return _download_video(url, output_template, timestamp, quality='720')

        if format_id == 'video_nowm':
            return _download_tiktok_nowatermark(url, output_template, timestamp)

        if format_id in ('ig_image', 'ig_image_webp'):
            # Always use instaloader for /p/ posts (handles conversion via Pillow)
            if _is_post_url(url):
                try:
                    return _try_instaloader_download(url, format_id)
                except Exception:
                    pass
            return _download_instagram_image(url, timestamp)

        if format_id == 'ig_video':
            # Instaloader-sourced video download
            if _is_post_url(url):
                return _try_instaloader_download(url, 'ig_video')
            return _download_video(url, output_template, timestamp, quality='best')

        if format_id == 'profile_pic':
            return _download_instagram_image(url, timestamp)

        if format_id == 'carousel_zip':
            # Try instaloader for /p/ carousels (more reliable)
            if _is_post_url(url):
                try:
                    return _try_instaloader_download(url, 'carousel_zip')
                except Exception:
                    pass
            return _download_carousel_zip(url, timestamp)

        if format_id.startswith('slide_'):
            idx = int(format_id.split('_')[1])
            # Try instaloader for /p/ carousel slides
            if _is_post_url(url):
                try:
                    return _try_instaloader_download(url, format_id)
                except Exception:
                    pass
            return _download_carousel_slide(url, idx, timestamp)

        if format_id == 'video_sd':
            if platform == 'facebook':
                return _download_facebook_video(url, output_template, timestamp, quality='sd')
            return _download_video(url, output_template, timestamp, quality='sd')

        if format_id == 'fb_image':
            return _download_og_image(url, timestamp, FB_HEADERS)

        if format_id == 'pin_image':
            return _download_og_image(url, timestamp, PINTEREST_HEADERS)

        # Default: best video
        # For /p/ posts try instaloader first (handles video posts)
        if _is_post_url(url):
            try:
                return _try_instaloader_download(url, 'video_best')
            except Exception:
                pass

        # Platform-specific best video routing
        if platform == 'facebook':
            return _download_facebook_video(url, output_template, timestamp, quality='best')
        if platform == 'pinterest':
            return _download_pinterest_video(url, output_template, timestamp)

        # Default: best video
        return _download_video(url, output_template, timestamp, quality='best')

    except yt_dlp.utils.DownloadError as e:
        # One last try with manual fallback for downloads
        if platform in ('facebook', 'pinterest'):
            try:
                meta = _try_manual_fallback(url, platform)
                if meta and meta.get('formats'):
                    # Find the requested format or best video
                    target = next((f for f in meta['formats'] if f['id'] == format_id), meta['formats'][0])
                    if target.get('url'):
                        return _download_direct_url(target['url'], timestamp, target['type'])
            except:
                pass
        raise _map_download_error(e)
    except (ValueError, PermissionError, FileNotFoundError):
        raise
    except Exception as e:
        raise ValueError(f"Download error: {_clean_error(e)}")


def _download_direct_url(url: str, timestamp: str, media_type: str) -> dict:
    """Download a direct URL (from fallback) using requests."""
    ext = 'mp4' if media_type == 'video' else 'jpg'
    mime = 'video/mp4' if media_type == 'video' else 'image/jpeg'
    filename = f"fallback_{timestamp}.{ext}"
    filepath = os.path.join(DOWNLOAD_FOLDER, f"{timestamp}_fallback.{ext}")

    resp = requests.get(url, headers=GENERIC_HEADERS, timeout=30, stream=True)
    resp.raise_for_status()

    with open(filepath, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return {'filepath': filepath, 'filename': filename, 'ext': ext, 'mime_type': mime}


# ─────────────────────────────────────────────
#  DOWNLOAD IMPLEMENTATIONS
# ─────────────────────────────────────────────

def _download_video(url: str, output_template: str, timestamp: str, quality: str = 'best') -> dict:
    if quality == '720':
        fmt = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]/best'
    elif quality == 'sd':
        fmt = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best[height<=480]/worst'
    else:
        fmt = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best'

    ydl_opts = _get_ydl_opts_base({
        'format': fmt,
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
        'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
    })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    filepath = _find_downloaded_file(timestamp, DOWNLOAD_FOLDER)
    return {'filepath': filepath, 'filename': f'video_{timestamp}.mp4', 'ext': 'mp4', 'mime_type': 'video/mp4'}


def _download_facebook_video(url: str, output_template: str, timestamp: str, quality: str = 'best') -> dict:
    """Download Facebook video with specialized fallback logic."""
    fmt = 'bestvideo[ext=mp4]+bestaudio/best' if quality == 'best' else 'worst'
    ydl_opts = _get_ydl_opts_facebook({
        'format': fmt,
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
    })
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
    except Exception as e:
        # If yt-dlp fails, try to scrape the direct video URL from meta tags
        try:
            resp = requests.get(url, headers=FB_HEADERS, timeout=20)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Check for various video meta tags
            og_video = soup.find('meta', property='og:video') or soup.find('meta', property='og:video:url')
            video_url = og_video['content'] if og_video else None
            
            if not video_url:
                raise e # re-raise original if we still can't find it
                
            return _download_direct_url(video_url, timestamp, 'video')
        except:
            raise e

    filepath = _find_downloaded_file(timestamp, DOWNLOAD_FOLDER)
    return {'filepath': filepath, 'filename': f'fb_video_{timestamp}.mp4', 'ext': 'mp4', 'mime_type': 'video/mp4'}


def _download_facebook_photo(url: str, timestamp: str) -> dict:
    """Scrape and download high-res Facebook photo via og:image."""
    resp = requests.get(url, headers=FB_HEADERS, timeout=25)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    og_image = soup.find('meta', property='og:image')
    img_url = og_image['content'] if og_image else None
    
    if not img_url:
        raise ValueError("Could not find image in this Facebook post page source")
    
    # Download the image content
    img_resp = requests.get(img_url, headers=FB_HEADERS, timeout=25)
    img_resp.raise_for_status()
    
    filepath = os.path.join(DOWNLOAD_FOLDER, f'{timestamp}_fb_photo.jpg')
    with open(filepath, 'wb') as f:
        f.write(img_resp.content)
        
    return {
        'filepath': filepath, 
        'filename': f'fb_photo_{timestamp}.jpg', 
        'ext': 'jpg', 
        'mime_type': 'image/jpeg'
    }


def _download_pinterest_image(url: str, timestamp: str) -> dict:
    """Scrape and download high-res Pinterest image via og:image."""
    resp = requests.get(url, headers=PINTEREST_HEADERS, timeout=20)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    og_image = soup.find('meta', property='og:image')
    img_url = og_image['content'] if og_image else None
    
    if not img_url:
        raise ValueError("Could not extract image from this Pinterest pin")
    
    # Try to find high-res version if URL looks like a thumbnail (Pinterest specific)
    # thumbnail: i.pinimg.com/236x/...
    # original: i.pinimg.com/originals/...
    if 'pinimg.com/' in img_url:
        img_url = img_url.replace('/236x/', '/originals/').replace('/474x/', '/originals/').replace('/736x/', '/originals/')

    img_resp = requests.get(img_url, headers=PINTEREST_HEADERS, timeout=25)
    img_resp.raise_for_status()
    
    filepath = os.path.join(DOWNLOAD_FOLDER, f'{timestamp}_pin.jpg')
    with open(filepath, 'wb') as f:
        f.write(img_resp.content)
        
    return {
        'filepath': filepath, 
        'filename': f'pin_{timestamp}.jpg', 
        'ext': 'jpg', 
        'mime_type': 'image/jpeg'
    }


def _download_pinterest_video(url: str, output_template: str, timestamp: str) -> dict:
    """Download Pinterest video with og:video fallback."""
    try:
        # Try yt-dlp first
        ydl_opts = _get_ydl_opts_base({
            'outtmpl': output_template,
            'merge_output_format': 'mp4',
        })
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
    except Exception as e:
        # Fallback to scraping og:video
        resp = requests.get(url, headers=PINTEREST_HEADERS, timeout=20)
        soup = BeautifulSoup(resp.text, 'html.parser')
        og_video = soup.find('meta', property='og:video') or soup.find('meta', property='og:video:url')
        
        if not og_video:
            raise e
            
        return _download_direct_url(og_video['content'], timestamp, 'video')
        
    filepath = _find_downloaded_file(timestamp, DOWNLOAD_FOLDER)
    return {'filepath': filepath, 'filename': f'pin_video_{timestamp}.mp4', 'ext': 'mp4', 'mime_type': 'video/mp4'}


def _download_og_image(url: str, timestamp: str, headers: dict) -> dict:
    """Scrape og:image or og:video from a page — works for FB posts & Pinterest pins."""
    resp = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
    resp.raise_for_status()
    html_content = resp.text

    # Try og:image
    match = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](https?://[^"\']+)', html_content)
    if not match:
        match = re.search(r'<meta[^>]+content=["\'](https?://[^"\']+)[^>]+property=["\']og:image["\']', html_content)

    if not match:
        raise ValueError("Could not find a downloadable image in this post")

    img_url = match.group(1)
    img_resp = requests.get(img_url, headers=headers, timeout=20)
    img_resp.raise_for_status()

    try:
        from PIL import Image as PILImage
        import io
        img = PILImage.open(io.BytesIO(img_resp.content))
        if img.mode not in ('RGB',):
            img = img.convert('RGB')
        out = io.BytesIO()
        img.save(out, format='JPEG', quality=95)
        img_bytes = out.getvalue()
    except Exception:
        img_bytes = img_resp.content

    filepath = os.path.join(DOWNLOAD_FOLDER, f'{timestamp}_og_image.jpg')
    with open(filepath, 'wb') as f:
        f.write(img_bytes)
    return {'filepath': filepath, 'filename': f'image_{timestamp}.jpg', 'ext': 'jpg', 'mime_type': 'image/jpeg'}


def _download_audio(url: str, output_template: str, timestamp: str, quality: str = '128') -> dict:
    ydl_opts = _get_ydl_opts_base({
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': quality}],
    })
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)
    filepath = _find_downloaded_file(timestamp, DOWNLOAD_FOLDER, ext='mp3')
    return {'filepath': filepath, 'filename': f'audio_{timestamp}.mp3', 'ext': 'mp3', 'mime_type': 'audio/mpeg'}


def _download_thumbnail(url: str, timestamp: str) -> dict:
    ydl_opts = _get_ydl_opts_base({'skip_download': True})
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        thumb_url = info.get('thumbnail') or _get_best_thumbnail(info)
        if not thumb_url:
            raise ValueError("No thumbnail available for this video")

    resp = requests.get(thumb_url, timeout=15, headers=GENERIC_HEADERS)
    resp.raise_for_status()
    filepath = os.path.join(DOWNLOAD_FOLDER, f'{timestamp}_thumbnail.jpg')
    with open(filepath, 'wb') as f:
        f.write(resp.content)
    return {'filepath': filepath, 'filename': f'thumbnail_{timestamp}.jpg', 'ext': 'jpg', 'mime_type': 'image/jpeg'}


def _download_generic_image(url: str, output_template: str, timestamp: str) -> dict:
    """Download image for Facebook photos and Pinterest pins via yt-dlp."""
    ydl_opts = _get_ydl_opts_base({'skip_download': True})
    
    # Custom headers for image retrieval to avoid 403
    headers = GENERIC_HEADERS.copy()
    if 'facebook.com' in url or 'fb.watch' in url:
        headers['Referer'] = 'https://www.facebook.com/'
    elif 'pinterest' in url:
        headers['Referer'] = 'https://www.pinterest.com/'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        if not info:
            raise ValueError("Could not extract image info")

        if info.get('_type') == 'playlist':
            entries = [e for e in (info.get('entries') or []) if e]
            info = entries[0] if entries else info
            
        img_url = info.get('url') or info.get('thumbnail') or _get_best_thumbnail(info)
        
        if not img_url:
            raise ValueError("No image URL found for this post")
            
        resp = requests.get(img_url, timeout=25, headers=headers)
        resp.raise_for_status()
        
        # Convert to proper JPG via Pillow
        try:
            from PIL import Image as PILImage
            import io
            img = PILImage.open(io.BytesIO(resp.content))
            
            # Remove Exif/Metadata and ensure RGB for compatibility
            data = list(img.getdata())
            img_no_exif = PILImage.new(img.mode, img.size)
            img_no_exif.putdata(data)
            
            if img_no_exif.mode not in ('RGB',):
                img_no_exif = img_no_exif.convert('RGB')
                
            out = io.BytesIO()
            img_no_exif.save(out, format='JPEG', quality=95, optimize=True)
            img_bytes = out.getvalue()
        except Exception:
            img_bytes = resp.content
            
        filepath = os.path.join(DOWNLOAD_FOLDER, f'{timestamp}_image.jpg')
        with open(filepath, 'wb') as f:
            f.write(img_bytes)
            
        return {'filepath': filepath, 'filename': f'image_{timestamp}.jpg', 'ext': 'jpg', 'mime_type': 'image/jpeg'}
    except Exception as e:
        raise ValueError(f"Could not download image: {_clean_error(e)}")


def _download_instagram_image(url: str, timestamp: str) -> dict:
    """
    Download a single Instagram image post (no video).
    Tries yt-dlp first, falls back to direct thumbnail download.
    """
    ydl_opts = _get_ydl_opts_instagram({'skip_download': True})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # Flatten playlist
        if info.get('_type') == 'playlist':
            entries = [e for e in (info.get('entries') or []) if e]
            info = entries[0] if entries else info

        # Try to get the direct image URL from formats or thumbnail
        image_url = _get_instagram_image_url(info)
        if not image_url:
            raise ValueError("Could not find image URL in this post")

        resp = requests.get(image_url, timeout=20, headers=IG_HEADERS)
        resp.raise_for_status()

        # Detect extension from content-type
        ct = resp.headers.get('Content-Type', 'image/jpeg')
        ext = 'jpg' if 'jpeg' in ct or 'jpg' in ct else ('png' if 'png' in ct else 'jpg')

        filepath = os.path.join(DOWNLOAD_FOLDER, f'{timestamp}_image.{ext}')
        with open(filepath, 'wb') as f:
            f.write(resp.content)

        return {
            'filepath': filepath,
            'filename': f'instagram_{timestamp}.{ext}',
            'ext': ext,
            'mime_type': f'image/{ext}' if ext != 'jpg' else 'image/jpeg',
        }

    except requests.RequestException as e:
        raise ValueError(f"Failed to download Instagram image: {str(e)[:100]}")


def _get_instagram_image_url(info: dict) -> Optional[str]:
    """Extract the highest-quality image URL from an Instagram info dict."""
    # Check formats for image/jpeg mime type
    for fmt in (info.get('formats') or []):
        mime = fmt.get('ext', '') or ''
        url = fmt.get('url', '')
        if url and (mime in ('jpg', 'jpeg', 'png', 'webp') or 'jpg' in url or 'cdninstagram' in url):
            return url

    # Check thumbnails sorted by resolution
    thumbnails = info.get('thumbnails') or []
    if thumbnails:
        sorted_t = sorted(
            [t for t in thumbnails if t.get('url')],
            key=lambda t: (t.get('width') or 0) * (t.get('height') or 0),
            reverse=True
        )
        if sorted_t:
            return sorted_t[0]['url']

    return info.get('thumbnail')


def _download_carousel_zip(url: str, timestamp: str) -> dict:
    """Download all slides of a carousel post and zip them."""
    ydl_opts = _get_ydl_opts_instagram({'skip_download': True})

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        raise ValueError("Could not extract carousel info")

    entries = []
    if info.get('_type') == 'playlist':
        entries = [e for e in (info.get('entries') or []) if e]
    else:
        entries = [info]

    if not entries:
        raise ValueError("No items found in carousel")

    zip_path = os.path.join(DOWNLOAD_FOLDER, f'{timestamp}_carousel.zip')
    downloaded_files = []

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for i, entry in enumerate(entries):
            slide_ts = f'{timestamp}_{i}'
            try:
                if _entry_is_video(entry):
                    output_tmpl = os.path.join(DOWNLOAD_FOLDER, f'{slide_ts}_%(id)s.%(ext)s')
                    ydl_dl_opts = _get_ydl_opts_instagram({
                        'format': 'bestvideo[ext=mp4]+bestaudio/best',
                        'outtmpl': output_tmpl,
                        'merge_output_format': 'mp4',
                    })
                    entry_url = entry.get('webpage_url') or entry.get('url', '')
                    with yt_dlp.YoutubeDL(ydl_dl_opts) as ydl2:
                        ydl2.extract_info(entry_url, download=True)
                    fpath = _find_downloaded_file(slide_ts, DOWNLOAD_FOLDER)
                    zf.write(fpath, f'slide_{i+1:02d}.mp4')
                    downloaded_files.append(fpath)
                else:
                    img_url = _get_instagram_image_url(entry)
                    if img_url:
                        resp = requests.get(img_url, timeout=20, headers=IG_HEADERS)
                        resp.raise_for_status()
                        fpath = os.path.join(DOWNLOAD_FOLDER, f'{slide_ts}_image.jpg')
                        with open(fpath, 'wb') as f:
                            f.write(resp.content)
                        zf.write(fpath, f'slide_{i+1:02d}.jpg')
                        downloaded_files.append(fpath)
            except Exception:
                continue  # Skip failed slides, don't abort the whole zip

    # Clean up individual slide files
    for fpath in downloaded_files:
        try:
            os.remove(fpath)
        except Exception:
            pass

    if not zipfile.ZipFile(zip_path).namelist():
        raise ValueError("Could not download any slides from this post")

    return {
        'filepath': zip_path,
        'filename': f'instagram_carousel_{timestamp}.zip',
        'ext': 'zip',
        'mime_type': 'application/zip',
    }


def _download_carousel_slide(url: str, slide_index: int, timestamp: str) -> dict:
    """Download a single slide from a carousel."""
    ydl_opts = _get_ydl_opts_instagram({'skip_download': True})

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    entries = []
    if info.get('_type') == 'playlist':
        entries = [e for e in (info.get('entries') or []) if e]
    else:
        entries = [info]

    if slide_index >= len(entries):
        raise ValueError(f"Slide {slide_index + 1} not found (post has {len(entries)} slides)")

    entry = entries[slide_index]

    if _entry_is_video(entry):
        slide_ts = f'{timestamp}_s{slide_index}'
        output_tmpl = os.path.join(DOWNLOAD_FOLDER, f'{slide_ts}_%(id)s.%(ext)s')
        entry_url = entry.get('webpage_url') or entry.get('url', url)
        ydl_dl_opts = _get_ydl_opts_instagram({
            'format': 'bestvideo[ext=mp4]+bestaudio/best',
            'outtmpl': output_tmpl,
            'merge_output_format': 'mp4',
        })
        with yt_dlp.YoutubeDL(ydl_dl_opts) as ydl2:
            ydl2.extract_info(entry_url, download=True)
        fpath = _find_downloaded_file(slide_ts, DOWNLOAD_FOLDER)
        return {'filepath': fpath, 'filename': f'slide_{slide_index+1}.mp4', 'ext': 'mp4', 'mime_type': 'video/mp4'}
    else:
        img_url = _get_instagram_image_url(entry)
        if not img_url:
            raise ValueError(f"Could not get image URL for slide {slide_index + 1}")
        resp = requests.get(img_url, timeout=20, headers=IG_HEADERS)
        resp.raise_for_status()
        fpath = os.path.join(DOWNLOAD_FOLDER, f'{timestamp}_slide{slide_index}.jpg')
        with open(fpath, 'wb') as f:
            f.write(resp.content)
        return {'filepath': fpath, 'filename': f'slide_{slide_index+1}.jpg', 'ext': 'jpg', 'mime_type': 'image/jpeg'}


def _download_tiktok_nowatermark(url: str, output_template: str, timestamp: str) -> dict:
    ydl_opts = _get_ydl_opts_base({
        'format': 'download_addr-0/bestvideo[vcodec!*=h265]+bestaudio/best',
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
    })
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)
    filepath = _find_downloaded_file(timestamp, DOWNLOAD_FOLDER)
    return {'filepath': filepath, 'filename': f'tiktok_nowm_{timestamp}.mp4', 'ext': 'mp4', 'mime_type': 'video/mp4'}


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def _map_download_error(e: yt_dlp.utils.DownloadError) -> Exception:
    """Convert a yt-dlp DownloadError to a clean typed exception."""
    raw = _clean_error(e)
    lower = raw.lower()
    if 'private' in lower or 'login' in lower or 'sign in' in lower or 'not logged in' in lower:
        return PermissionError("This content is private or requires login to access.")
    if 'not available' in lower or 'removed' in lower or 'deleted' in lower:
        return ValueError("This content is no longer available.")
    if 'geo' in lower or 'region' in lower or 'country' in lower or 'not available in your country' in lower:
        return ValueError("This content is not available in your region.")
    if 'rate' in lower or 'throttl' in lower or 'too many' in lower:
        return ConnectionError("Rate limited by platform. Please try again in a moment.")
    if 'no video' in lower or 'no media' in lower:
        return ValueError("No downloadable media found in this post.")
    return ValueError(f"Could not process this URL: {raw}")


def _find_downloaded_file(timestamp: str, folder: str, ext: str = None) -> str:
    if not os.path.exists(folder):
        raise FileNotFoundError("Download folder not found")

    candidates = []
    for fname in os.listdir(folder):
        if fname.startswith(timestamp):
            fpath = os.path.join(folder, fname)
            if ext is None or fname.endswith(f'.{ext}'):
                if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
                    candidates.append(fpath)

    if candidates:
        return max(candidates, key=os.path.getmtime)

    raise FileNotFoundError(f"Downloaded file not found for session {timestamp}")


def cleanup_old_files(max_age_seconds: int = 3600):
    if not os.path.exists(DOWNLOAD_FOLDER):
        return
    now = time.time()
    for fname in os.listdir(DOWNLOAD_FOLDER):
        fpath = os.path.join(DOWNLOAD_FOLDER, fname)
        try:
            if os.path.isfile(fpath) and (now - os.path.getmtime(fpath)) > max_age_seconds:
                os.remove(fpath)
        except Exception:
            pass
