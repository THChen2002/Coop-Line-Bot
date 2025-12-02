# -*- coding: utf-8 -*-
from services.firebase_service import FirebaseService
from utils.parser import CommandParser
from handlers.expense_handler import ExpenseHandler
from handlers.settlement_handler import SettlementHandler
from handlers.todo_handler import TodoHandler
from utils.quick_reply import QuickReplyHelper
from utils.flex_message import FlexMessageHelper
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
import logging

logger = logging.getLogger(__name__)


class MessageHandler:
    """訊息處理器"""

    def __init__(self, firebase_service, line_configuration):
        self.firebase_service: FirebaseService = firebase_service
        self.line_configuration: Configuration = line_configuration
        self.expense_handler: ExpenseHandler = ExpenseHandler(firebase_service)
        self.settlement_handler: SettlementHandler = SettlementHandler(firebase_service)
        self.todo_handler: TodoHandler = TodoHandler()
        self.quick_reply_helper: QuickReplyHelper = QuickReplyHelper()

    def handle_text_message(
        self,
        text: str,
        user_id: str,
        user_name: str,
        group_id: str,
        is_group: bool = True
    ) -> str:
        """
        處理文字訊息
        返回回覆訊息
        """
        # 確保群組/聊天和使用者存在
        self._ensure_group_and_user(group_id, user_id, user_name, is_group)

        # 取得群組成員
        members = self.firebase_service.get_group_members(group_id)

        # 主選單
        if text.strip() in ['主選單', '選單', 'menu']:
            return {
                'type': 'text',
                'message': '請選擇功能：',
                'quick_reply': 'main_menu'
            }

        # 幫助指令
        if CommandParser.is_help_command(text):
            return {
                'type': 'flex',
                'message': FlexMessageHelper.create_help_message(),
                'quick_reply': 'main_menu'
            }

        # 記帳選單
        if text.strip() in ['記帳選單', '開啟記帳表單', '記帳表單', '新增記帳', '開啟表單']:
            return {
                'type': 'text',
                'message': '請選擇細項：',
                'quick_reply': 'expense_menu'
            }

        # 記帳指令（傳入當前使用者資訊）
        parsed = CommandParser.parse_expense_command(
            text,
            members,
            current_user_id=user_id,
            current_user_name=user_name
        )
        if parsed:
            return self.expense_handler.handle_create_expense(
                parsed, group_id, user_id, members
            )

        # 刪除指令
        expense_number = CommandParser.parse_delete_command(text)
        if expense_number:
            return self.expense_handler.handle_delete_expense(
                group_id, expense_number, user_id
            )

        # 查詢帳目
        if CommandParser.is_query_command(text):
            return self.expense_handler.handle_query_expenses(group_id)

        # 我的帳目
        if CommandParser.is_my_expenses_command(text):
            return self.expense_handler.handle_user_expenses(
                group_id, user_id, user_name
            )

        # 統計
        if CommandParser.is_statistics_command(text):
            return self.expense_handler.handle_statistics(group_id, members)

        # 結算
        if CommandParser.is_settlement_command(text):
            return self.settlement_handler.handle_settlement(group_id)

        # 清帳
        if CommandParser.is_clear_command(text):
            return self.settlement_handler.handle_clear_expenses(
                group_id, user_id, user_name
            )

        # ===== 待辦清單功能 =====

        # 待辦選單
        if text.strip() in ['待辦清單', '查看待辦', 'todo', 'TODO', '新增待辦', '建立待辦', '新待辦']:
            return {
                'type': 'text',
                'message': '請選擇細項：',
                'quick_reply': 'todo_menu'
            }

        # 查看待處理的待辦
        if text.strip() in ['待處理', '未完成', '進行中的待辦']:
            result = self.todo_handler.handle_list_todos(
                group_id=group_id,
                status='pending'
            )
            return result

        # 查看已完成的待辦
        if text.strip() in ['已完成', '完成的待辦']:
            result = self.todo_handler.handle_list_todos(
                group_id=group_id,
                status='completed'
            )
            return result

        # 待辦統計
        if text.strip() in ['待辦統計', 'todo統計', '待辦報表']:
            result = self.todo_handler.handle_statistics(group_id)
            return result

        # 未知指令
        return "無法識別的指令，請輸入「說明」查看使用方法"

    def _ensure_group_and_user(self, group_id: str, user_id: str, user_name: str, is_group: bool = True):
        """確保群組/聊天和使用者存在於資料庫

        Args:
            group_id: 群組 ID 或使用者 ID（一對一時）
            user_id: 使用者 ID
            user_name: 使用者名稱
            is_group: 是否為群組聊天（False 表示一對一聊天）
        """
        if is_group:
            # 群組聊天：建立或更新群組
            group = self.firebase_service.get_group(group_id)
            if not group:
                self.firebase_service.create_or_update_group(group_id, f"群組 {group_id[:8]}")

            # 確保使用者在群組中（檢查 members 列表是否包含此 user_id）
            members_list = self.firebase_service.get_group_members(group_id)
            member_ids = [m['id'] for m in members_list]

            if user_id not in member_ids:
                # 需要新增成員，從 LINE API 取得頭貼
                picture_url = ""
                try:
                    with ApiClient(self.line_configuration) as api_client:
                        line_bot_api = MessagingApi(api_client)
                        profile = line_bot_api.get_group_member_profile(group_id, user_id)
                        picture_url = profile.picture_url if hasattr(profile, 'picture_url') else ""
                except Exception as e:
                    logger.warning(f"無法取得使用者 {user_id} 的頭貼: {e}")

                # 新增成員到群組和 users 集合
                self.firebase_service.add_group_member(group_id, user_id, user_name, picture_url)
            else:
                # 成員已存在，只更新 users 集合的基本資料（不更新頭貼避免覆蓋）
                self.firebase_service.create_or_update_user(user_id, user_name)
        else:
            # 一對一聊天：建立或更新聊天記錄和使用者
            self.firebase_service.create_or_update_chat(user_id, user_name)
            self.firebase_service.create_or_update_user(user_id, user_name)
