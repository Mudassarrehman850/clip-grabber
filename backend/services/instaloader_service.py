"""
instaloader_service.py
Fallback for Instagram /p/ posts that yt-dlp can't access anonymously.
Handles: single image, single video, carousel (multi-image/video).
Images are force-converted to proper JPG (or WebP) via Pillow — no JFIF issues.
"""

import os
import re
import io
import time
import zipfile
import requests
import instaloader
from typing import Optional

try:
    from PIL import Image as PILImage
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

DOWNLOAD_FOLDER = '/tmp/social_dl_cache'

IG_DL_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Referer': 'https://www.instagram.com/',
    'Accept': 'image/avif,image/webp,image/apng,*/*;q=0.8',
}

_loader = None


def _get_loader() -> instaloader.Instaloader:
    global _loader
    if _loader is None:
        _loader = instaloader.Instaloader(
            quiet=True,
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern='',
        )
    return _loader


def _shortcode_from_url(url: str) -> Optional[str]:
    match = re.search(r'/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)', url)
    return match.group(1) if match else None


def _convert_to_jpg(raw_bytes: bytes) -> bytes:
    """
    Force-convert any image bytes (WebP, JFIF, PNG, etc.) to proper JPEG bytes.
    Falls back to raw bytes if Pillow not available.
    """
    if not HAS_PILLOW:
        return raw_bytes
    try:
        img = PILImage.open(io.BytesIO(raw_bytes))
        # Convert palette/RGBA modes to RGB for JPEG compatibility
        if img.mode in ('RGBA', 'P', 'LA'):
            bg = PILImage.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            bg.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        out = io.BytesIO()
        img.save(out, format='JPEG', quality=95, optimize=True)
        return out.getvalue()
    except Exception:
        return raw_bytes  # fallback: return original


def _convert_to_webp(raw_bytes: bytes) -> bytes:
    """Convert image to WebP for smaller file sizes."""
    if not HAS_PILLOW:
        return raw_bytes
    try:
        img = PILImage.open(io.BytesIO(raw_bytes))
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGBA')
        out = io.BytesIO()
        img.save(out, format='WEBP', quality=90, method=6)
        return out.getvalue()
    except Exception:
        return raw_bytes


# ─────────────────────────────────────────────────────────────
#  METADATA
# ─────────────────────────────────────────────────────────────

