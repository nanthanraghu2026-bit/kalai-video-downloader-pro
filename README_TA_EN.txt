KALAI VIDEO DOWNLOADER PRO — WEBSITE SOURCE

LOCAL TEST (Windows):
1. Install Python 3.12 64-bit.
2. Install FFmpeg and add ffmpeg.exe to PATH (required for MP3).
3. Open Command Prompt in this folder:
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
4. Visit http://127.0.0.1:5000

DEPLOYMENT:
- This is website source, not a hosted website.
- Deploy to a server that allows yt-dlp/FFmpeg and outbound network traffic.
- Use HTTPS and a production WSGI server; Procfile is a starting point.
- Before public launch add rate limiting, CAPTCHA/abuse prevention, job queue,
  storage quotas, monitoring, robust SSRF protection, and scheduled cleanup.
- Replace contact placeholder and complete legal disclosures.

GOOGLE ADSENSE:
- Ad boxes are placeholders only. No ads or revenue are active.
- Apply to AdSense using your own domain. Approval is not guaranteed.
- Add official ad code only after approval. Ensure useful original site content,
  clear navigation, privacy disclosures, and compliant consent management.
- Never click your own ads or encourage visitors to click ads.

LIMITATIONS:
- Public Facebook/Instagram links may fail when platforms change their systems.
- No login/private/DRM bypass or browser cookies are included.
- Only download content you own or are authorized to use.
- MP3 conversion requires FFmpeg.
- This starter needs security hardening before handling public traffic.
