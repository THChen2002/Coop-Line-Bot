# -*- coding: utf-8 -*-
from services.firebase_service import FirebaseService
import logging

logger = logging.getLogger(__name__)


class MessageHandler:
    """訊息處理器（僅支援一對一聊天）"""

    def __init__(self, firebase_service):
        self.firebase_service: FirebaseService = firebase_service

    def handle_text_message(
        self,
        text: str,
        user_id: str,
        user_name: str
    ) -> str:
        """
        處理文字訊息（僅支援一對一聊天）
        返回回覆訊息
        """
        # 確保聊天和使用者存在
        self.firebase_service.create_or_update_user(user_id, user_name)

        # 主選單
        if text.strip() in ['主選單', '選單', 'menu', '說明', '幫助', 'help']:
            return '👋 歡迎使用記帳與待辦機器人\n\n請使用 LINE 選單開啟功能頁面'

        # 未知指令
        return "無法識別的指令。請使用 LINE 選單開啟功能。"
