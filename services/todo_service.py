# -*- coding: utf-8 -*-
from typing import List, Dict, Optional
from datetime import datetime
from models.todo import Todo
from services.firebase_service import FirebaseService
import logging

logger = logging.getLogger(__name__)


class TodoService:
    """待辦事項服務"""

    def __init__(self):
        self.db = FirebaseService()

    def create_todo(self, todo_data: Dict) -> Dict:
        """建立待辦事項"""
        try:
            todo_id = self.db.create('todos', todo_data)
            return {'success': True, 'todo_id': todo_id}
        except Exception as e:
            logger.error(f"建立待辦事項失敗: {e}")
            return {'success': False, 'error': str(e)}

    def get_todo(self, todo_id: str) -> Optional[Todo]:
        """取得單一待辦事項"""
        try:
            data = self.db.get('todos', todo_id)
            if data:
                return Todo.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"取得待辦事項失敗: {e}")
            return None

    def get_group_todos(self, group_id: str, status: Optional[str] = None, category: Optional[str] = None) -> List[Todo]:
        """取得群組的所有待辦事項"""
        try:
            # 建立查詢條件
            conditions = [('group_id', '==', group_id)]

            if status:
                conditions.append(('status', '==', status))

            if category:
                conditions.append(('category', '==', category))

            results = self.db.query('todos', conditions, order_by='created_at', order_direction='desc')

            return [Todo.from_dict(data) for data in results]
        except Exception as e:
            logger.error(f"取得群組待辦事項失敗: {e}")
            return []

    def get_user_todos(self, group_id: str, user_id: str, status: Optional[str] = None) -> List[Todo]:
        """取得使用者的待辦事項"""
        try:
            conditions = [
                ('group_id', '==', group_id),
                ('assignee_id', '==', user_id)
            ]

            if status:
                conditions.append(('status', '==', status))

            results = self.db.query('todos', conditions, order_by='created_at',
                                   order_direction='desc')

            return [Todo.from_dict(data) for data in results]
        except Exception as e:
            logger.error(f"取得使用者待辦事項失敗: {e}")
            return []

    def update_todo(self, todo_id: str, updates: Dict) -> Dict:
        """更新待辦事項"""
        try:
            updates['updated_at'] = datetime.now()

            # 如果狀態更新為已完成，記錄完成時間
            if 'status' in updates and updates['status'] == 'completed':
                updates['completed_at'] = datetime.now()

            success = self.db.update('todos', todo_id, updates)
            return {'success': success}
        except Exception as e:
            logger.error(f"更新待辦事項失敗: {e}")
            return {'success': False, 'error': str(e)}

    def delete_todo(self, todo_id: str) -> Dict:
        """刪除待辦事項"""
        try:
            success = self.db.delete('todos', todo_id)
            return {'success': success}
        except Exception as e:
            logger.error(f"刪除待辦事項失敗: {e}")
            return {'success': False, 'error': str(e)}

    def mark_completed(self, todo_id: str) -> Dict:
        """標記為已完成"""
        return self.update_todo(todo_id, {
            'status': 'completed',
            'completed_at': datetime.now()
        })

    def mark_in_progress(self, todo_id: str) -> Dict:
        """標記為進行中"""
        return self.update_todo(todo_id, {'status': 'in_progress'})

    def get_categories(self, group_id: str) -> List[str]:
        """取得群組的所有類別"""
        try:
            todos = self.get_group_todos(group_id)
            categories = set()

            for todo in todos:
                if todo.category:
                    categories.add(todo.category)

            # 加入預設類別
            default_categories = ['一般', '工作', '學習', '生活', '購物', '其他']
            categories.update(default_categories)

            return sorted(list(categories))
        except Exception as e:
            logger.error(f"取得類別失敗: {e}")
            return ['一般', '工作', '學習', '生活', '購物', '其他']

    def get_statistics(self, group_id: str) -> Dict:
        """取得待辦事項統計"""
        try:
            todos = self.get_group_todos(group_id)

            total = len(todos)
            pending = len([t for t in todos if t.status == 'pending'])
            in_progress = len([t for t in todos if t.status == 'in_progress'])
            completed = len([t for t in todos if t.status == 'completed'])

            # 按類別統計
            by_category = {}
            for todo in todos:
                category = todo.category or '未分類'
                by_category[category] = by_category.get(category, 0) + 1

            # 按負責人統計
            by_assignee = {}
            for todo in todos:
                if todo.assignee_name:
                    assignee = todo.assignee_name
                    by_assignee[assignee] = by_assignee.get(assignee, 0) + 1

            return {
                'total': total,
                'pending': pending,
                'in_progress': in_progress,
                'completed': completed,
                'completion_rate': (completed / total * 100) if total > 0 else 0,
                'by_category': by_category,
                'by_assignee': by_assignee
            }
        except Exception as e:
            logger.error(f"取得統計資料失敗: {e}")
            return {
                'total': 0,
                'pending': 0,
                'in_progress': 0,
                'completed': 0,
                'completion_rate': 0,
                'by_category': {},
                'by_assignee': {}
            }
