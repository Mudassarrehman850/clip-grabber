from flask import Blueprint, request, jsonify, send_file
from utils.url_detector import detect_platform, detect_content_type, validate_url, sanitize_filename
from services.ytdlp_service import download_media, cleanup_old_files
import os
import threading

download_bp = Blueprint('download', __name__)

_cleanup_counter = 0


def _maybe_cleanup():
    global _cleanup_counter
    _cleanup_counter += 1
    if _cleanup_counter % 10 == 0:
        t = threading.Thread(target=cleanup_old_files, daemon=True)
        t.start()


@download_bp.route('/download', methods=['POST'])
def download():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    url = data.get('url', '').strip()
    format_id = data.get('format_id', 'video_best').strip()
    title = data.get('title', 'download').strip()
    slide_index = data.get('slide_index')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Validate allowed format IDs (static + dynamic slide_N)
    static_formats = {
        'video_best', 'video_720', 'audio_mp3', 'thumbnail',
        'video_nowm', 'video_sd', 'image', 'ig_image', 'ig_image_webp', 'ig_video', 'fb_image', 'pin_image', 'profile_pic', 'carousel_zip'
    }
    is_slide_format = format_id.startswith('slide_') and format_id[6:].isdigit()
    if format_id not in static_formats and not is_slide_format:
        return jsonify({'error': 'Invalid format requested'}), 400

    if is_slide_format:
        slide_index = int(format_id[6:])

    is_valid, result = validate_url(url)
    if not is_valid:
        return jsonify({'error': result}), 422

    clean_url = result
    platform = detect_platform(clean_url)
    if not platform:
        return jsonify({'error': 'Unsupported platform'}), 422

    content_type = detect_content_type(clean_url, platform)

    try:
        _maybe_cleanup()
        file_info = download_media(
            clean_url, format_id, platform, content_type,
            slide_index=slide_index
        )

        filepath = file_info['filepath']
        if not os.path.exists(filepath):
            return jsonify({'error': 'Downloaded file not found on server'}), 500

        safe_title = sanitize_filename(title)
        if is_slide_format:
            download_name = f'{safe_title}_slide{slide_index + 1}.{file_info["ext"]}'
        elif format_id == 'carousel_zip':
            download_name = f'{safe_title}_all.zip'
        else:
            download_name = f'{safe_title}.{file_info["ext"]}' if safe_title != 'download' else file_info['filename']

        def remove_after_send(path):
            try:
                os.remove(path)
            except Exception:
                pass

        response = send_file(
            filepath,
            mimetype=file_info['mime_type'],
            as_attachment=True,
            download_name=download_name,
        )

        @response.call_on_close
        def cleanup():
            remove_after_send(filepath)

        return response

    except PermissionError as e:
        return jsonify({'error': str(e), 'code': 'PRIVATE_CONTENT'}), 403
    except ValueError as e:
        return jsonify({'error': str(e), 'code': 'DOWNLOAD_FAILED'}), 400
    except FileNotFoundError:
        return jsonify({'error': 'File not found after download', 'code': 'FILE_NOT_FOUND'}), 500
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)[:100]}', 'code': 'UNKNOWN'}), 500
