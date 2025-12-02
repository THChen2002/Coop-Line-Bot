# -*- coding: utf-8 -*-
"""LINE Bot 輔助工具"""

from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    ShowLoadingAnimationRequest
)
import logging

logger = logging.getLogger(__name__)


def show_loading_animation(configuration, event, loading_seconds: int = 10):
    """顯示 LINE loading animation（僅限一對一聊天）

    Args:
        configuration: LINE Bot Configuration
        event: LINE 事件物件
        loading_seconds: 動畫顯示時間（秒），最大 60 秒

    Note:
        loading animation 只能在一對一聊天室使用，群組聊天不支援
    """
    try:
        # 只在一對一聊天室顯示 loading animation
        # 群組聊天不支援此功能
        if hasattr(event.source, 'group_id') or hasattr(event.source, 'room_id'):
            # 群組或聊天室，不顯示 loading animation
            logger.debug("群組聊天不支援 loading animation")
            return

        # 一對一聊天
        chat_id = event.source.user_id
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.show_loading_animation(
                ShowLoadingAnimationRequest(
                    chatId=chat_id,
                    loadingSeconds=min(loading_seconds, 60)  # 確保不超過 60 秒
                )
            )
            logger.debug(f"顯示 loading animation: {chat_id}, {loading_seconds}s")
    except Exception as e:
        logger.warning(f"顯示 loading animation 失敗: {e}")


def get_chat_id(event):
    """從事件中取得 chat_id

    Args:
        event: LINE 事件物件

    Returns:
        str: chat_id (群組 ID 或使用者 ID)
    """
    if hasattr(event.source, 'group_id'):
        return event.source.group_id
    elif hasattr(event.source, 'room_id'):
        return event.source.room_id
    else:
        return event.source.user_id
