import re
from urllib.parse import urlparse


PLATFORM_PATTERNS = {
    'youtube': [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+',
        r'(?:https?://)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
    ],
    'instagram': [
        r'(?:https?://)?(?:www\.)?instagram\.com/p/[\w-]+',
        r'(?:https?://)?(?:www\.)?instagram\.com/reel/[\w-]+',
        r'(?:https?://)?(?:www\.)?instagram\.com/reels/[\w-]+',
        r'(?:https?://)?(?:www\.)?instagram\.com/tv/[\w-]+',
        r'(?:https?://)?(?:www\.)?instagram\.com/[\w.]+/?$',
    ],
    'tiktok': [
        r'(?:https?://)?(?:www\.)?tiktok\.com/@[\w.]+/video/\d+',
        r'(?:https?://)?(?:vm\.)?tiktok\.com/[\w]+',
        r'(?:https?://)?(?:www\.)?tiktok\.com/t/[\w]+',
    ],
    'facebook': [
        r'(?:https?://)?(?:www\.|m\.|web\.)?facebook\.com/.*?/videos/[\w-]+',
        r'(?:https?://)?(?:www\.|m\.)?facebook\.com/video\.php',
        r'(?:https?://)?(?:www\.|m\.)?facebook\.com/watch',
        r'(?:https?://)?(?:www\.|m\.)?facebook\.com/reel/[\w-]+',
        r'(?:https?://)?(?:www\.|m\.)?facebook\.com/share/[rvp]/[\w-]+',
        r'(?:https?://)?fb\.watch/[\w-]+',
        r'(?:https?://)?(?:www\.|m\.)?facebook\.com/[\w.]+/posts/[\w-]+',
        r'(?:https?://)?(?:www\.|m\.)?facebook\.com/photo',
        r'(?:https?://)?(?:www\.|m\.)?facebook\.com/[\w.]+/photos/[\w./-]+',
    ],
    'pinterest': [
        r'(?:https?://)?(?:www\.)?pinterest\.com/pin/[\w-]+',
        r'(?:https?://)?(?:www\.)?pinterest\.[a-z.]+/pin/[\w-]+',
        r'(?:https?://)?pin\.it/[\w-]+',
        r'(?:https?://)?(?:www\.)?pinterest\.com/[\w-]+/[\w-]+',
    ],
}

CONTENT_TYPE_PATTERNS = {
    'youtube_short':      r'(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+',
    'instagram_reel':     r'(?:https?://)?(?:www\.)?instagram\.com/(?:reel|reels)/[\w-]+',
    'instagram_post':     r'(?:https?://)?(?:www\.)?instagram\.com/p/[\w-]+',
    'instagram_profile':  r'(?:https?://)?(?:www\.)?instagram\.com/[\w.]+/?(?:\?.*)?$',
    'instagram_tv':       r'(?:https?://)?(?:www\.)?instagram\.com/tv/[\w-]+',
    'facebook_reel':      r'(?:https?://)?(?:www\.|m\.)?facebook\.com/reel/[\w-]+',
    'facebook_video':     r'(?:https?://)?(?:www\.|m\.|web\.)?facebook\.com/.*?/videos/[\w-]+|(?:https?://)?fb\.watch/|(?:https?://)?(?:www\.|m\.)?facebook\.com/watch|(?:https?://)?(?:www\.|m\.)?facebook\.com/share/[rvp]/[\w-]+',
    'facebook_photo':     r'(?:https?://)?(?:www\.|m\.)?facebook\.com/photo|(?:https?://)?(?:www\.|m\.)?facebook\.com/[\w.]+/photos/',
    'pinterest_pin':      r'(?:https?://)?(?:www\.)?pinterest\.[a-z.]+/pin/[\w-]+|(?:https?://)?pin\.it/[\w-]+',
    'pinterest_board':    r'(?:https?://)?(?:www\.)?pinterest\.[a-z.]+/[\w-]+/[\w-]+',
}


def detect_platform(url: str) -> str | None:
    url = url.strip()
    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return platform
    return None


def detect_content_type(url: str, platform: str) -> str:
    url = url.strip()

    if platform == 'youtube':
        if re.search(CONTENT_TYPE_PATTERNS['youtube_short'], url, re.IGNORECASE):
            return 'short'
        return 'video'

    if platform == 'instagram':
        if re.search(CONTENT_TYPE_PATTERNS['instagram_reel'], url, re.IGNORECASE):
            return 'reel'
        if re.search(CONTENT_TYPE_PATTERNS['instagram_post'], url, re.IGNORECASE):
            return 'post'
        if re.search(CONTENT_TYPE_PATTERNS['instagram_tv'], url, re.IGNORECASE):
            return 'tv'
        path = urlparse(url).path.strip('/')
        if path and '/' not in path and not any(path.startswith(x) for x in ['p/', 'reel/', 'tv/']):
            return 'profile'
        return 'post'

    if platform == 'tiktok':
        return 'video'

    if platform == 'facebook':
        if re.search(CONTENT_TYPE_PATTERNS['facebook_reel'], url, re.IGNORECASE):
            return 'reel'
        if re.search(CONTENT_TYPE_PATTERNS['facebook_photo'], url, re.IGNORECASE):
            return 'photo'
        # Detect generic /share/p/ posts as "post" rather than assuming video
        if '/share/p/' in url:
            return 'post'
        return 'video'

    if platform == 'pinterest':
        if re.search(CONTENT_TYPE_PATTERNS['pinterest_pin'], url, re.IGNORECASE):
            return 'pin'
        return 'board'

    return 'video'


def validate_url(url: str) -> tuple[bool, str]:
    if not url or not url.strip():
        return False, "URL cannot be empty"

    url = url.strip()

    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = 'https://' + url
            parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False, "Only HTTP/HTTPS URLs are supported"
    except Exception:
        return False, "Invalid URL format"

    platform = detect_platform(url)
    if not platform:
        return False, "Unsupported platform. Please use YouTube, Instagram, TikTok, Facebook, or Pinterest URLs."

    dangerous_patterns = [r'javascript:', r'data:', r'file://', r'<script', r'onclick']
    for pattern in dangerous_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return False, "Invalid URL"

    return True, url


def sanitize_filename(name: str) -> str:
    if not name:
        return 'download'
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    name = name[:100]
    return name or 'download'
