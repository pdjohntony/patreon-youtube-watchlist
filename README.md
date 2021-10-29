# patreon-youtube-watchlist
Parses a Patreon RSS feed for YouTube video links and adds them to a YouTube Playlist.

## Getting Started
1. Clone the repository
```
git clone https://github.com/pdjohntony/patreon-youtube-watchlist
```
2. Install the python requirements
```python
pip install -r requirements.txt
```
3. Configure your environment variables:
```ini
	PATREON_RSS_URL
	PATREON_RSS_PARSE_AMOUNT (optional, defaults to 10)
	YT_PLAYLIST_ID
	TELEGRAM_BOT_TOKEN (optional)
	TELEGRAM_CHAT_ID (optional)
```
4. Obtain a YouTube OAuth Token
You'll need to run this first from a GUI capable system the first time. A browser will open and you must login to your google account and authorize the app. Once thats done it will generate a `youtube_token.pickle` file. You can then copy and paste this file to another system.

## Usage
```bash
python app.py
```

## Automate with Cron
To run automatically every 30 minutes setup a cron job:

```bash
crontab -e
0,30 * * * * (cd <script-location> && /usr/bin/python3 app.py)
```