import { useState, useCallback } from 'react';
import { analyzeUrl, downloadMedia } from '../utils/api';
import { addToHistory, triggerBrowserDownload } from '../utils/helpers';

export function useDownloader() {
  const [state, setState] = useState({
    status: 'idle', // idle | analyzing | ready | downloading | done | error
    metadata: null,
    error: null,
    downloadingFormatId: null,
    downloadProgress: 0,
    url: '',
  });

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
        // Save to history
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
      setState((s) => ({ ...s, status: 'error', error: msg }));
    }
  }, []);

  const download = useCallback(async (formatId, title) => {
    const { url } = state;
    if (!url) return;

    setState((s) => ({
      ...s,
      status: 'downloading',
      downloadingFormatId: formatId,
      downloadProgress: 0,
      error: null,
    }));

    try {
      const response = await downloadMedia(url, formatId, title, (pct) => {
        setState((s) => ({ ...s, downloadProgress: pct }));
      });

      // Get filename from Content-Disposition header
      const disposition = response.headers['content-disposition'] || '';
      let filename = 'download';
      const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/i);
      if (match) {
        filename = match[1].replace(/['"]/g, '');
      }

      triggerBrowserDownload(response.data, filename);

      setState((s) => ({
        ...s,
        status: 'ready', // go back to ready so user can download more formats
        downloadingFormatId: null,
        downloadProgress: 0,
      }));
    } catch (err) {
      const msg = err?.response?.data?.error || err.message || 'Download failed';
      setState((s) => ({
        ...s,
        status: 'error',
        error: msg,
        downloadingFormatId: null,
        downloadProgress: 0,
      }));
    }
  }, [state]);

  const reset = useCallback(() => {
    setState({
      status: 'idle',
      metadata: null,
      error: null,
      downloadingFormatId: null,
      downloadProgress: 0,
      url: '',
    });
  }, []);

  return { state, analyze, download, reset };
}
