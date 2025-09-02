import time
import os
from pprint import pprint

import requests

from dotenv import load_dotenv

from loguru import logger
import sys
import json

# logger.add(sys.stderr)

if '.env' in os.listdir():
    load_dotenv()
    logger.info('env load')


url = 'https://api.line.me/v2/bot/message/broadcast'

headers = {
    'Content-Type':'application/json',
    'Authorization':f"Bearer {os.getenv('LINE_CHANNEL_ACCESS_TOKEN')}"
}
data = {
    'messages':[
        {
            'type':'text',
            'text':'test message'
        }
    ]
}
res = requests.post(url, headers = headers, data = json.dumps(data))
res.raise_for_status()

logger.info('message sent')