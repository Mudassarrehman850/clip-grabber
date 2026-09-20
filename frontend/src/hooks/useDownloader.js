import { useState, useCallback, useRef } from 'react';
import { analyzeUrl, startDownload, getDownloadStatus, fetchDownloadResult } from '../utils/api';
import { addToHistory, triggerBrowserDownload } from '../utils/helpers';

const POLL_INTERVAL_MS = 1000;
const MAX_POLL_ATTEMPTS = 300; // ~5 minutes

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function useDownloader() {
  const [state, setState] = useState({
    status: 'idle', // idle | analyzing | ready | downloading | done | error
    metadata: null,
    error: null,
    errorCode: null,
    downloadingFormatId: null,
    downloadProgress: 0,
    url: '',
  });

  const cancelledRef = useRef(false);

  const analyze = useCallback(async (url) => {
    if (!url.trim()) return;

    setState((s) => ({ ...s, status: 'analyzing', error: null, metadata: null, url }));

    try {
      const result = await analyzeUrl(url);
      if (result.success) {
        setState((s) => ({
          ...s,
          status: 'ready',
          metadata: result.data,
          url: result.url || url,
        }));
        addToHistory({
          url: result.url || url,
          title: result.data.title,
          thumbnail: result.data.thumbnail,
          platform: result.data.platform,
          timestamp: Date.now(),
        });
      } else {
        setState((s) => ({ ...s, status: 'error', error: result.error || 'Unknown error' }));
      }
    } catch (err) {
      const msg = err?.response?.data?.error || err.message || 'Failed to analyze URL';
      const code = err?.response?.data?.code || null;
      setState((s) => ({ ...s, status: 'error', error: msg, errorCode: code }));
    }
  }, []);

  const download = useCallback(async (formatId, title, slideIndex) => {
    const { url } = state;
    if (!url) return;

    cancelledRef.current = false;
    setState((s) => ({
      ...s,
      status: 'downloading',
      downloadingFormatId: formatId,
      downloadProgress: 0,
      error: null,
    }));

    try {
      const { job_id: jobId } = await startDownload(url, formatId, slideIndex);

      let attempts = 0;
      let job = null;
      while (attempts < MAX_POLL_ATTEMPTS && !cancelledRef.current) {
        job = await getDownloadStatus(jobId);
        if (job.status === 'done' || job.status === 'error') break;
        setState((s) => ({ ...s, downloadProgress: Math.round(job.progress || 0) }));
        await sleep(POLL_INTERVAL_MS);
        attempts += 1;
      }

      if (!job || job.status !== 'done') {
        throw new Error(job?.error || 'Download timed out. Please try again.');
      }

      const response = await fetchDownloadResult(jobId);
      const disposition = response.headers['content-disposition'] || '';
      let filename = title || 'download';
      const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/i);
      if (match) {
        filename = match[1].replace(/['"]/g, '');
      }

      triggerBrowserDownload(response.data, filename);

      setState((s) => ({
        ...s,
        status: 'ready',
        downloadingFormatId: null,
        downloadProgress: 0,
      }));
    } catch (err) {
      const msg = err?.response?.data?.error || err.message || 'Download failed';
      const code = err?.response?.data?.code || null;
      setState((s) => ({
        ...s,
        status: 'error',
        error: msg,
        errorCode: code,
        downloadingFormatId: null,
        downloadProgress: 0,
      }));
    }
  }, [state]);

  const reset = useCallback(() => {
    cancelledRef.current = true;
    setState({
      status: 'idle',
      metadata: null,
      error: null,
      errorCode: null,
      downloadingFormatId: null,
      downloadProgress: 0,
      url: '',
    });
  }, []);

  return { state, analyze, download, reset };
}
