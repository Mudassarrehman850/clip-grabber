# ClipGrabber — Social Media Downloader

A production-ready web app to download videos, audio, and images from **YouTube**, **Instagram**, and **TikTok** — with full caption extraction, hashtag parsing, and carousel support.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Tailwind CSS, Axios |
| Backend | Flask (Python), Flask-CORS, Flask-Limiter |
| Downloader | yt-dlp |
| Media processing | FFmpeg |

---

## Project Structure

```
clip-grabber/
├── backend/
│   ├── app.py                        ← Flask app factory
│   ├── requirements.txt
│   ├── routes/
│   │   ├── analyze.py                ← POST /api/analyze
│   │   ├── download.py               ← POST /api/download
│   │   └── caption.py                ← POST /api/caption, /api/caption/export
│   ├── services/
│   │   └── ytdlp_service.py          ← yt-dlp core + caption extraction
│   └── utils/
│       └── url_detector.py           ← Platform detection & URL validation
└── frontend/
    └── src/
        ├── pages/HomePage.jsx
        ├── components/
        │   ├── Header.jsx
        │   ├── URLInput.jsx           ← Live platform badge while typing
        │   ├── PreviewCard.jsx        ← Thumbnail + stats + carousel strip
        │   ├── DownloadButtons.jsx    ← Format buttons + carousel ZIP/slides
        │   ├── CaptionPanel.jsx       ← Full caption, hashtags, chapters, export
        │   ├── AnalyzeLoader.jsx      ← Skeleton loading state
        │   ├── ErrorMessage.jsx       ← User-friendly errors
        │   ├── HistoryPanel.jsx       ← localStorage history (last 10)
        │   └── Footer.jsx
        ├── hooks/useDownloader.js     ← State machine hook
        └── utils/
            ├── api.js                 ← Axios client
            └── helpers.js             ← Formatters, platform detection
```

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **FFmpeg** — required for audio extraction and video merging

### Install FFmpeg

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows — download from https://ffmpeg.org, add to PATH

# Verify
ffmpeg -version
```

---

## Setup & Run

### Backend

```bash
cd social-dl/backend
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

### Frontend

```bash
cd social-dl/frontend
npm install
npm start
# → http://localhost:3000
```

The React dev server proxies `/api/*` to `http://localhost:5000` automatically.

---

## API Reference

### `POST /api/analyze`
Extract metadata without downloading.

**Request:** `{ "url": "https://..." }`

**Response:**
```json
{
  "success": true,
  "platform": "youtube",
  "content_type": "video",
  "data": {
    "title": "Video Title",
    "thumbnail": "https://...",
    "duration": "3:33",
    "uploader": "Channel Name",
    "view_count": 1500000,
    "like_count": 50000,
    "comment_count": 1200,
    "upload_date": "20240101",
    "tags": ["tag1", "tag2"],
    "caption": {
      "full_text": "Full description text...",
      "hashtags": ["coding", "tutorial"],
      "mentions": ["someuser"],
      "urls": ["https://linktr.ee/..."],
      "word_count": 42,
      "char_count": 310,
      "chapters": [
        { "title": "Intro", "start_time": 0, "start_time_str": "0:00" },
        { "title": "Main Content", "start_time": 120, "start_time_str": "2:00" }
      ]
    },
    "formats": [
      { "id": "video_best", "label": "Video (Best Quality)", "ext": "mp4", "type": "video" },
      { "id": "video_720",  "label": "Video (720p)",         "ext": "mp4", "type": "video" },
      { "id": "audio_mp3",  "label": "Audio Only (MP3)",     "ext": "mp3", "type": "audio" },
      { "id": "thumbnail",  "label": "Thumbnail (JPG)",      "ext": "jpg", "type": "image" }
    ]
  }
}
```

### `POST /api/download`
Download and stream a file.

**Request:** `{ "url": "...", "format_id": "audio_mp3", "title": "My Video" }`

