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
    """
    try:
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
