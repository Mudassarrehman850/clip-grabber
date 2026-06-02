---
title: ClipGrabber API
title: ClipGrabber / SocialDL
emoji: 🎥
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---
# ClipGrabber Backend API
Social Media Downloader Backend (YouTube, Instagram, TikTok, etc.)
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
## 📝 Disclaimer
This tool is intended for educational purposes and personal use only. Please respect the copyright and terms of service of the respective platforms when downloading content.
