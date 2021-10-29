"""
Simple module to allow sending quick messages via Telegram (with logging)

Getting Started:
	1. Import this module
	2. Add the following to your environment variables:
			TELEGRAM_BOT_TOKEN=
			TELEGRAM_CHAT_ID=
	3. Call telegram.botSendMessage("Hello world!")
"""

import os
from dotenv import load_dotenv
import requests
import logging

load_dotenv()
logger = logging.getLogger('global-log')

def botSendMessage(botMessage):
	try:
		botToken  = os.getenv('TELEGRAM_BOT_TOKEN')
		botChatID = os.getenv('TELEGRAM_CHAT_ID')
		if botToken == None or botChatID == None: return # end function, telegram alerts are optional

		url       = 'https://api.telegram.org/bot' + botToken + '/sendMessage'
		data = {
			"chat_id": botChatID,
			"text" : botMessage
		}

		logger.info("Sending Telegram message...")
		response = requests.post(url, data)
		# print(response.json())
		if response.status_code >= 300: raise Exception(response.json())
		logger.info(response.json())
	except Exception as e:
		logger.error(e)

# botSendMessage("From Py!")