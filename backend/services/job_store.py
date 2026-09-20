"""
job_store.py
Lightweight SQLite-backed background job tracker for downloads, plus the
thread pool that actually runs them. Keeps /api/download from blocking a
web worker for the whole duration of a yt-dlp download, and gives the
frontend real progress to poll instead of only HTTP transfer progress.
"""

import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from config import JOBS_DB_PATH, DOWNLOAD_WORKERS, DOWNLOAD_FOLDER, DOWNLOAD_TIMEOUT
from utils.timeout import run_with_timeout, OperationTimeoutError

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_executor = ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS, thread_name_prefix='download')


def _get_conn() -> sqlite3.Connection:
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    conn = sqlite3.connect(JOBS_DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _lock, _get_conn() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                progress REAL DEFAULT 0,
                message TEXT,
                result_path TEXT,
                filename TEXT,
                mime_type TEXT,
                error TEXT,
                error_code TEXT,
                created_at REAL,
                updated_at REAL,
                consumed INTEGER DEFAULT 0
            )
        ''')
        conn.commit()


def create_job() -> str:
    job_id = uuid.uuid4().hex
    now = time.time()
    with _lock, _get_conn() as conn:
        conn.execute(
            'INSERT INTO jobs (id, status, progress, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
            (job_id, 'queued', 0, now, now),
        )
        conn.commit()
    return job_id


def update_job(job_id: str, **fields):
    if not fields:
        return
    fields['updated_at'] = time.time()
    columns = ', '.join(f'{k} = ?' for k in fields)
    values = list(fields.values()) + [job_id]
    with _lock, _get_conn() as conn:
        conn.execute(f'UPDATE jobs SET {columns} WHERE id = ?', values)
        conn.commit()


def get_job(job_id: str) -> dict | None:
    with _lock, _get_conn() as conn:
        row = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
        return dict(row) if row else None


def cleanup_old_jobs(max_age_seconds: int = 3600):
    cutoff = time.time() - max_age_seconds
    with _lock, _get_conn() as conn:
        rows = conn.execute('SELECT id, result_path FROM jobs WHERE created_at < ?', (cutoff,)).fetchall()
        for row in rows:
            if row['result_path'] and os.path.exists(row['result_path']):
                try:
                    os.remove(row['result_path'])
                except OSError as e:
                    logger.warning('Failed to remove stale job file %s: %s', row['result_path'], e)
        conn.execute('DELETE FROM jobs WHERE created_at < ?', (cutoff,))
        conn.commit()


def submit_download(job_id: str, func, *args, **kwargs):
    """Run `func(*args, **kwargs, progress_cb=...)` in the background and record the outcome on the job."""

    def _progress_cb(percent: float, message: str = ''):
        update_job(job_id, progress=percent, message=message)

    def _run():
        update_job(job_id, status='running', progress=0)
        try:
            result = run_with_timeout(func, *args, progress_cb=_progress_cb, timeout=DOWNLOAD_TIMEOUT, **kwargs)
            update_job(
                job_id,
                status='done',
                progress=100,
                result_path=result['filepath'],
                filename=result['filename'],
                mime_type=result['mime_type'],
            )
        except PermissionError as e:
            update_job(job_id, status='error', error=str(e), error_code='PRIVATE_CONTENT')
        except ValueError as e:
            update_job(job_id, status='error', error=str(e), error_code='DOWNLOAD_FAILED')
        except FileNotFoundError as e:
            update_job(job_id, status='error', error=str(e), error_code='FILE_NOT_FOUND')
        except OperationTimeoutError:
            logger.warning('Download job %s timed out after %ss', job_id, DOWNLOAD_TIMEOUT)
            update_job(job_id, status='error', error='Download took too long and timed out.', error_code='TIMEOUT')
        except Exception:
            logger.exception('Unhandled error running download job %s', job_id)
            update_job(job_id, status='error', error='Download failed unexpectedly', error_code='UNKNOWN')

    _executor.submit(_run)
