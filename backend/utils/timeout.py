"""Bound the wall-clock time of a blocking call (yt-dlp extraction/download).

yt-dlp's own `socket_timeout`/`retries` only bound individual HTTP calls, not
the overall extraction, so a pathological page (or a platform quietly
stalling requests) can otherwise tie up a worker thread indefinitely. This
runs the call in a helper thread and gives up waiting after `timeout`
seconds — the helper thread may still be running afterwards, but the caller
is freed to respond with a clear timeout error instead of hanging.
"""

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

_pool = ThreadPoolExecutor(max_workers=8, thread_name_prefix='timeout-guard')


class OperationTimeoutError(TimeoutError):
    pass


def run_with_timeout(fn, *args, timeout: float, **kwargs):
    future = _pool.submit(fn, *args, **kwargs)
    try:
        return future.result(timeout=timeout)
    except FutureTimeoutError:
        raise OperationTimeoutError(f'Operation timed out after {timeout}s')
