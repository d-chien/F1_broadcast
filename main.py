import os
import time
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

from threading import Thread
import schedule
import requests
import json

from f1_data import get_next_game, last_session_result

# logger.add(sys.stderr)   # 似乎已經會預設加上了，所以先移除

if '.env' in os.listdir():
    load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

send_count = 0
MAX_SENDS = 1


configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = FastAPI()
logger.info('webhook all set')

# 處理 LINE Webhook 的主要路由
@app.post("/callback")
async def callback(request: Request):
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    if signature is None:
        raise HTTPException(status_code=400, detail="X-Line-Signature header is missing.")

    # get request body as text
    body = await request.body()
    # app.logger.info("Request body: " + body)
    logger.info(f'Request body: {body.decode()}')

    # handle webhook body
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        # app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        # abort(400)
        logger.error("Invalid signature. Please check your channel access token/channel secret.")
        raise HTTPException(status_code=400, detail="Invalid signature")

    return 'OK'

# 處理所有訊息事件，特別是文字訊息
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    logger.info(f'reply token: {event.reply_token}')
    logger.info(f'msg received: {event.message.text}')

    # 前場賽事logic
    if '前場' in event.message.text:
        logger.info(f'獲取前場賽事資訊')
        try:
            return_msg = last_session_result()
            logger.success(f'獲取前場賽事資訊完成')
        except Exception as e:
            logger.error(f'獲取前場賽事資訊錯誤:{e}')
            return_msg = '資料獲取失敗，請稍後再行嘗試，非常抱歉！'
        
        try:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=return_msg)]
                    )
                )
            logger.success(f'{return_msg=}')
        except Exception as e:
            logger.error(f'return failed: {e}')
    # else:
    #     with ApiClient(configuration) as api_client:
    #         line_bot_api = MessagingApi(api_client)
    #         line_bot_api.reply_message_with_http_info(
    #             ReplyMessageRequest(
    #                 reply_token=event.reply_token,
    #                 messages=[TextMessage(text=event.message.text)]
    #             )
    #         )

    # 前場賽事logic
    if '去年' in event.message.text:
        logger.info(f'獲取去年賽事資訊')
        try:
            return_msg = get_last_year_result()
            logger.success(f'獲取去年賽事資訊完成')
        except Exception as e:
            logger.error(f'獲取去年賽事資訊錯誤:{e}')
            return_msg = '資料獲取失敗，請稍後再行嘗試，非常抱歉！'
        
        try:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=return_msg)]
                    )
                )
            logger.success(f'{return_msg=}')
        except Exception as e:
            logger.error(f'return failed: {e}')
    else:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=event.message.text)]
                )
            )


# Broadcast Message
def broadcast():
    global send_count, MAX_SENDS
    
    # 檢查是否已達到發送上限
    # if send_count >= MAX_SENDS:
    #     logger.warning(f"已達到發送上限 {MAX_SENDS} 次，停止排程。")
    #     schedule.clear() # 清除所有排程任務
    #     return

    msg = get_next_game()
    try:
        url = 'https://api.line.me/v2/bot/message/broadcast'

        headers = {
            'Content-Type':'application/json',
            'Authorization':f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        }
        data = {
            'messages':[
                {
                    'type':'text',
                    'text':msg
                }
            ]
        }
        res = requests.post(url, headers = headers, data = json.dumps(data))
        res.raise_for_status()
        logger.success(f'Broadcast: {msg}')

    except Exception as e:
        logger.error(f'Broadcast Error: {e}')

    # send_count+=1

def schedule_thread():
    # when on first time
    # broadcast()
    # schedule every monday
    schedule.every().monday.at('01:00').do(broadcast)   # system use UTC time, so in my laziness, I choose an easy way to let it broadcast at 9.
    logger.info('scheduled project done')

    while True:
        schedule.run_pending()
        time.sleep(1)

@app.on_event("startup")
async def startup_event():
    thread = Thread(target=schedule_thread)
    thread.daemon = True # 確保主程式結束時執行緒也會結束
    thread.start()
    logger.info("排程執行緒已啟動！")



def main():
    print("Hello from f1-broadcast!")
    uvicorn.run('main:app', port=8080, log_level = 'info')

# if __name__ == "__main__":
    # main()
