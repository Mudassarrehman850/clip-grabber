from flask import Blueprint, request, jsonify
from utils.url_detector import detect_platform, detect_content_type, validate_url
from services.ytdlp_service import extract_metadata

analyze_bp = Blueprint('analyze', __name__)


@analyze_bp.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Validate URL
    is_valid, result = validate_url(url)
    if not is_valid:
        return jsonify({'error': result}), 422

    clean_url = result  # validate_url returns cleaned URL

    # Detect platform
    platform = detect_platform(clean_url)
    if not platform:
        return jsonify({'error': 'Unsupported platform. Please use YouTube, Instagram, or TikTok URLs.'}), 422

    content_type = detect_content_type(clean_url, platform)

    try:
        metadata = extract_metadata(clean_url, platform, content_type)
        return jsonify({
            'success': True,
            'data': metadata,
            'url': clean_url,
            'platform': platform,
            'content_type': content_type,
        }), 200

    except PermissionError as e:
        return jsonify({'error': str(e), 'code': 'PRIVATE_CONTENT'}), 403

    except ValueError as e:
        return jsonify({'error': str(e), 'code': 'EXTRACTION_FAILED'}), 400

    except ConnectionError as e:
        return jsonify({'error': str(e), 'code': 'RATE_LIMITED'}), 429

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)[:100]}', 'code': 'UNKNOWN'}), 500
