# -*- coding: utf-8 -*-
"""LINE Bot Blueprint - Webhook and event handlers"""

from flask import Blueprint, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    FollowEvent
)
import logging

from config import Config
from services.firebase_service import firebase_service
from handlers.message_handler import MessageHandler
from utils.line_helper import show_loading_animation

logger = logging.getLogger(__name__)

# Create blueprint
linebot_bp = Blueprint('linebot', __name__)

# LINE Bot 設定
configuration = Configuration(access_token=Config.CHANNEL_ACCESS_TOKEN)
line_handler = WebhookHandler(Config.CHANNEL_SECRET)

# 初始化訊息處理器
message_handler = MessageHandler(firebase_service)


@linebot_bp.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """處理文字訊息事件"""
    try:
        # 取得訊息內容
        text = event.message.text

        # 取得使用者資訊
        user_id = event.source.user_id

        # 顯示 loading animation（僅限一對一聊天）
        show_loading_animation(configuration, event, loading_seconds=10)

        # 取得使用者名稱
        user_name = "使用者"
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            try:
                # 一對一取得使用者名稱
                profile = line_bot_api.get_profile(user_id)
                user_name = profile.display_name
            except Exception as e:
                # 如果無法取得名稱，使用預設值
                logger.warning(f"無法取得使用者名稱: {e}")
                user_name = "使用者"

        # 處理訊息
        result = message_handler.handle_text_message(
            text=text,
            user_id=user_id,
            user_name=user_name
        )

        # 準備回覆訊息
        if isinstance(result, str):
            # 一般文字回應
            reply_message = TextMessage(text=result)            

            # 回覆訊息
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[reply_message]
                    )
                )

            logger.info(f"處理訊息成功: {text[:20]}...")

    except Exception as e:
        logger.error(f"處理訊息時發生錯誤: {e}")
        # 嘗試回覆錯誤訊息
        try:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="處理訊息時發生錯誤，請稍後再試")]
                    )
                )
        except Exception as e:
            logger.error(f"回覆錯誤訊息失敗: {e}")


@line_handler.add(FollowEvent)
def handle_follow(event):
    """處理使用者加入好友事件"""
    try:
        user_id = event.source.user_id

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)

            # 取得使用者資料
            try:
                profile = line_bot_api.get_profile(user_id)
                user_name = profile.display_name
            except Exception as e:
                logger.error(f"取得使用者資料失敗: {e}")
                user_name = "使用者"

            # 建立使用者和聊天記錄
            firebase_service.create_or_update_user(user_id, user_name)

            welcome_message = """👋 你好！我是記帳與待辦機器人

我可以幫助你：
💰 記錄個人支出
📝 管理待辦事項

請使用 LINE 選單開啟功能頁面"""

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=welcome_message)]
                )
            )

        logger.info(f"使用者加入好友: {user_name} ({user_id})")

    except Exception as e:
        logger.error(f"處理加入好友事件時發生錯誤: {e}")
