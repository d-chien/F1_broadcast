import os
from fastapi import FastAPI, Request, HTTPException, Response
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
import uvicorn

from dotenv import load_dotenv
from loguru import logger
import sys

logger.add(sys.stderr)

if '.env' in os.listdir():
    load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')



configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = FastAPI()
logger.info('webhook all set')

# 處理 LINE Webhook 的主要路由
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# 處理所有訊息事件，特別是文字訊息
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     # 取得用戶傳送的文字訊息內容
#     user_message = event.message.text.strip().lower()
#     logger.info(f'{user_message=}')
    
#     # 根據用戶訊息內容，設定不同的回覆
#     if "嗨" in user_message or "你好" in user_message:
#         reply_text = "嗨！您好！很高興與您對話！"
#     elif "天氣" in user_message:
#         reply_text = "目前我還無法查詢天氣，但很高興你問我！"
#     elif "貓" in user_message:
#         reply_text = "我喜歡貓咪！你有養嗎？"
#     else:
#         # 如果沒有符合的關鍵字，就回覆預設內容
#         reply_text = f"你傳送了「{user_message}」嗎？這是一段預設的回應。"
    
#     # 回覆訊息給用戶
#     logger.info(f'{reply_text=}')
#     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
#     logger.success('msg sent')

def main():
    print("Hello from f1-broadcast!")
    uvicorn.run('main:app', port=8080, log_level = 'info')

if __name__ == "__main__":
    main()
