from utils.url_detector import detect_platform, detect_content_type, validate_url, sanitize_filename


def test_detect_platform_youtube():
    assert detect_platform('https://www.youtube.com/watch?v=abc123') == 'youtube'
    assert detect_platform('https://youtu.be/abc123') == 'youtube'


def test_detect_platform_instagram():
    assert detect_platform('https://www.instagram.com/p/Cabc123/') == 'instagram'
    assert detect_platform('https://www.instagram.com/reel/Cabc123/') == 'instagram'


def test_detect_platform_unsupported():
    assert detect_platform('https://example.com/video') is None


def test_detect_content_type_youtube_short():
    url = 'https://www.youtube.com/shorts/abc123'
    assert detect_content_type(url, 'youtube') == 'short'


def test_detect_content_type_youtube_video():
    url = 'https://www.youtube.com/watch?v=abc123'
    assert detect_content_type(url, 'youtube') == 'video'


def test_validate_url_empty():
    ok, msg = validate_url('')
    assert ok is False
    assert 'empty' in msg.lower()


def test_validate_url_adds_scheme():
    ok, cleaned = validate_url('youtube.com/watch?v=abc123')
    assert ok is True
    assert cleaned.startswith('https://')


def test_validate_url_rejects_javascript_scheme():
    ok, msg = validate_url('javascript:alert(1)')
    assert ok is False


def test_validate_url_rejects_unsupported_platform():
    ok, msg = validate_url('https://example.com/video')
    assert ok is False


def test_sanitize_filename_strips_dangerous_chars():
    assert sanitize_filename('my<video>:name?.mp4') == 'myvideoname.mp4'


def test_sanitize_filename_empty_defaults():
    assert sanitize_filename('') == 'download'


def test_sanitize_filename_truncates():
    long_name = 'a' * 300
    assert len(sanitize_filename(long_name)) <= 100
