import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.get_json() == {'status': 'ok'}


def test_analyze_requires_json_body(client):
    resp = client.post('/api/analyze', data='not json', content_type='text/plain')
    assert resp.status_code == 400


def test_analyze_rejects_unsupported_platform(client):
    resp = client.post('/api/analyze', json={'url': 'https://example.com/video'})
    assert resp.status_code == 422


def test_analyze_success_mocked(client, monkeypatch):
    fake_metadata = {
        'title': 'Test Video',
        'thumbnail': 'https://example.com/thumb.jpg',
        'duration': '1:00',
        'uploader': 'tester',
        'formats': [{'id': 'video_best', 'label': 'Video (Best)', 'ext': 'mp4', 'type': 'video'}],
        'caption': {'full_text': '', 'hashtags': [], 'mentions': [], 'urls': [], 'word_count': 0, 'char_count': 0, 'chapters': []},
    }
    monkeypatch.setattr('routes.analyze.extract_metadata', lambda url, platform, content_type: fake_metadata)

    resp = client.post('/api/analyze', json={'url': 'https://www.youtube.com/watch?v=abc123'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['data']['title'] == 'Test Video'
    assert data['platform'] == 'youtube'


def test_analyze_maps_permission_error_to_403(client, monkeypatch):
    def raise_private(url, platform, content_type):
        raise PermissionError('This content is private.')

    monkeypatch.setattr('routes.analyze.extract_metadata', raise_private)

    resp = client.post('/api/analyze', json={'url': 'https://www.youtube.com/watch?v=abc123'})
    assert resp.status_code == 403
    assert resp.get_json()['code'] == 'PRIVATE_CONTENT'


def test_download_rejects_invalid_format(client):
    resp = client.post('/api/download', json={'url': 'https://www.youtube.com/watch?v=abc123', 'format_id': 'not_a_real_format'})
    assert resp.status_code == 400


def test_download_job_lifecycle_mocked(client, monkeypatch, tmp_path):
    fake_file = tmp_path / 'video.mp4'
    fake_file.write_bytes(b'fake video bytes')

    def fake_download_media(url, format_id, platform, content_type, slide_index=None, progress_cb=None):
        if progress_cb:
            progress_cb(50, 'halfway')
        return {'filepath': str(fake_file), 'filename': 'video.mp4', 'ext': 'mp4', 'mime_type': 'video/mp4'}

    monkeypatch.setattr('routes.download.download_media', fake_download_media)

    resp = client.post('/api/download', json={'url': 'https://www.youtube.com/watch?v=abc123', 'format_id': 'video_best', 'title': 'my video'})
    assert resp.status_code == 202
    job_id = resp.get_json()['job_id']

    import time
    status = None
    for _ in range(50):
        status_resp = client.get(f'/api/download/status/{job_id}')
        status = status_resp.get_json()
        if status['status'] in ('done', 'error'):
            break
        time.sleep(0.05)

    assert status['status'] == 'done', status

    result_resp = client.get(f'/api/download/result/{job_id}')
    assert result_resp.status_code == 200
    assert result_resp.headers['Content-Disposition'].startswith('attachment')


def test_download_status_unknown_job_404(client):
    resp = client.get('/api/download/status/does-not-exist')
    assert resp.status_code == 404
