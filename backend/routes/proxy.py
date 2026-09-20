import logging

from flask import Blueprint, request, Response, jsonify
import requests

logger = logging.getLogger(__name__)

proxy_bp = Blueprint('proxy', __name__)

# Instagram CDN headers needed to bypass hotlink protection
IG_FETCH_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Referer': 'https://www.instagram.com/',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site',
}

ALLOWED_DOMAINS = (
    'cdninstagram.com',
    'instagram.com',
    'fbcdn.net',
    'scontent',
    'fbsbx.com',
)


def _is_safe_image_url(url: str) -> bool:
    """Only proxy known Instagram/Facebook CDN domains."""
    return any(d in url for d in ALLOWED_DOMAINS)


@proxy_bp.route('/proxy-image', methods=['GET'])
def proxy_image():
    """
    Proxy an Instagram CDN image to the browser.
    Usage: GET /api/proxy-image?url=https://cdninstagram.com/...
    """
    img_url = request.args.get('url', '').strip()

    if not img_url:
        return jsonify({'error': 'url parameter required'}), 400

    if not _is_safe_image_url(img_url):
        return jsonify({'error': 'URL not from an allowed domain'}), 403

    try:
        resp = requests.get(
            img_url,
            headers=IG_FETCH_HEADERS,
            timeout=15,
            stream=True,
        )
        resp.raise_for_status()

        content_type = resp.headers.get('Content-Type', 'image/jpeg')

        # Stream back to browser
        def generate():
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        return Response(
            generate(),
            status=200,
            content_type=content_type,
            headers={
                'Cache-Control': 'public, max-age=3600',
                'Access-Control-Allow-Origin': '*',
            },
        )

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Image fetch timed out'}), 504
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'CDN returned {e.response.status_code}'}), 502
    except Exception as e:
        logger.warning('Proxy image fetch failed for %s: %s', img_url, e)
        return jsonify({'error': f'Proxy error: {str(e)[:80]}'}), 500
