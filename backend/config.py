import os

DOWNLOAD_FOLDER = os.environ.get('DOWNLOAD_FOLDER', '/tmp/clip_grabber_cache')
JOBS_DB_PATH = os.path.join(DOWNLOAD_FOLDER, 'jobs.db')

EXTRACTION_TIMEOUT = int(os.environ.get('EXTRACTION_TIMEOUT', '45'))
DOWNLOAD_TIMEOUT = int(os.environ.get('DOWNLOAD_TIMEOUT', '300'))
JOB_MAX_AGE_SECONDS = int(os.environ.get('JOB_MAX_AGE_SECONDS', '3600'))
METADATA_CACHE_TTL = int(os.environ.get('METADATA_CACHE_TTL', '600'))
DOWNLOAD_WORKERS = int(os.environ.get('DOWNLOAD_WORKERS', '3'))

YTDLP_PROXY = os.environ.get('YTDLP_PROXY') or None

CORS_ORIGIN = os.environ.get('CORS_ORIGIN', '*')

COOKIE_ENV_VARS = {
    'youtube': 'YT_COOKIES',
    'instagram': 'IG_COOKIES',
    'tiktok': 'TIKTOK_COOKIES',
    'facebook': 'FB_COOKIES',
}