def extract_post_metadata(url: str) -> dict:
    shortcode = _shortcode_from_url(url)
    if not shortcode:
        raise ValueError("Could not extract shortcode from Instagram URL")

    try:
        L = _get_loader()
        post = instaloader.Post.from_shortcode(L.context, shortcode)
    except instaloader.exceptions.LoginRequiredException:
        raise PermissionError("This Instagram post is private or requires login.")
    except instaloader.exceptions.BadResponseException as e:
        raise ValueError(f"Instagram returned an error: {str(e)[:120]}")
    except Exception as e:
        msg = str(e)
        if 'login' in msg.lower() or 'private' in msg.lower():
            raise PermissionError("This Instagram post is private or requires login.")
        raise ValueError(f"Could not load Instagram post: {msg[:120]}")

    is_video    = post.is_video
    is_carousel = post.typename == 'GraphSidecar'

    # ── Build slides ──────────────────────────────────────────
    slides = []
    if is_carousel:
        try:
            for i, node in enumerate(post.get_sidecar_nodes()):
                # Use proxy URL so browser can load the thumbnail
                raw_thumb = node.video_url if node.is_video else node.display_url
                slides.append({
                    'index': i,
                    'type': 'video' if node.is_video else 'image',
                    # Proxy through our backend so browser can load it
                    'thumbnail': f'/api/proxy-image?url={requests.utils.quote(raw_thumb, safe="")}',
                    'url': url,
                    'video_url': node.video_url if node.is_video else None,
                    'image_url': node.display_url,
                })
        except Exception:
            pass

    # ── Main thumbnail ────────────────────────────────────────
    raw_thumb_url = post.url
    if is_video:
        raw_thumb_url = post.video_thumbnail_url or post.url
    # Proxy it so the <img> tag in the browser can load it
    thumbnail = f'/api/proxy-image?url={requests.utils.quote(raw_thumb_url, safe="")}'

    # ── Caption ───────────────────────────────────────────────
    caption_text = post.caption or ''
    hashtags  = [t.lower() for t in (post.caption_hashtags or [])]
    mentions  = [m.lower() for m in (post.caption_mentions or [])]
    urls_cap  = re.findall(r'https?://[^\s\)\]\"\']+', caption_text)

    caption_data = {
        'full_text':  caption_text,
        'hashtags':   hashtags,
        'mentions':   mentions,
        'urls':       urls_cap[:10],
        'word_count': len(re.sub(r'[#@]\w+', '', caption_text).split()) if caption_text.strip() else 0,
        'char_count': len(caption_text),
        'chapters':   [],
    }

    upload_date = post.date_utc.strftime('%Y%m%d') if post.date_utc else None

    # ── Formats ───────────────────────────────────────────────
    if is_carousel:
        slide_count = len(slides) if slides else 1
        has_video   = any(s['type'] == 'video' for s in slides)
        formats     = _build_carousel_formats(slides, has_video, slide_count)
        content_type = 'carousel'
    elif is_video:
        formats = [
            {'id': 'ig_video', 'label': 'Download Video (MP4)', 'ext': 'mp4', 'type': 'video'},
        ]
        content_type = 'post'
    else:
        formats = [
            {'id': 'ig_image',    'label': 'Download Image (JPG)',  'ext': 'jpg',  'type': 'image'},
            {'id': 'ig_image_webp','label': 'Download Image (WebP)', 'ext': 'webp', 'type': 'image'},
        ]
        content_type = 'post'

    return {
        'title':            caption_text[:80] or f'Instagram Post by @{post.owner_username}',
        'thumbnail':        thumbnail,
        'duration':         None,
        'uploader':         post.owner_username,
        'uploader_url':     f'https://www.instagram.com/{post.owner_username}/',
        'view_count':       post.video_view_count if is_video else None,
        'like_count':       post.likes,
        'comment_count':    post.comments,
        'upload_date':      upload_date,
        'upload_timestamp': int(post.date_utc.timestamp()) if post.date_utc else None,
        'caption':          caption_data,
        'description':      caption_text[:200],
        'platform':         'instagram',
        'content_type':     content_type,
        'is_carousel':      is_carousel,
        'slide_count':      len(slides) if is_carousel else 1,
        'slides':           slides if is_carousel else [],
        'formats':          formats,
        'webpage_url':      url,
        'tags':             hashtags,
        # Internal keys for download functions
        '_shortcode':       shortcode,
        '_is_video':        is_video,
        '_video_url':       post.video_url if is_video else None,
        '_image_url':       post.url,
    }


def _build_carousel_formats(slides: list, has_video: bool, slide_count: int) -> list:
    formats = [{
        'id':          'carousel_zip',
        'label':       f'Download All ({slide_count} files) — ZIP',
        'ext':         'zip',
        'type':        'archive',
        'slide_count': slide_count,
    }]
    for i, slide in enumerate(slides):
        is_vid = slide['type'] == 'video'
        formats.append({
            'id':          f'slide_{i}',
            'label':       f'Slide {i+1} — {"Video (MP4)" if is_vid else "Image (JPG)"}',
            'ext':         'mp4' if is_vid else 'jpg',
            'type':        'video' if is_vid else 'image',
            'slide_index': i,
        })
    return formats


# ─────────────────────────────────────────────────────────────
#  DOWNLOADS
# ─────────────────────────────────────────────────────────────

