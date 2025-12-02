# -*- coding: utf-8 -*-
from typing import Dict
from services.todo_service import TodoService
from utils.flex_message import FlexMessageHelper
import logging

logger = logging.getLogger(__name__)


class TodoHandler:
    """待辦事項處理器"""

    def __init__(self):
        self.todo_service = TodoService()

    def handle_list_todos(self, group_id: str, user_id: str = None, status: str = None, category: str = None) -> Dict:
        """處理列出待辦事項"""
        try:
            if user_id:
                todos = self.todo_service.get_user_todos(group_id, user_id, status)
            else:
                todos = self.todo_service.get_group_todos(group_id, status, category)

            if not todos:
                return {
                    'type': 'flex',
                    'message': FlexMessageHelper.create_info_message(
                        "📝 待辦清單",
                        "目前沒有待辦事項"
                    )
                }

            # 使用 Flex Message 顯示待辦清單
            flex_message = FlexMessageHelper.create_todo_list(todos)

            return {
                'type': 'flex',
                'message': flex_message
            }
        except Exception as e:
            logger.error(f"列出待辦事項失敗: {e}")
            return {
                'type': 'text',
                'text': f"❌ 取得待辦事項失敗：{str(e)}"
            }

    def handle_create_todo(self, todo_data: Dict) -> Dict:
        """處理建立待辦事項"""
        try:
            result = self.todo_service.create_todo(todo_data)

            if result['success']:
                return {
                    'type': 'flex',
                    'message': FlexMessageHelper.create_success_message(
                        f"待辦事項「{todo_data['title']}」已建立"
                    )
                }
            else:
                return {
                    'type': 'text',
                    'text': f"❌ 建立失敗：{result.get('error', '未知錯誤')}"
                }
        except Exception as e:
            logger.error(f"建立待辦事項失敗: {e}")
            return {
                'type': 'text',
                'text': f"❌ 建立待辦事項失敗：{str(e)}"
            }

    def handle_update_todo(self, todo_id: str, updates: Dict) -> Dict:
        """處理更新待辦事項"""
        try:
            result = self.todo_service.update_todo(todo_id, updates)

            if result['success']:
                return {
                    'type': 'flex',
                    'message': FlexMessageHelper.create_success_message('待辦事項已更新')
                }
            else:
                return {
                    'type': 'text',
                    'text': f"❌ 更新失敗：{result.get('error', '未知錯誤')}"
                }
        except Exception as e:
            logger.error(f"更新待辦事項失敗: {e}")
            return {
                'type': 'text',
                'text': f"❌ 更新待辦事項失敗：{str(e)}"
            }

    def handle_delete_todo(self, todo_id: str) -> Dict:
        """處理刪除待辦事項"""
        try:
            result = self.todo_service.delete_todo(todo_id)

            if result['success']:
                return {
                    'type': 'flex',
                    'message': FlexMessageHelper.create_success_message('待辦事項已刪除')
                }
            else:
                return {
                    'type': 'text',
                    'text': f"❌ 刪除失敗：{result.get('error', '未知錯誤')}"
                }
        except Exception as e:
            logger.error(f"刪除待辦事項失敗: {e}")
            return {
                'type': 'text',
                'text': f"❌ 刪除待辦事項失敗：{str(e)}"
            }

    def handle_complete_todo(self, todo_id: str) -> Dict:
        """處理完成待辦事項"""
        try:
            todo = self.todo_service.get_todo(todo_id)
            if not todo:
                return {
                    'type': 'text',
                    'text': "❌ 找不到該待辦事項"
                }

            result = self.todo_service.mark_completed(todo_id)

            if result['success']:
                return {
                    'type': 'flex',
                    'message': FlexMessageHelper.create_success_message(
                        f"待辦事項「{todo.title}」已完成"
                    )
                }
            else:
                return {
                    'type': 'text',
                    'text': f"❌ 標記完成失敗：{result.get('error', '未知錯誤')}"
                }
        except Exception as e:
            logger.error(f"完成待辦事項失敗: {e}")
            return {
                'type': 'text',
                'text': f"❌ 完成待辦事項失敗：{str(e)}"
            }

    def handle_statistics(self, group_id: str) -> Dict:
        """處理統計資料"""
        try:
            stats = self.todo_service.get_statistics(group_id)

            # 準備統計資料
            stat_data = {
                "總計": f"{stats['total']} 項",
                "⏳ 待處理": f"{stats['pending']} 項",
                "🔄 進行中": f"{stats['in_progress']} 項",
                "✅ 已完成": f"{stats['completed']} 項",
                "📈 完成率": f"{stats['completion_rate']:.1f}%"
            }

            # 加入類別統計
            if stats['by_category']:
                stat_data[""] = "—————"  # 分隔線
                for category, count in stats['by_category'].items():
                    stat_data[f"📁 {category}"] = f"{count} 項"

            # 加入負責人統計
            if stats['by_assignee']:
                stat_data[" "] = "—————"  # 分隔線
                for assignee, count in stats['by_assignee'].items():
                    stat_data[f"👤 {assignee}"] = f"{count} 項"

            return {
                'type': 'flex',
                'message': FlexMessageHelper.create_statistics_message(
                    "📊 待辦事項統計",
                    stat_data
                )
            }
        except Exception as e:
            logger.error(f"取得統計失敗: {e}")
            return {
                'type': 'text',
                'text': f"❌ 取得統計失敗：{str(e)}"
            }
