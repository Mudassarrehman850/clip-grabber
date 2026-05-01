import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 60000, // 60s for downloads
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeUrl = async (url) => {
  const response = await apiClient.post('/api/analyze', { url });
  return response.data;
};

export const downloadMedia = async (url, formatId, title, onProgress) => {
  const response = await apiClient.post(
    '/api/download',
    { url, format_id: formatId, title },
    {
      responseType: 'blob',
      timeout: 300000, // 5 min for large files
      onDownloadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const pct = Math.round((progressEvent.loaded / progressEvent.total) * 100);
          onProgress(pct);
        }
      },
    }
  );
  return response;
};

export default apiClient;
