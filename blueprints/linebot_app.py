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
    JoinEvent,
    MemberJoinedEvent,
    FollowEvent
)
import logging

from config import Config
from services.firebase_service import firebase_service
from handlers.message_handler import MessageHandler
from utils.line_helper import show_loading_animation
from utils.quick_reply import QuickReplyHelper

logger = logging.getLogger(__name__)

# Create blueprint
linebot_bp = Blueprint('linebot', __name__)

# LINE Bot 設定
configuration = Configuration(access_token=Config.CHANNEL_ACCESS_TOKEN)
line_handler = WebhookHandler(Config.CHANNEL_SECRET)

# 初始化訊息處理器
message_handler = MessageHandler(firebase_service, configuration)


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

        # 取得群組 ID（如果是群組訊息）
        group_id = None
        if hasattr(event.source, 'group_id'):
            group_id = event.source.group_id
        elif hasattr(event.source, 'room_id'):
            group_id = event.source.room_id

        # 取得使用者名稱
        user_name = "使用者"
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            try:
                if group_id:
                    # 群組中取得成員名稱
                    profile = line_bot_api.get_group_member_profile(group_id, user_id)
                    user_name = profile.display_name
                else:
                    # 一對一取得使用者名稱
                    profile = line_bot_api.get_profile(user_id)
                    user_name = profile.display_name
            except Exception as e:
                # 如果無法取得名稱，使用預設值
                logger.warning(f"無法取得使用者名稱: {e}")
                user_name = "使用者"

        # 處理訊息（支援群組和一對一）
        # 區分群組和一對一聊天
        is_group = group_id is not None

        result = message_handler.handle_text_message(
            text=text,
            user_id=user_id,
            user_name=user_name,
            group_id=group_id if is_group else user_id,  # 一對一時使用 user_id 作為識別
            is_group=is_group  # 傳遞是否為群組的標記
        )

        # 準備回覆訊息
        reply_message = None

        # 處理特殊回應類型
        if isinstance(result, dict):
            # 文字回應（帶 Quick Reply 指定）
            if result.get('type') == 'text':
                # 根據指定的選單類型設定 Quick Reply
                menu_type = result.get('quick_reply')
                if menu_type == 'expense_menu':
                    quick_reply = QuickReplyHelper.get_expense_menu(group_id)
                elif menu_type == 'todo_menu':
                    quick_reply = QuickReplyHelper.get_todo_menu(group_id)
                elif menu_type == 'settlement_menu':
                    quick_reply = QuickReplyHelper.get_settlement_menu()
                elif menu_type == 'main_menu':
                    quick_reply = QuickReplyHelper.get_main_menu()
                else:
                    quick_reply = QuickReplyHelper.get_main_menu()

                reply_message = TextMessage(
                    text=result.get('message', ''),
                    quick_reply=quick_reply
                )
            # Flex Message 回應
            elif result.get('type') == 'flex':
                # 根據指定的選單類型設定 Quick Reply
                menu_type = result.get('quick_reply')
                if menu_type == 'expense_menu':
                    quick_reply = QuickReplyHelper.get_expense_menu(group_id)
                elif menu_type == 'todo_menu':
                    quick_reply = QuickReplyHelper.get_todo_menu(group_id)
                elif menu_type == 'settlement_menu':
                    quick_reply = QuickReplyHelper.get_settlement_menu()
                elif menu_type == 'main_menu':
                    quick_reply = QuickReplyHelper.get_main_menu()
                else:
                    quick_reply = QuickReplyHelper.get_main_menu()

                # FlexMessage 也支援 quick_reply 屬性
                reply_message = result['message']
                reply_message.quick_reply = quick_reply
            # 其他字典回應
            else:
                reply_message = TextMessage(
                    text=result.get('text', '發生錯誤'),
                    quick_reply=QuickReplyHelper.get_main_menu()
                )
        elif isinstance(result, str):
            # 一般文字回應 - 根據訊息內容決定 Quick Reply
            if '說明' in text or '幫助' in text:
                quick_reply = QuickReplyHelper.get_main_menu()
            elif '記帳' in text:
                quick_reply = QuickReplyHelper.get_expense_menu(group_id)
            elif '待辦' in text:
                quick_reply = QuickReplyHelper.get_todo_menu(group_id)
            elif '結算' in text and '清帳' not in text:
                quick_reply = QuickReplyHelper.get_settlement_menu()
            elif "無法識別的指令" in result:
                quick_reply = QuickReplyHelper.get_main_menu()
            else:
                # 預設顯示主選單
                quick_reply = QuickReplyHelper.get_main_menu()

            reply_message = TextMessage(
                text=result,
                quick_reply=quick_reply
            )
        else:
            # FlexMessage 或其他類型
            reply_message = result
            if hasattr(reply_message, 'quick_reply'):
                reply_message.quick_reply = QuickReplyHelper.get_main_menu()

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
            firebase_service.create_or_update_chat(user_id, user_name)

            welcome_message = """👋 你好！我是記帳與待辦機器人

我可以幫助你：
💰 記錄個人支出
📝 管理待辦事項

輸入「說明」查看完整使用說明"""

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text=welcome_message,
                        quick_reply=QuickReplyHelper.get_main_menu()
                    )]
                )
            )

        logger.info(f"使用者加入好友: {user_name} ({user_id})")

    except Exception as e:
        logger.error(f"處理加入好友事件時發生錯誤: {e}")


