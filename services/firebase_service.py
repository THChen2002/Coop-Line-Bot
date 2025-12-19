import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Query
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore import SERVER_TIMESTAMP, ArrayUnion
from typing import Optional, Dict, List, Any
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
                'updated_at': SERVER_TIMESTAMP
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
                'created_at': SERVER_TIMESTAMP,
                'updated_at': SERVER_TIMESTAMP
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

    def create_group(self, group_name: str, created_by: str) -> Dict:
        """建立群組

        Args:
            group_name: 群組名稱
            created_by: 建立者 user_id

        Returns:
            群組資料包含 id 和 group_code
        """
        from models.group import Group

        try:
            group = Group(group_name=group_name, created_by=created_by)
            group_data = group.to_dict()

            # created_at 使用 SERVER_TIMESTAMP
            group_data['created_at'] = SERVER_TIMESTAMP

            # 建立文件
            doc_ref = self._db.collection('groups').document()
            doc_ref.set(group_data)

            logger.info(f"群組 {group_name} (code: {group.group_code}) 建立成功")

            return {
                'id': doc_ref.id,
                'group_code': group.group_code,
                'group_name': group_name,
                'created_by': created_by
            }
        except Exception as e:
            logger.error(f"建立群組失敗: {e}")
            raise

    def get_group_by_code(self, group_code: str) -> Optional[Dict]:
        """透過群組代碼取得群組

        Args:
            group_code: 群組代碼

        Returns:
            群組資料或 None
        """
        try:
            groups = self._db.collection('groups')\
                .where(filter=FieldFilter('group_code', '==', group_code))\
                .limit(1)\
                .stream()

            for group in groups:
                data = group.to_dict()
                data['id'] = group.id
                return data

            return None
        except Exception as e:
            logger.error(f"查詢群組失敗: {e}")
            return None

    def join_group(self, group_id: str, user_id: str) -> bool:
        """加入群組

        Args:
            group_id: 群組 ID
            user_id: 使用者 ID

        Returns:
            是否成功加入
        """
        try:
            group_ref = self._db.collection('groups').document(group_id)
            group_ref.update({
                'members': ArrayUnion([user_id])
            })
            logger.info(f"使用者 {user_id} 加入群組 {group_id}")
            return True
        except Exception as e:
            logger.error(f"加入群組失敗: {e}")
            return False

    def get_user_groups(self, user_id: str) -> List[Dict]:
        """取得使用者加入的所有群組

        Args:
            user_id: 使用者 ID

        Returns:
            群組列表
        """
        try:
            groups = self._db.collection('groups')\
                .where(filter=FieldFilter('members', 'array_contains', user_id))\
                .where(filter=FieldFilter('is_active', '==', True))\
                .order_by('created_at', direction=Query.DESCENDING)\
                .stream()

            result = []
            for group in groups:
                data = group.to_dict()
                data['id'] = group.id
                result.append(data)

            return result
        except Exception as e:
            logger.error(f"取得使用者群組失敗: {e}")
            return []

    def delete_group(self, group_id: str) -> bool:
        """刪除群組及其所有相關資料

        Args:
            group_id: 群組 ID

        Returns:
            是否成功刪除
        """
        try:
            # 使用 batch 操作確保原子性
            batch = self._db.batch()

            # 1. 刪除群組的所有 expenses
            expenses = self._db.collection('expenses')\
                .where(filter=FieldFilter('group_id', '==', group_id))\
                .stream()

            for expense in expenses:
                batch.delete(expense.reference)

            # 2. 刪除群組的所有 todos
            todos = self._db.collection('todos')\
                .where(filter=FieldFilter('group_id', '==', group_id))\
                .stream()

            for todo in todos:
                batch.delete(todo.reference)

            # 3. 刪除群組的所有 settlements
            settlements = self._db.collection('settlements')\
                .where(filter=FieldFilter('group_id', '==', group_id))\
                .stream()

            for settlement in settlements:
                batch.delete(settlement.reference)

            # 4. 刪除群組本身
            group_ref = self._db.collection('groups').document(group_id)
            batch.delete(group_ref)

            # 提交批次操作
            batch.commit()

            logger.info(f"群組 {group_id} 及其所有相關資料已刪除")
            return True
        except Exception as e:
            logger.error(f"刪除群組失敗: {e}")
            return False

    # ===== 支出記錄相關操作 =====

    def create_expense(self, expense_data: Dict) -> str:
        """建立支出記錄"""
        # 取得群組內的下一個帳目編號
        expense_number = self._get_next_expense_number(expense_data['group_id'])

        expense_data['expense_number'] = expense_number
        expense_data['created_at'] = SERVER_TIMESTAMP
        expense_data['is_settled'] = False

        doc_ref = self._db.collection('expenses').add(expense_data)
        return doc_ref[1].id

    def _get_next_expense_number(self, group_id: str) -> int:
        """取得群組內的下一個帳目編號"""
        expenses = self._db.collection('expenses')\
            .where(filter=FieldFilter('group_id', '==', group_id))\
            .order_by('expense_number', direction=Query.DESCENDING)\
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

    def get_group_expenses(self, group_id: str, is_settled: bool = None, limit: int = 50) -> List[Dict]:
        """取得群組的支出記錄

        Args:
            group_id: 群組 ID
            is_settled: 是否已結算。None 表示取得所有帳目（不過濾）
            limit: 限制回傳數量

        Returns:
            支出記錄列表
        """
        # 如果 is_settled 為 None，分別查詢未結算和已結算的帳目，然後合併
        if is_settled is None:
            unsettled = self.get_group_expenses(group_id, is_settled=False, limit=limit)
            settled = self.get_group_expenses(group_id, is_settled=True, limit=limit)
            # 合併並按 created_at 排序
            all_expenses = unsettled + settled
            all_expenses.sort(key=lambda x: x.get('created_at'), reverse=True)
            return all_expenses[:limit]

        # 原有邏輯：查詢特定 is_settled 狀態的帳目
        expenses = self._db.collection('expenses')\
            .where(filter=FieldFilter('group_id', '==', group_id))\
            .where(filter=FieldFilter('is_settled', '==', is_settled))\
            .order_by('created_at', direction=Query.DESCENDING)\
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
            .where(filter=FieldFilter('group_id', '==', group_id))\
            .where(filter=FieldFilter('expense_number', '==', expense_number))\
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
            .where(filter=FieldFilter('group_id', '==', group_id))\
            .where(filter=FieldFilter('is_settled', '==', False))\
            .stream()

        batch = self._db.batch()
        for expense in expenses:
            batch.update(expense.reference, {'is_settled': True})

        batch.commit()

    # ===== 結算記錄相關操作 =====

    def create_settlement(self, settlement_data: Dict) -> str:
        """建立結算記錄"""
        settlement_data['settled_at'] = SERVER_TIMESTAMP

        doc_ref = self._db.collection('settlements').add(settlement_data)
        return doc_ref[1].id

    def get_group_settlements(self, group_id: str, limit: int = 10) -> List[Dict]:
        """取得群組的結算記錄"""
        settlements = self._db.collection('settlements')\
            .where(filter=FieldFilter('group_id', '==', group_id))\
            .order_by('settled_at', direction=Query.DESCENDING)\
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
            query = query.where(filter=FieldFilter(field, operator, value))

        # 排序
        if order_by:
            direction = Query.DESCENDING if order_direction == 'desc' else Query.ASCENDING
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
