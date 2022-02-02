"""
Patreon YouTube Watchlist

1. Parse Patreon RSS for Post ID, Title, and YT Video ID
2. Store Post ID in local JSON to avoid re-adding old videos
3. Add to YT playlist

Environment Variables:
	PATREON_RSS_URL
	PATREON_RSS_PARSE_AMOUNT (optional, defaults to 10)
	YT_PLAYLIST_ID
	TELEGRAM_BOT_TOKEN (optional, used for error alerts)
	TELEGRAM_CHAT_ID (optional)

"""

import os
from dotenv import load_dotenv
import sys
import datetime
import logging
import logging.handlers as handlers
import traceback
import re
import json
import feedparser
from pprint import pprint
from youtube import youtube
import telegram

def init_logger(console_debug_lvl = '1'):
	"""
	Initiates logger

	- Creates log file
	- Rotates log after 10 MB, with 5 backups
	- Creates two log handlers
		- One for the log file
		- Another for the console
	- Sets debug level

	Args:
		console_debug_lvl (str): 0 off, 1 on prints only in log file, 2 on prints to log file & console
	"""
	try:
		# Log File Variables
		log_file_name = 'app'
		log_file_ext = '.log'
		global log_file_fullname
		global log_file_actual
		log_file_fullname = (log_file_name + log_file_ext)
		log_file_actual = os.path.join(os.getcwd(), log_file_fullname)

		# Global log FILE settings
		log_file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s -> %(message)s')
		log_file_handler   = handlers.RotatingFileHandler(log_file_actual, maxBytes=10000000, backupCount=5)
		log_file_handler.setFormatter(log_file_formatter)

		# Global log CONSOLE settings
		log_console_formatter = logging.Formatter('%(asctime)s - %(message)s')
		log_console_handler   = logging.StreamHandler()
		log_console_handler.setFormatter(log_console_formatter)

		if console_debug_lvl == '2':
			# Debug writes to log file AND displays in console
			log_console_handler.setLevel(logging.DEBUG)
			logger.setLevel(logging.DEBUG)
		elif console_debug_lvl == '1':
			# Debug only writes to log file, does not display in console
			log_console_handler.setLevel(logging.INFO)
			logger.setLevel(logging.DEBUG)
		else:
			# Debug is completely off, doesn't write to log file
			log_console_handler.setLevel(logging.INFO)
			logger.setLevel(logging.INFO)

		# Adds configurations to global log
		logger.addHandler(log_file_handler)
		logger.addHandler(log_console_handler)

	except IOError as e:
		errOut = "** ERROR: Unable to create or open log file %s" % log_file_name
		if e.errno == 2:    errOut += "- No such directory **"
		elif e.errno == 13: errOut += " - Permission Denied **"
		elif e.errno == 24: errOut += " - Too many open files **"
		else:
			errOut += " - Unhandled Exception-> %s **" % str(e)
			sys.stderr.write(errOut + "\n")
			traceback.print_exc()

	except Exception:
		traceback.print_exc()

def main():
	new_patreon_vids   = []
	new_watchlist_vids = []
	video_history_file = "youtube_video_history.json"

	# Load video history from local storage
	logger.info(f"Reading {video_history_file}...")
	if os.path.exists(video_history_file):
		with open(video_history_file) as infile:
			videoHistory = json.load(infile)
			# pprint(videoHistory)
	else:
		with open(video_history_file, 'wb') as outfile:
			videoHistory = []

	logger.info("Loading Patreon RSS feed...")
	feed = feedparser.parse(rss_url)
	logger.info(f"Number of RSS posts : {len(feed.entries)}")

	# RSS Entry Regex Loop
	for index, entry in enumerate(feed.entries):
		ytids_init  = re.findall(ytid_pattern, entry.summary, re.MULTILINE | re.IGNORECASE)
		ytids_final = list(set(ytids_init)) # removes duplicates

		# regex accidentally matches youtube.com/kindafunny and kindafunnygames
		for ytid in reversed(ytids_final):
			if "indafun" in ytid.lower(): ytids_final.remove(ytid)

		# OLD METHOD, DELETE LATER
		# logger.info(f"Entry #{index+1} - {entry.published}")
		# logger.info(f"	{entry.title}")
		# logger.info(f"	Video IDs found: {ytids_final}")

		# # Compare and add new videos to playlist
		# for vID in ytids_final:
		# 	if vID not in videoHistory:
		# 		logger.info(f"	Adding new video to playlist '{vID}'...")
		# 		youtube.add_to_playlist(yt_playlist_id, vID)
		# 		new_watchlist_vids.append(vID)
		# 	else:
		# 		logger.info(f"	Skipping old video '{vID}'...")

		# new_patreon_vids.extend(ytids_final)
		new_patreon_vids.append({
			"published": entry.published,
			"title"    : entry.title,
			"ytIDs"    : ytids_final
		})

		if index == (rss_parse_amount-1): break # Stop at X to avoid looping through entire RSS feed
	new_patreon_vids.reverse()

	# Compare and add new videos to playlist
	for index, pEntry in enumerate(new_patreon_vids):
		logger.info(f"Entry #{index+1} - {pEntry['published']}")
		logger.info(f"  {pEntry['title']}")
		logger.info(f"    Video IDs found: {pEntry['ytIDs']}")

		for vID in pEntry['ytIDs']:
			if vID not in videoHistory:
				logger.info(f"      Adding new video to playlist '{vID}'...")
				youtube.add_to_playlist(yt_playlist_id, vID)
				new_watchlist_vids.append(vID)
			else:
				logger.info(f"      Skipping old video '{vID}'...")
	
	# Save history
	videoHistory.extend(new_watchlist_vids)
	logger.info("Saving video history...")
	with open(video_history_file, 'w') as outfile:
		json.dump(videoHistory, outfile)

	logger.info(f"Added {len(new_watchlist_vids)} new videos to the playlist")
	logger.debug("FINISHED")

def test():
	print(f"youtube.get_playlist_videos({yt_playlist_id})={youtube.get_playlist_videos(yt_playlist_id)}")

if __name__ == "__main__":
	# Load Settings
	try:
		load_dotenv()
		rss_url          = os.environ['PATREON_RSS_URL']
		yt_playlist_id   = os.environ['YT_PLAYLIST_ID']
		rss_parse_amount = int(os.getenv('PATREON_RSS_PARSE_AMOUNT', 10)) # Defaults to 10
		ytid_pattern     = r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})'
	except KeyError as e:
		print(f"Error: Missing {e} from environment variables!")
		sys.exit(1)

	# Initiate logger
	logger = logging.getLogger('global-log')
	init_logger(console_debug_lvl="1")
	logger.debug("STARTING APP")
	logger.debug("========================================")

	try:
		usage_help = "\nUsage: python app.py [OPTION]\n\nOptional Arguments:\n  -t, -testyoutube     test youtube auth and api by requesting playlist items\n  -h, -help        display this help and exit"
		
		if   sys.argv[1] == "-t" or sys.argv[1] == "-testyoutube":
			youtube = youtube()
			test()
		elif sys.argv[1] == "-h" or sys.argv[1] == "-help":
			print(usage_help)
			sys.exit(0)
		else:
			print(f"\n{sys.argv[1]} is not a valid option")
			print(usage_help)
			sys.exit(1)
	except IndexError as e:
		youtube = youtube()
		main()