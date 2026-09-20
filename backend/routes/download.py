import logging
import os

from flask import Blueprint, request, jsonify, send_file

from extensions import limiter
from utils.url_detector import detect_platform, detect_content_type, validate_url, sanitize_filename
from services.ytdlp_service import download_media
from services import job_store

logger = logging.getLogger(__name__)

download_bp = Blueprint('download', __name__)

STATIC_FORMATS = {
    'video_best', 'video_720', 'audio_mp3', 'audio_320', 'thumbnail',
    'video_nowm', 'video_sd', 'image', 'ig_image', 'ig_image_webp', 'ig_video',
    'fb_image', 'pin_image', 'og_image', 'profile_pic', 'carousel_zip',
}

# job_id -> requested display name/format, kept only for building the download filename at result time
_job_meta: dict[str, dict] = {}


def _is_slide_format(format_id: str) -> bool:
    return format_id.startswith('slide_') and format_id[6:].isdigit()


@download_bp.route('/download', methods=['POST'])
@limiter.limit("10 per minute")
def start_download():
    """Kick off a download as a background job and return its id immediately."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    url = data.get('url', '').strip()
    format_id = data.get('format_id', 'video_best').strip()
    title = data.get('title', 'download').strip()
    slide_index = data.get('slide_index')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    if format_id not in STATIC_FORMATS and not _is_slide_format(format_id):
        return jsonify({'error': 'Invalid format requested'}), 400

    if _is_slide_format(format_id):
        slide_index = int(format_id[6:])

    is_valid, result = validate_url(url)
    if not is_valid:
        return jsonify({'error': result}), 422

    clean_url = result
    platform = detect_platform(clean_url)
    if not platform:
        return jsonify({'error': 'Unsupported platform'}), 422

    content_type = detect_content_type(clean_url, platform)

    job_id = job_store.create_job()
    _job_meta[job_id] = {
        'title': title,
        'format_id': format_id,
        'is_slide_format': _is_slide_format(format_id),
        'slide_index': slide_index,
    }

    job_store.submit_download(
        job_id, download_media,
        clean_url, format_id, platform, content_type,
        slide_index=slide_index,
    )

    logger.info('Started download job %s for %s (%s, format=%s)', job_id, platform, clean_url, format_id)
    return jsonify({'job_id': job_id, 'status': 'queued'}), 202


@download_bp.route('/download/status/<job_id>', methods=['GET'])
@limiter.limit("120 per minute")
def download_status(job_id):
    job = job_store.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    response = {
        'job_id': job_id,
        'status': job['status'],
        'progress': job['progress'],
        'message': job['message'],
    }
    if job['status'] == 'error':
        response['error'] = job['error']
        response['code'] = job['error_code']
    return jsonify(response), 200


@download_bp.route('/download/result/<job_id>', methods=['GET'])
@limiter.limit("30 per minute")
def download_result(job_id):
    job = job_store.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    if job['status'] != 'done':
        return jsonify({'error': 'Job is not finished yet', 'status': job['status']}), 409

    filepath = job['result_path']
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'Downloaded file not found on server'}), 500

    meta = _job_meta.pop(job_id, {})
    safe_title = sanitize_filename(meta.get('title', 'download'))
    format_id = meta.get('format_id', '')
    ext = job['filename'].rsplit('.', 1)[-1] if '.' in (job['filename'] or '') else 'bin'

    if meta.get('is_slide_format'):
        download_name = f"{safe_title}_slide{(meta.get('slide_index') or 0) + 1}.{ext}"
    elif format_id == 'carousel_zip':
        download_name = f'{safe_title}_all.zip'
    else:
        download_name = f'{safe_title}.{ext}' if safe_title != 'download' else job['filename']

    def _cleanup(path):
        try:
            os.remove(path)
        except OSError as e:
            logger.warning('Failed to remove downloaded file %s: %s', path, e)

    response = send_file(
        filepath,
        mimetype=job['mime_type'],
        as_attachment=True,
        download_name=download_name,
    )

    @response.call_on_close
    def cleanup():
        _cleanup(filepath)
        job_store.update_job(job_id, consumed=1)

    return response
