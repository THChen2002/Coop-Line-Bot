from typing import Dict
from services.firebase_service import FirebaseService
from services.expense_service import ExpenseService
from services.settlement_service import SettlementService
from utils.formatter import MessageFormatter


class ExpenseHandler:
    """記帳處理器"""

    def __init__(self, firebase_service: FirebaseService):
        self.firebase_service: FirebaseService = firebase_service
        self.expense_service: ExpenseService = ExpenseService()
        self.settlement_service: SettlementService = SettlementService()

    def handle_create_expense(
        self,
        parsed_data: Dict,
        group_id: str,
        user_id: str,
        members: Dict
    ) -> str:
        """處理建立支出記錄"""
        # 檢查解析是否有效
        if not parsed_data.get('valid'):
            return MessageFormatter.format_error(
                parsed_data.get('error', '指令格式錯誤')
            )

        # 根據分帳類型計算分帳明細
        split_type = parsed_data['split_type']
        amount = parsed_data['amount']

        if split_type == 'equal':
            splits = self.expense_service.calculate_equal_split(amount, members)
        elif split_type == 'selected':
            splits = self.expense_service.calculate_selected_split(
                amount, parsed_data['split_members']
            )
        elif split_type == 'ratio':
            ratios = parsed_data.get('ratios', [])
            if len(ratios) != len(members):
                return MessageFormatter.format_error(
                    f'比例數量 ({len(ratios)}) 與成員數量 ({len(members)}) 不符'
                )
            splits = self.expense_service.calculate_ratio_split(
                amount, members, ratios
            )
        else:
            return MessageFormatter.format_error('不支援的分帳類型')

        if not splits:
            return MessageFormatter.format_error('無法計算分帳明細')

        # 建立支出記錄資料
        expense_data = self.expense_service.create_expense_data(
            group_id=group_id,
            payer_id=parsed_data['payer_id'],
            payer_name=parsed_data['payer_name'],
            amount=amount,
            description=parsed_data['description'],
            split_type=split_type,
            splits=splits,
            created_by=user_id
        )

        # 驗證資料
        valid, error_msg = self.expense_service.validate_expense_data(expense_data)
        if not valid:
            return MessageFormatter.format_error(error_msg)

        # 儲存到 Firebase
        try:
            expense_id = self.firebase_service.create_expense(expense_data)
            # 重新取得完整資料（包含 expense_number）
            expense = self.firebase_service.get_expense(expense_id)
            return MessageFormatter.format_expense_success(expense, splits)
        except Exception as e:
            return MessageFormatter.format_error(f'記帳失敗: {str(e)}')

    def handle_delete_expense(
        self,
        group_id: str,
        expense_number: int,
        user_id: str
    ) -> str:
        """處理刪除支出記錄"""
        # 根據編號查詢支出記錄
        expense = self.firebase_service.get_expense_by_number(group_id, expense_number)

        if not expense:
            return MessageFormatter.format_error(f'找不到帳目 #{expense_number:03d}')

        # 檢查權限（只有建立者可以刪除）
        if expense.get('created_by') != user_id:
            return MessageFormatter.format_error('只有建立者可以刪除此帳目')

        # 刪除
        try:
            success = self.firebase_service.delete_expense(expense['id'])
            if success:
                return MessageFormatter.format_delete_success(expense_number)
            else:
                return MessageFormatter.format_error('刪除失敗')
        except Exception as e:
            return MessageFormatter.format_error(f'刪除失敗: {str(e)}')

    def handle_query_expenses(self, group_id: str) -> str:
        """處理查詢帳目"""
        try:
            expenses = self.firebase_service.get_group_expenses(
                group_id, is_settled=False, limit=50
            )
            return MessageFormatter.format_expense_list(expenses)
        except Exception as e:
            return MessageFormatter.format_error(f'查詢失敗: {str(e)}')

    def handle_user_expenses(
        self,
        group_id: str,
        user_id: str,
        user_name: str
    ) -> str:
        """處理查詢個人帳目"""
        try:
            expenses = self.firebase_service.get_group_expenses(
                group_id, is_settled=False
            )
            return MessageFormatter.format_user_expenses(user_id, user_name, expenses)
        except Exception as e:
            return MessageFormatter.format_error(f'查詢失敗: {str(e)}')

    def handle_statistics(self, group_id: str, members: Dict) -> str:
        """處理統計查詢"""
        try:
            expenses = self.firebase_service.get_group_expenses(
                group_id, is_settled=False
            )
            return MessageFormatter.format_statistics(expenses, members)
        except Exception as e:
            return MessageFormatter.format_error(f'查詢失敗: {str(e)}')
