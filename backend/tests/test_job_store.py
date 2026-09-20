import time

import pytest

from services import job_store


@pytest.fixture(autouse=True)
def _init_db():
    job_store.init_db()
    yield


def test_create_and_get_job():
    job_id = job_store.create_job()
    job = job_store.get_job(job_id)
    assert job is not None
    assert job['status'] == 'queued'
    assert job['progress'] == 0


def test_update_job():
    job_id = job_store.create_job()
    job_store.update_job(job_id, status='running', progress=42)
    job = job_store.get_job(job_id)
    assert job['status'] == 'running'
    assert job['progress'] == 42


def test_get_missing_job_returns_none():
    assert job_store.get_job('does-not-exist') is None


def test_submit_download_success_updates_job_to_done():
    job_id = job_store.create_job()

    def fake_download(progress_cb=None):
        progress_cb(50, 'halfway')
        return {'filepath': '/tmp/fake.mp4', 'filename': 'fake.mp4', 'mime_type': 'video/mp4'}

    job_store.submit_download(job_id, fake_download)

    for _ in range(50):
        job = job_store.get_job(job_id)
        if job['status'] in ('done', 'error'):
            break
        time.sleep(0.05)

    assert job['status'] == 'done'
    assert job['filename'] == 'fake.mp4'


def test_submit_download_failure_updates_job_to_error():
    job_id = job_store.create_job()

    def failing_download(progress_cb=None):
        raise ValueError('boom')

    job_store.submit_download(job_id, failing_download)

    for _ in range(50):
        job = job_store.get_job(job_id)
        if job['status'] in ('done', 'error'):
            break
        time.sleep(0.05)

    assert job['status'] == 'error'
    assert job['error_code'] == 'DOWNLOAD_FAILED'


def test_cleanup_old_jobs_removes_stale_rows():
    job_id = job_store.create_job()
    job_store.update_job(job_id, created_at=time.time() - 10000)
    job_store.cleanup_old_jobs(max_age_seconds=1)
    assert job_store.get_job(job_id) is None
