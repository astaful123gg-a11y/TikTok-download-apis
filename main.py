import os
import uuid
import yt_dlp
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="TikTok Download API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PASSWORD = "SHUVO-apis"
COOKIES_FILE = os.environ.get("COOKIES_FILE", "cookies.txt")  # Netscape format cookies.txt
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def check_auth(x_api_key: str = Header(default=None)):
    """Require header:  X-API-Key: SHUVO-apis"""
    if x_api_key != API_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


class DownloadRequest(BaseModel):
    url: str
    no_watermark: bool = True


def ydl_opts(outtmpl=None):
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": outtmpl is None,
        "format": "best",
    }
    if os.path.exists(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE
    if outtmpl:
        opts["outtmpl"] = outtmpl
    return opts


@app.get("/")
def health():
    return {"status": "ok", "cookies_loaded": os.path.exists(COOKIES_FILE)}


@app.post("/api/info", dependencies=[Depends(check_auth)])
def get_info(req: DownloadRequest):
    """Video info + direct play/download links, no file saved on server."""
    try:
        with yt_dlp.YoutubeDL(ydl_opts()) as ydl:
            info = ydl.extract_info(req.url, download=False)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Extract failed: {e}")

    formats = info.get("formats", [])
    video_url = None
    for f in formats:
        if f.get("vcodec") != "none" and f.get("acodec") != "none":
            video_url = f.get("url")
    if not video_url:
        video_url = info.get("url")

    return {
        "title": info.get("title"),
        "author": info.get("uploader") or info.get("creator"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "play_count": info.get("view_count"),
        "like_count": info.get("like_count"),
        "download_url": video_url,
        "no_watermark": req.no_watermark,
    }


@app.post("/api/download", dependencies=[Depends(check_auth)])
def download_file(req: DownloadRequest):
    """Downloads the file server-side and returns it as a file response."""
    file_id = str(uuid.uuid4())
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    try:
        with yt_dlp.YoutubeDL(ydl_opts(outtmpl)) as ydl:
            info = ydl.extract_info(req.url, download=True)
            filepath = ydl.prepare_filename(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Download failed: {e}")

    if not os.path.exists(filepath):
        raise HTTPException(status_code=500, detail="File not found after download")

    filename = f"{info.get('title', 'tiktok_video')}.mp4"
    return FileResponse(filepath, media_type="video/mp4", filename=filename)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
