# 🎥 ClipGrabber (SocialDL)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![React](https://img.shields.io/badge/react-18.2-blue)
![Flask](https://img.shields.io/badge/flask-3.0-blue)
A powerful, full-stack web application that allows users to seamlessly download media (videos, images, audio) and extract captions from various social media platforms including YouTube, Instagram, Facebook, Pinterest, and TikTok.
## ✨ Features
- **Multi-Platform Support**: Download content from YouTube, Instagram, Facebook, Pinterest, and more.
- **Media Extraction**: Download videos in highest quality, extract audio, and fetch thumbnails.
- **Caption Generation/Extraction**: Automatically grab or generate captions/metadata for social media posts.
- **Modern UI/UX**: Premium, responsive interface built with React, featuring a sleek dark/light mode toggle.
- **Robust Backend**: Powered by a robust Python/Flask backend utilizing `yt-dlp` and `instaloader` for reliable media fetching.
- **Rate Limiting**: Built-in API rate limiting to prevent abuse.
## 🛠️ Tech Stack
### Frontend
- **React 18**
- **TailwindCSS** (Styling & Dark Mode)
- **Axios** (API Requests)
### Backend
- **Python & Flask**
- **yt-dlp** (Media extraction core)
- **Instaloader** (Instagram-specific scraping)
- **BeautifulSoup4** (HTML parsing)
- **Flask-Limiter** (Rate limiting)
## 🚀 Getting Started
### Prerequisites
- [Node.js](https://nodejs.org/) (v16 or higher)
- [Python](https://www.python.org/) (v3.8 or higher)
- [FFmpeg](https://ffmpeg.org/) (Required by `yt-dlp` for media merging and processing)
### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the Flask server:
   ```bash
   python app.py
   ```
   The backend will run on `http://localhost:5000`.
### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```
   The frontend will run on `http://localhost:3000`.
## 📁 Project Structure
```text
social-dl/
├── backend/               # Flask API and scraping services
│   ├── app.py             # Main Flask application
│   ├── routes/            # API endpoints (analyze, download, caption, proxy)
│   ├── services/          # Core download logic (yt-dlp, instaloader)
│   ├── utils/             # Helper functions (url parsing, etc.)
│   └── requirements.txt   # Python dependencies
├── frontend/              # React application
│   ├── public/            # Static assets
│   ├── src/               # React components, contexts, and pages
│   ├── package.json       # Node dependencies
│   └── tailwind.config.js # Tailwind CSS configuration
└── README.md              # Project documentation
```
## 🧪 Testing
```bash
cd backend
pip install -r requirements.txt
pytest -q
```
CI runs the backend test suite and the frontend production build on every push/PR (`.github/workflows/ci.yml`).

## ⬆️ Keeping yt-dlp current
`yt-dlp` breaks against live platforms as YouTube/Instagram/etc. change their sites, so `backend/requirements.txt`
pins an exact version rather than an open range. `.github/dependabot.yml` checks for a new `yt-dlp` release
weekly and opens a PR automatically — review and merge those promptly, since a stale `yt-dlp` is the most common
cause of "downloads suddenly stopped working."

## ☁️ Deployment
The backend deploys to Render.com's free tier via `backend/render.yaml` (single web service, threaded gunicorn
worker, `/health` endpoint for uptime checks). Set `CORS_ORIGIN` to your deployed frontend's origin and, if you
want cookie-gated extraction, one or more of `YT_COOKIES` / `IG_COOKIES` / `TIKTOK_COOKIES` / `FB_COOKIES`.

The frontend is a static build (`npm run build`) deployable to any static host. Set `REACT_APP_API_URL` to the
backend's URL at build time if frontend and backend are on different domains, and `REACT_APP_SITE_URL` to the
real domain for correct SEO metadata. See `frontend/.env.example` for the full list, including AdSense/Adsterra
env vars — both ad networks are disabled by default until their respective keys are set.

## 📝 Disclaimer
This tool is intended for educational purposes and personal use only. Please respect the copyright and terms of service of the respective platforms when downloading content.
