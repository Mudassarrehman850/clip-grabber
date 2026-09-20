import logging

from flask import Blueprint, request, jsonify, Response
from utils.url_detector import detect_platform, detect_content_type, validate_url
from utils.timeout import run_with_timeout, OperationTimeoutError
from services.ytdlp_service import extract_metadata
from config import EXTRACTION_TIMEOUT

logger = logging.getLogger(__name__)

caption_bp = Blueprint('caption', __name__)


@caption_bp.route('/caption', methods=['POST'])
def get_caption():
    """
    Returns the full structured caption for a URL.
    Useful for copy-paste without downloading the media.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    is_valid, result = validate_url(url)
    if not is_valid:
        return jsonify({'error': result}), 422

    clean_url = result
    platform = detect_platform(clean_url)
    if not platform:
        return jsonify({'error': 'Unsupported platform'}), 422

    content_type = detect_content_type(clean_url, platform)

    try:
        metadata = run_with_timeout(extract_metadata, clean_url, platform, content_type, timeout=EXTRACTION_TIMEOUT)
        caption = metadata.get('caption', {})

        return jsonify({
            'success': True,
            'platform': platform,
            'uploader': metadata.get('uploader'),
            'caption': caption,
        }), 200

    except PermissionError as e:
        return jsonify({'error': str(e), 'code': 'PRIVATE_CONTENT'}), 403
    except ValueError as e:
        return jsonify({'error': str(e), 'code': 'EXTRACTION_FAILED'}), 400
    except OperationTimeoutError:
        logger.warning('Caption fetch timed out for %s', clean_url)
        return jsonify({'error': 'This took too long. Please try again.', 'code': 'TIMEOUT'}), 504
    except Exception as e:
        logger.exception('Unexpected error fetching caption for %s', clean_url)
        return jsonify({'error': f'Failed: {str(e)[:100]}', 'code': 'UNKNOWN'}), 500


@caption_bp.route('/caption/export', methods=['POST'])
def export_caption():
    """Export caption as a plain .txt file download."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    is_valid, result = validate_url(url)
    if not is_valid:
        return jsonify({'error': result}), 422

    clean_url = result
    platform = detect_platform(clean_url)
    if not platform:
        return jsonify({'error': 'Unsupported platform'}), 422

    content_type = detect_content_type(clean_url, platform)

    try:
        metadata = run_with_timeout(extract_metadata, clean_url, platform, content_type, timeout=EXTRACTION_TIMEOUT)
        caption = metadata.get('caption', {})
        title = metadata.get('title', 'untitled')
        uploader = metadata.get('uploader', '')

        lines = []
        lines.append(f"Title: {title}")
        lines.append(f"Author: {uploader}")
        lines.append(f"Platform: {platform.capitalize()}")
        if metadata.get('upload_date'):
            d = metadata['upload_date']
            lines.append(f"Date: {d[:4]}-{d[4:6]}-{d[6:]}")
        lines.append(f"URL: {clean_url}")
        lines.append("")
        lines.append("─" * 60)
        lines.append("CAPTION / DESCRIPTION")
        lines.append("─" * 60)
        lines.append(caption.get('full_text', '(No caption)'))
        lines.append("")

        if caption.get('hashtags'):
            lines.append("─" * 60)
            lines.append("HASHTAGS")
            lines.append("─" * 60)
            lines.append("  ".join(f"#{h}" for h in caption['hashtags']))
            lines.append("")

        if caption.get('mentions'):
            lines.append("─" * 60)
            lines.append("MENTIONS")
            lines.append("─" * 60)
            lines.append("  ".join(f"@{m}" for m in caption['mentions']))
            lines.append("")

        if caption.get('chapters'):
            lines.append("─" * 60)
            lines.append("CHAPTERS")
            lines.append("─" * 60)
            for ch in caption['chapters']:
                lines.append(f"  {ch['start_time_str']}  {ch['title']}")
            lines.append("")

        if caption.get('urls'):
            lines.append("─" * 60)
            lines.append("LINKS IN CAPTION")
            lines.append("─" * 60)
            for u in caption['urls']:
                lines.append(f"  {u}")
            lines.append("")

        txt = "\n".join(lines)

        import re
        safe_title = re.sub(r'[^\w\s-]', '', title)[:40].strip().replace(' ', '_')
        filename = f'{safe_title}_caption.txt'

        return Response(
            txt,
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )

    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except OperationTimeoutError:
        logger.warning('Caption export timed out for %s', clean_url)
        return jsonify({'error': 'This took too long. Please try again.'}), 504
    except Exception as e:
        logger.exception('Unexpected error exporting caption for %s', clean_url)
        return jsonify({'error': f'Failed: {str(e)[:100]}'}), 500
