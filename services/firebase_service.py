import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import Optional, Dict, List, Any
import os
import logging

logger = logging.getLogger(__name__)


class FirebaseService:
    """Firebase Firestore 服務類"""

    _instance = None
    _db = None

    def __new__(cls):
        """單例模式確保只有一個 Firebase 連接"""
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化 Firebase"""
        if self._db is None:
            self._initialize_firebase()

    def _initialize_firebase(self):
        """初始化 Firebase Admin SDK"""
        try:
            from config import Config
            import json

            firebase_config = Config.FIREBASE_CREDENTIALS

            if not firebase_config:
                raise ValueError("FIREBASE_CREDENTIALS 環境變數未設定")

            # 解析 JSON 字串
            cred_dict = json.loads(firebase_config)

            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            self._db = firestore.client()
            logger.info("Firebase 初始化成功")
        except Exception as e:
            logger.error(f"Firebase 初始化失敗: {e}")
            raise

    @property
    def db(self):
        """取得 Firestore 資料庫實例"""
        return self._db

    # ===== 使用者相關操作 =====

    def create_or_update_user(self, line_user_id: str, display_name: str, picture_url: str = '') -> Dict:
        """建立或更新使用者"""
        user_ref = self._db.collection('users').document(line_user_id)
        user_data = user_ref.get()

        if user_data.exists:
            # 更新使用者
            update_data = {
                'display_name': display_name,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            if picture_url:
                update_data['picture_url'] = picture_url
            user_ref.update(update_data)
        else:
            # 建立新使用者
            user_ref.set({
                'line_user_id': line_user_id,
                'display_name': display_name,
                'picture_url': picture_url,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            })

        return {'line_user_id': line_user_id, 'display_name': display_name}

    def get_user(self, line_user_id: str) -> Optional[Dict]:
        """取得使用者資料"""
        user_ref = self._db.collection('users').document(line_user_id)
        user_data = user_ref.get()

        if user_data.exists:
            return user_data.to_dict()
        return None

    # ===== 群組相關操作 =====

    def create_or_update_group(self, line_group_id: str, group_name: str) -> Dict:
        """建立或更新群組"""
        group_ref = self._db.collection('groups').document(line_group_id)
        group_data = group_ref.get()

        if group_data.exists:
            # 更新群組名稱
            group_ref.update({
                'group_name': group_name,
                'is_active': True
            })
        else:
            # 建立新群組
            group_ref.set({
                'line_group_id': line_group_id,
                'group_name': group_name,
                'created_at': firestore.SERVER_TIMESTAMP,
                'is_active': True,
                'members': {}
            })

        return {'line_group_id': line_group_id, 'group_name': group_name}

    def create_group(self, line_group_id: str, group_name: str) -> bool:
        """建立群組

        Args:
            line_group_id: LINE 群組 ID
            group_name: 群組名稱

        Returns:
            是否建立成功
        """
        try:
            group_data = {
                'line_group_id': line_group_id,
                'group_name': group_name,
                'created_at': firestore.SERVER_TIMESTAMP,
                'is_active': True,
                'members': []  # 空列表，成員會在發言時加入
            }

            self._db.collection('groups').document(line_group_id).set(group_data)
            logger.info(f"群組 {line_group_id} 建立成功")
            return True
        except Exception as e:
            logger.error(f"建立群組失敗: {e}")
            return False

    def add_group_member(self, line_group_id: str, line_user_id: str, display_name: str, picture_url: str = ''):
        """新增群組成員（只儲存 user_id 到列表）

        Args:
            line_group_id: LINE 群組 ID
            line_user_id: LINE 使用者 ID
            display_name: 顯示名稱
            picture_url: 大頭貼 URL（可選）
        """
        try:
            # 將 user_id 加入群組的 members 列表
            group_ref = self._db.collection('groups').document(line_group_id)
            group_ref.update({
                'members': firestore.ArrayUnion([line_user_id])
            })

            # 將用戶詳細資料存到 users 集合
            self.create_or_update_user(line_user_id, display_name, picture_url)

            logger.info(f"成員 {display_name} ({line_user_id}) 已加入群組 {line_group_id}")
        except Exception as e:
            logger.error(f"新增群組成員失敗: {e}")

    def get_group(self, line_group_id: str) -> Optional[Dict]:
        """取得群組資料"""
        group_ref = self._db.collection('groups').document(line_group_id)
        group_data = group_ref.get()

        if group_data.exists:
            return group_data.to_dict()
        return None

    def get_group_members(self, line_group_id: str) -> list:
        """取得群組成員列表（含詳細資料）

        Returns:
            成員列表，格式: [{'id': user_id, 'name': display_name, 'picture_url': url}, ...]
        """
        group = self.get_group(line_group_id)
        if not group or 'members' not in group:
            return []

        member_ids = group['members']
        members_with_details = []

        # 從 users 集合取得每個成員的詳細資料
        for user_id in member_ids:
            user = self.get_user(user_id)
            if user:
                members_with_details.append({
                    'id': user_id,
                    'name': user.get('display_name', '未知用戶'),
                    'picture_url': user.get('picture_url') or 'https://static.line-scdn.net/line_web_login/1980c203b61/dist/image/default@2x.png'
                })

        return members_with_details

    # ===== 一對一聊天相關操作 =====

    def create_or_update_chat(self, line_user_id: str, user_name: str) -> Dict:
        """建立或更新一對一聊天記錄

        Args:
            line_user_id: LINE 使用者 ID
            user_name: 使用者顯示名稱

        Returns:
            聊天記錄字典
        """
        chat_ref = self._db.collection('chats').document(line_user_id)
        chat_data = chat_ref.get()

        if chat_data.exists:
            # 更新聊天記錄
            chat_ref.update({
                'user_name': user_name,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
        else:
            # 建立新聊天記錄
            chat_ref.set({
                'line_user_id': line_user_id,
                'user_name': user_name,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'is_active': True
            })

        return {'line_user_id': line_user_id, 'user_name': user_name}

    def get_chat(self, line_user_id: str) -> Optional[Dict]:
        """取得一對一聊天記錄

        Args:
            line_user_id: LINE 使用者 ID

        Returns:
            聊天記錄字典或 None
        """
        chat_ref = self._db.collection('chats').document(line_user_id)
        chat_data = chat_ref.get()

        if chat_data.exists:
            return chat_data.to_dict()
        return None

    # ===== 支出記錄相關操作 =====

    def create_expense(self, expense_data: Dict) -> str:
        """建立支出記錄"""
        # 取得群組內的下一個帳目編號
        expense_number = self._get_next_expense_number(expense_data['group_id'])

        expense_data['expense_number'] = expense_number
        expense_data['created_at'] = firestore.SERVER_TIMESTAMP
        expense_data['is_settled'] = False

        doc_ref = self._db.collection('expenses').add(expense_data)
        return doc_ref[1].id

    def _get_next_expense_number(self, group_id: str) -> int:
        """取得群組內的下一個帳目編號"""
        expenses = self._db.collection('expenses')\
            .where(filter=firestore.FieldFilter('group_id', '==', group_id))\
            .order_by('expense_number', direction=firestore.Query.DESCENDING)\
            .limit(1)\
            .stream()

        for expense in expenses:
            return expense.to_dict().get('expense_number', 0) + 1

        return 1

    def get_expense(self, expense_id: str) -> Optional[Dict]:
        """取得單筆支出記錄"""
        expense_ref = self._db.collection('expenses').document(expense_id)
        expense_data = expense_ref.get()

        if expense_data.exists:
            data = expense_data.to_dict()
            data['id'] = expense_id
            return data
        return None

    def get_group_expenses(self, group_id: str, is_settled: bool = False, limit: int = 50) -> List[Dict]:
        """取得群組的支出記錄"""
        expenses = self._db.collection('expenses')\
            .where(filter=firestore.FieldFilter('group_id', '==', group_id))\
            .where(filter=firestore.FieldFilter('is_settled', '==', is_settled))\
            .order_by('created_at', direction=firestore.Query.DESCENDING)\
            .limit(limit)\
            .stream()

        result = []
        for expense in expenses:
            data = expense.to_dict()
            data['id'] = expense.id
            result.append(data)

        return result

    def get_expense_by_number(self, group_id: str, expense_number: int) -> Optional[Dict]:
        """根據帳目編號取得支出記錄"""
        expenses = self._db.collection('expenses')\
            .where(filter=firestore.FieldFilter('group_id', '==', group_id))\
            .where(filter=firestore.FieldFilter('expense_number', '==', expense_number))\
            .limit(1)\
            .stream()

        for expense in expenses:
            data = expense.to_dict()
            data['id'] = expense.id
            return data

        return None

    def delete_expense(self, expense_id: str) -> bool:
        """刪除支出記錄"""
        try:
            self._db.collection('expenses').document(expense_id).delete()
            return True
        except Exception as e:
            logger.error(f"刪除支出記錄失敗: {e}")
            return False

    def settle_expenses(self, group_id: str):
        """將群組的所有未結算支出標記為已結算"""
        expenses = self._db.collection('expenses')\
            .where(filter=firestore.FieldFilter('group_id', '==', group_id))\
            .where(filter=firestore.FieldFilter('is_settled', '==', False))\
            .stream()

        batch = self._db.batch()
        for expense in expenses:
            batch.update(expense.reference, {'is_settled': True})

        batch.commit()

    # ===== 結算記錄相關操作 =====

    def create_settlement(self, settlement_data: Dict) -> str:
        """建立結算記錄"""
        settlement_data['settled_at'] = firestore.SERVER_TIMESTAMP

        doc_ref = self._db.collection('settlements').add(settlement_data)
        return doc_ref[1].id

    def get_group_settlements(self, group_id: str, limit: int = 10) -> List[Dict]:
        """取得群組的結算記錄"""
        settlements = self._db.collection('settlements')\
            .where(filter=firestore.FieldFilter('group_id', '==', group_id))\
            .order_by('settled_at', direction=firestore.Query.DESCENDING)\
            .limit(limit)\
            .stream()

        result = []
        for settlement in settlements:
            data = settlement.to_dict()
            data['id'] = settlement.id
            result.append(data)

        return result

    # ===== 通用 CRUD 操作 =====

    def create(self, collection: str, data: Dict) -> str:
        """建立文件（通用）"""
        doc_ref = self._db.collection(collection).add(data)
        return doc_ref[1].id

    def get(self, collection: str, doc_id: str) -> Optional[Dict]:
        """取得文件（通用）"""
        doc_ref = self._db.collection(collection).document(doc_id)
        doc_data = doc_ref.get()

        if doc_data.exists:
            data = doc_data.to_dict()
            data['id'] = doc_id
            return data
        return None

    def update(self, collection: str, doc_id: str, data: Dict) -> bool:
        """更新文件（通用）"""
        try:
            self._db.collection(collection).document(doc_id).update(data)
            return True
        except Exception as e:
            logger.error(f"更新文件失敗: {e}")
            return False

    def delete(self, collection: str, doc_id: str) -> bool:
        """刪除文件（通用）"""
        try:
            self._db.collection(collection).document(doc_id).delete()
            return True
        except Exception as e:
            logger.error(f"刪除文件失敗: {e}")
            return False

    def query(self, collection: str, conditions: List[tuple],
              order_by: Optional[str] = None,
              order_direction: str = 'asc',
              limit: Optional[int] = None) -> List[Dict]:
        """查詢文件（通用）

        Args:
            collection: Collection 名稱
            conditions: 查詢條件列表 [('field', 'operator', 'value'), ...]
            order_by: 排序欄位
            order_direction: 排序方向 ('asc' or 'desc')
            limit: 限制數量

        Returns:
            文件列表
        """
        query = self._db.collection(collection)

        # 加入查詢條件
        for field, operator, value in conditions:
            query = query.where(filter=firestore.FieldFilter(field, operator, value))

        # 排序
        if order_by:
            direction = firestore.Query.DESCENDING if order_direction == 'desc' else firestore.Query.ASCENDING
            query = query.order_by(order_by, direction=direction)

        # 限制數量
        if limit:
            query = query.limit(limit)

        # 執行查詢
        result = []
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            result.append(data)

        return result


# 建立全域實例
firebase_service = FirebaseService()
