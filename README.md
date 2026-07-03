# TikTok Download API

## Setup
1. `pip install -r requirements.txt`
2. Export TikTok cookies from browser (extension: "Get cookies.txt LOCALLY") as Netscape format → save as `cookies.txt` in this folder.
3. Run: `uvicorn main:app --reload`

## Endpoints
- `GET /` — health check, shows if cookies loaded (no auth)
- `POST /api/info` — `{"url": "tiktok_link"}` → title, author, direct video url, needs X-API-Key header
- `POST /api/download` — `{"url": "tiktok_link"}` → downloads server-side, returns mp4 file, needs X-API-Key header

## Auth
Every /api/* call needs header: X-API-Key: SHUVO-apis
The / health check is open (no key) - that's what UptimeRobot should ping.

## Deploy on Render
1. Push this folder to a PRIVATE GitHub repo (cookies.txt has session tokens, never make it public).
2. Render -> New -> Web Service -> connect repo.
3. Build command: pip install -r requirements.txt
4. Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
5. Deploy. No env vars needed - cookies.txt ships with repo, password is hardcoded in main.py.

## UptimeRobot
- Monitor type: HTTP(s)
- URL: https://your-app.onrender.com/
- Interval: 5 min (keeps Render free tier awake)

## Note
Cookies expire if you log out of TikTok on the browser you exported from. If /api/info starts failing, re-export cookies.txt and redeploy.
