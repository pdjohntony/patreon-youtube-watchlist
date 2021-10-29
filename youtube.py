"""
YouTube API
https://developers.google.com/youtube/v3/quickstart/python
https://console.cloud.google.com

Test Video IDs
M7FIvfx5J10
9bZkp7q19f0
"""

from pprint import pprint
import pickle
import os
import sys
import logging
from sys import excepthook
import telegram

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request

logger = logging.getLogger('global-log')

scopes = [
				"https://www.googleapis.com/auth/youtube",
				"https://www.googleapis.com/auth/youtube.force-ssl",
				"https://www.googleapis.com/auth/youtubepartner"
			]

class youtube:
	def __init__(self):
		try:
			# Disable OAuthlib's HTTPS verification when running locally.
			# *DO NOT* leave this option enabled in production.
			os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

			api_service_name    = "youtube"
			api_version         = "v3"
			client_secrets_file = "youtube_web_client_secret.json"
			token_pickle_file   = "youtube_token.pickle"
			credentials         = None

			# youtube_token.pickle stores the user's credentials from previously successful logins
			if os.path.exists(token_pickle_file):
				logger.info("Loading Credentials From Pickle File...")
				with open(token_pickle_file, "rb") as token:
					credentials = pickle.load(token)
			
			# If there are no valid credentials available, then either refresh the token or log in.
			if not credentials or not credentials.valid:
				if credentials and credentials.expired and credentials.refresh_token:
					logger.info('Refreshing YouTube Access Token...')
					credentials.refresh(Request())
				else:
					logger.info('Fetching New YouTube Token...')
					logger.info("You cannot do this via CLI, you must run this from a GUI capable system.")
					flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
					flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
					credentials = flow.credentials
					# Save the credentials for the next run
					with open(token_pickle_file, 'wb') as f:
						logger.info('Saving YouTube Token for Future Use...')
						pickle.dump(credentials, f)

			self.youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
		except Exception as e:
			logger.error(e)
			telegram.botSendMessage(f"Patreon YouTube Watchlist - ERROR: {e}")
			sys.exit(1)

	def get_playlist_videos(self, plID=None):
		# Not used in main script, in favor of local video ID storage
		#! NEEDS PAGINATION, maxResults default is 5, maxes out at 50
		#! https://developers.google.com/youtube/v3/docs/playlistItems/list
		vIDs = []
		request = self.youtube.playlistItems().list(
			part="contentDetails",
			maxResults=50,
			playlistId=plID
		)
		response = request.execute()
		# pprint(response)

		for i in response["items"]:
			# print(i["contentDetails"]["videoId"])
			vIDs.append(i["contentDetails"]["videoId"])
		
		# print(vIDs)
		return vIDs
	
	def add_to_playlist(self, plID=None, vID=None):
		try:
			request = self.youtube.playlistItems().insert(
				part="snippet",
				body={
					"snippet": {
						"playlistId": plID,
						"resourceId": {
							"kind": "youtube#video",
							"videoId": vID
						}
					}
				}
			)
			response = request.execute()
			logger.debug(response)
		except googleapiclient.errors.HttpError as httperror:
			logger.error(httperror)

if __name__ == "__main__":
	youtube = youtube()
	# youtube.get_playlist_videos("xxx")
	# youtube.add_to_playlist(plID="xxx", vID="M7FIvfx5J10")