**Response:** Binary file stream with `Content-Disposition: attachment`.

### `POST /api/caption`
Get structured caption data only (no download).

**Request:** `{ "url": "https://..." }`

**Response:** `{ "success": true, "platform": "instagram", "caption": { ... } }`

### `POST /api/caption/export`
Download caption as a formatted `.txt` file.

**Request:** `{ "url": "https://..." }`

**Response:** Plain text file download.

---

## Format IDs

| `format_id` | Description | Platform |
|---|---|---|
| `video_best` | Best quality MP4 | All |
| `video_720` | 720p MP4 | YouTube |
| `audio_mp3` | MP3 audio | YouTube |
| `thumbnail` | JPG thumbnail | YouTube |
| `video_nowm` | MP4 no watermark | TikTok |
| `ig_image` | JPG image | Instagram (image posts) |
| `profile_pic` | Profile picture JPG | Instagram |
| `carousel_zip` | ZIP of all slides | Instagram carousel |
| `slide_0`, `slide_1`… | Individual carousel slide | Instagram carousel |

---

## Features

### ✅ Core
- YouTube: Video (best/720p), Audio (MP3), Thumbnail (JPG), Shorts
- TikTok: Video with watermark, Video without watermark
- Instagram: Reels, Video posts, Image posts, Carousel (multi-image/video), IGTV

### ✅ Caption Extraction (all platforms)
- Full description/caption text with show more/less
- `#hashtag` parsing — click any pill to copy
- `@mention` parsing — click any pill to copy
- Embedded URL detection
- YouTube chapter timestamps
- One-click copy full text
- Export as `.txt` file (formatted with title, author, date, hashtags, chapters)

### ✅ Instagram Carousel
- Detects multi-image/video posts automatically
- Shows slide strip preview in the card
- Download all slides as ZIP
- Download individual slides

### ✅ UX
- Live platform detection badge as you type
- Auto-submit on paste if URL is recognized
- Skeleton loading state while analyzing
- Download progress bar
- localStorage history (last 10 downloads)
- Clean error messages (private content, geo-block, rate limit)

---

## Test URLs

```
# YouTube
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ
https://www.youtube.com/shorts/dQw4w9WgXcQ

# TikTok
https://www.tiktok.com/@username/video/7123456789012345678
https://vm.tiktok.com/ZMxxxxxx/

# Instagram
https://www.instagram.com/reel/CxxxxxxYYYY/
https://www.instagram.com/p/CxxxxxxYYYY/      ← image or video post
```

---

## Rate Limits

- 20 requests / minute per IP
- 100 requests / hour per IP

---

## Error Codes

| Code | Meaning |
|---|---|
| `PRIVATE_CONTENT` | Content requires login or is private |
| `RATE_LIMITED` | Platform throttling — retry later |
| `EXTRACTION_FAILED` | yt-dlp couldn't parse the URL |
| `DOWNLOAD_FAILED` | Download started but failed |
| `UNKNOWN` | Unexpected server error |

---

## Production Deployment

```bash
# Backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

# Frontend
npm run build
# Serve /build with nginx or Vercel/Netlify
```

**Environment:**
```bash
# frontend/.env
REACT_APP_API_URL=https://your-api-domain.com
```

---

## Troubleshooting

**`ffmpeg not found`** → Install ffmpeg and make sure it's in PATH.

**yt-dlp errors** → Update it: `pip install -U yt-dlp`

**Instagram fails** → Instagram limits anonymous access. Add cookies:
```python
# ytdlp_service.py — add to _get_ydl_opts_instagram():
'cookiefile': '/path/to/instagram-cookies.txt'
```

Export cookies from your browser using the [cookies.txt extension](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc).

**TikTok region restricted** → Use a proxy:
```python
# ytdlp_service.py — add to _get_ydl_opts_base():
'proxy': 'http://your-proxy:port'
```