@line_handler.add(JoinEvent)
def handle_join(event):
    """處理機器人加入群組事件"""
    try:
        group_id = None
        if hasattr(event.source, 'group_id'):
            group_id = event.source.group_id

        if group_id:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)

                # 取得群組摘要
                try:
                    group_summary = line_bot_api.get_group_summary(group_id)
                    group_name = group_summary.group_name
                except Exception as e:
                    logger.error(f"取得群組摘要失敗: {e}")
                    group_name = f"群組 {group_id[:8]}"

                # 建立群組（不預先載入成員，採用懶加載策略）
                # 成員會在首次發言時透過 _ensure_group_and_user 自動加入
                firebase_service.create_group(
                    line_group_id=group_id,
                    group_name=group_name
                )

                welcome_message = """👋 你好！我是記帳與待辦機器人

我可以幫助你和朋友們：
💰 記錄共同支出
💰 自動計算每個人應付的金額
💰 提供最佳還款方案
📝 管理群組待辦事項
📝 追蹤任務進度

輸入「說明」查看完整使用說明"""

                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(
                            text=welcome_message,
                            quick_reply=QuickReplyHelper.get_main_menu()
                        )]
                    )
                )

            logger.info(f"成功加入群組: {group_id}，成員將在發言時自動加入")

    except Exception as e:
        logger.error(f"處理加入群組事件時發生錯誤: {e}")


@line_handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    """處理成員加入群組事件"""
    try:
        group_id = event.source.group_id
        new_members = []

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)

            # 處理每位新加入的成員
            for member in event.joined.members:
                user_id = member.user_id
                if member.type != "user":
                    continue

                try:
                    # 取得使用者名稱
                    profile = line_bot_api.get_group_member_profile(group_id, user_id)
                    user_name = profile.display_name
                    picture_url = profile.picture_url if hasattr(profile, 'picture_url') else ''

                    # 更新使用者資料
                    firebase_service.create_or_update_user(user_id, user_name)

                    # 新增至群組成員
                    firebase_service.add_group_member(group_id, user_id, user_name, picture_url)

                    new_members.append(user_name)
                    logger.info(f"新成員加入: {user_name} ({user_id}) -> 群組 {group_id}")

                except Exception as e:
                    logger.error(f"處理新成員 {user_id} 時發生錯誤: {e}")

        if new_members:
            welcome_text = f"歡迎 {'、'.join(new_members)} 加入！🎉\n\n我已經將你們加入記帳名單囉！"

            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(
                            text=welcome_text,
                            quick_reply=QuickReplyHelper.get_main_menu()
                        )]
                    )
                )

    except Exception as e:
        logger.error(f"處理成員加入事件時發生錯誤: {e}")
