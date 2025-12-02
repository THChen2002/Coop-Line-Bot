from typing import Dict, List, Optional
from models.expense import Expense, ExpenseSplit


class ExpenseService:
    """記帳邏輯服務"""

    @staticmethod
    def calculate_equal_split(amount: float, members: Dict) -> List[Dict]:
        """
        計算平均分帳
        amount: 總金額
        members: 群組成員字典 {user_id: {display_name, joined_at}}
        """
        if not members:
            return []

        member_count = len(members)
        per_person = amount / member_count

        splits = []
        for user_id, member_data in members.items():
            split = ExpenseSplit(
                user_id=user_id,
                user_name=member_data.get('display_name', '未知'),
                amount=per_person,
                is_paid=False
            )
            splits.append(split.to_dict())

        return splits

    @staticmethod
    def calculate_selected_split(amount: float, selected_members: List[Dict]) -> List[Dict]:
        """
        計算指定成員分帳
        amount: 總金額
        selected_members: 選定的成員列表 [{user_id, user_name}, ...]
        """
        if not selected_members:
            return []

        member_count = len(selected_members)
        per_person = amount / member_count

        splits = []
        for member in selected_members:
            split = ExpenseSplit(
                user_id=member['user_id'],
                user_name=member['user_name'],
                amount=per_person,
                is_paid=False
            )
            splits.append(split.to_dict())

        return splits

    @staticmethod
    def calculate_ratio_split(
        amount: float,
        members: Dict,
        ratios: List[int]
    ) -> List[Dict]:
        """
        計算比例分帳
        amount: 總金額
        members: 群組成員字典
        ratios: 比例列表 [2, 1, 1]
        """
        if not members or not ratios:
            return []

        member_list = list(members.items())

        if len(member_list) != len(ratios):
            # 如果比例數量與成員數量不符，返回空列表
            return []

        total_ratio = sum(ratios)
        splits = []

        for i, (user_id, member_data) in enumerate(member_list):
            ratio = ratios[i]
            split_amount = amount * (ratio / total_ratio)

            split = ExpenseSplit(
                user_id=user_id,
                user_name=member_data.get('display_name', '未知'),
                amount=split_amount,
                is_paid=False
            )
            splits.append(split.to_dict())

        return splits

    @staticmethod
    def create_expense_data(
        group_id: str,
        payer_id: str,
        payer_name: str,
        amount: float,
        description: str,
        split_type: str,
        splits: List[Dict],
        created_by: str
    ) -> Dict:
        """
        建立支出記錄資料
        """
        expense = Expense(
            group_id=group_id,
            payer_id=payer_id,
            payer_name=payer_name,
            amount=amount,
            description=description,
            split_type=split_type,
            splits=splits,
            created_by=created_by
        )

        return expense.to_dict()

    @staticmethod
    def validate_expense_data(expense_data: Dict) -> tuple[bool, Optional[str]]:
        """
        驗證支出記錄資料
        返回 (是否有效, 錯誤訊息)
        """
        # 檢查金額
        if expense_data.get('amount', 0) <= 0:
            return False, "金額必須大於 0"

        # 檢查描述
        if not expense_data.get('description'):
            return False, "項目描述不能為空"

        # 檢查付款人
        if not expense_data.get('payer_id'):
            return False, "付款人不能為空"

        # 檢查分帳明細
        if not expense_data.get('splits'):
            return False, "分帳明細不能為空"

        return True, None
