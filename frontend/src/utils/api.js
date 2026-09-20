import axios from 'axios';

// Same-origin '/api' by default (works behind any reverse proxy that routes
// /api to the backend). Override only for local dev against a backend
// running on a different host/port, or a split-domain deployment.
const API_BASE = process.env.REACT_APP_API_URL || '';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeUrl = async (url) => {
  const response = await apiClient.post('/api/analyze', { url });
  return response.data;
};

export const fetchCaption = async (url) => {
  const response = await apiClient.post('/api/caption', { url });
  return response.data;
};

export const exportCaption = async (url) => {
  return apiClient.post('/api/caption/export', { url }, { responseType: 'blob' });
};

/**
 * Starts a download job and returns its job_id. The backend runs yt-dlp in
 * the background instead of blocking the HTTP request, so large downloads
 * don't tie up a web worker or time out the connection.
 */
export const startDownload = async (url, formatId, slideIndex) => {
  const response = await apiClient.post('/api/download', {
    url,
    format_id: formatId,
    slide_index: slideIndex,
  });
  return response.data; // { job_id, status }
};

export const getDownloadStatus = async (jobId) => {
  const response = await apiClient.get(`/api/download/status/${jobId}`);
  return response.data; // { status, progress, message, error?, code? }
};

export const fetchDownloadResult = async (jobId) => {
  return apiClient.get(`/api/download/result/${jobId}`, { responseType: 'blob' });
};

export default apiClient;