def download_post(url: str, format_id: str) -> dict:
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    shortcode = _shortcode_from_url(url)
    if not shortcode:
        raise ValueError("Could not extract shortcode from URL")

    timestamp = str(int(time.time() * 1000))

    try:
        L = _get_loader()
        post = instaloader.Post.from_shortcode(L.context, shortcode)
    except instaloader.exceptions.LoginRequiredException:
        raise PermissionError("This Instagram post is private or requires login.")
    except Exception as e:
        raise ValueError(f"Could not load Instagram post: {str(e)[:120]}")

    if format_id == 'ig_image':
        return _dl_image(post.url, timestamp, f'instagram_{shortcode}', fmt='jpg')

    if format_id == 'ig_image_webp':
        return _dl_image(post.url, timestamp, f'instagram_{shortcode}', fmt='webp')

    if format_id == 'ig_video':
        return _dl_video(post.video_url, timestamp, f'instagram_{shortcode}')

    if format_id == 'carousel_zip':
        return _dl_carousel_zip(post, shortcode, timestamp)

    if format_id.startswith('slide_'):
        idx = int(format_id.split('_')[1])
        return _dl_carousel_slide(post, idx, shortcode, timestamp)

    # Fallback
    if post.is_video:
        return _dl_video(post.video_url, timestamp, f'instagram_{shortcode}')
    return _dl_image(post.url, timestamp, f'instagram_{shortcode}', fmt='jpg')


def _dl_image(image_url: str, timestamp: str, name: str, fmt: str = 'jpg') -> dict:
    """
    Download and force-convert an Instagram image to JPG or WebP via Pillow.
    This eliminates JFIF/WebP issues — output is always a clean standard file.
    """
    if not image_url:
        raise ValueError("No image URL available for this post")

    resp = requests.get(image_url, timeout=30, headers=IG_DL_HEADERS)
    resp.raise_for_status()

    raw = resp.content

    if fmt == 'webp':
        converted = _convert_to_webp(raw)
        ext = 'webp'
        mime = 'image/webp'
    else:
        converted = _convert_to_jpg(raw)
        ext = 'jpg'
        mime = 'image/jpeg'

    filepath = os.path.join(DOWNLOAD_FOLDER, f'{timestamp}_{name}.{ext}')
    with open(filepath, 'wb') as f:
        f.write(converted)

    return {
        'filepath': filepath,
        'filename': f'{name}.{ext}',
        'ext':      ext,
        'mime_type': mime,
    }


def _dl_video(video_url: str, timestamp: str, name: str) -> dict:
    if not video_url:
        raise ValueError("No video URL available for this post")

    resp = requests.get(video_url, timeout=60, headers=IG_DL_HEADERS, stream=True)
    resp.raise_for_status()

    filepath = os.path.join(DOWNLOAD_FOLDER, f'{timestamp}_{name}.mp4')
    with open(filepath, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

    return {
        'filepath': filepath,
        'filename': f'{name}.mp4',
        'ext':      'mp4',
        'mime_type': 'video/mp4',
    }


def _dl_carousel_zip(post, shortcode: str, timestamp: str) -> dict:
    zip_path  = os.path.join(DOWNLOAD_FOLDER, f'{timestamp}_carousel.zip')
    tmp_files = []

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        try:
            for i, node in enumerate(post.get_sidecar_nodes()):
                slide_ts = f'{timestamp}_{i}'
                try:
                    if node.is_video:
                        r = _dl_video(node.video_url, slide_ts, f'slide_{i+1}')
                        zf.write(r['filepath'], f'slide_{i+1:02d}.mp4')
                    else:
                        r = _dl_image(node.display_url, slide_ts, f'slide_{i+1}', fmt='jpg')
                        zf.write(r['filepath'], f'slide_{i+1:02d}.jpg')
                    tmp_files.append(r['filepath'])
                except Exception:
                    continue
        except Exception as e:
            raise ValueError(f"Failed to download carousel: {str(e)[:100]}")

    for fp in tmp_files:
        try:
            os.remove(fp)
        except Exception:
            pass

    if not zipfile.ZipFile(zip_path).namelist():
        raise ValueError("Could not download any slides from this carousel")

    return {
        'filepath': zip_path,
        'filename': f'instagram_carousel_{shortcode}.zip',
        'ext':      'zip',
        'mime_type': 'application/zip',
    }


def _dl_carousel_slide(post, idx: int, shortcode: str, timestamp: str) -> dict:
    slides = list(post.get_sidecar_nodes())
    if idx >= len(slides):
        raise ValueError(f"Slide {idx+1} not found (post has {len(slides)} slides)")

    node = slides[idx]
    name = f'instagram_{shortcode}_slide{idx+1}'

    if node.is_video:
        return _dl_video(node.video_url, timestamp, name)
    return _dl_image(node.display_url, timestamp, name, fmt='jpg')
