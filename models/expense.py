from typing import Dict, List


class Expense:
    """支出記錄資料模型"""

    def __init__(
        self,
        group_id: str,
        payer_id: str,
        payer_name: str,
        amount: float,
        description: str,
        split_type: str,
        splits: List[Dict],
        created_by: str,
        expense_number: int = 0,
        expense_id: str = None,
        is_settled: bool = False
    ):
        self.id = expense_id
        self.group_id = group_id
        self.payer_id = payer_id
        self.payer_name = payer_name
        self.amount = amount
        self.description = description
        self.split_type = split_type
        self.splits = splits
        self.created_by = created_by
        self.expense_number = expense_number
        self.is_settled = is_settled

    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        data = {
            'group_id': self.group_id,
            'payer_id': self.payer_id,
            'payer_name': self.payer_name,
            'amount': self.amount,
            'description': self.description,
            'split_type': self.split_type,
            'splits': self.splits,
            'created_by': self.created_by,
            'expense_number': self.expense_number,
            'is_settled': self.is_settled
        }
        if self.id:
            data['id'] = self.id
        return data

    @staticmethod
    def from_dict(data: Dict) -> 'Expense':
        """從字典建立支出物件"""
        return Expense(
            expense_id=data.get('id'),
            group_id=data['group_id'],
            payer_id=data['payer_id'],
            payer_name=data['payer_name'],
            amount=data['amount'],
            description=data['description'],
            split_type=data['split_type'],
            splits=data['splits'],
            created_by=data['created_by'],
            expense_number=data.get('expense_number', 0),
            is_settled=data.get('is_settled', False)
        )


class ExpenseSplit:
    """分帳明細資料模型"""

    def __init__(self, user_id: str, user_name: str, amount: float, is_paid: bool = False):
        self.user_id = user_id
        self.user_name = user_name
        self.amount = amount
        self.is_paid = is_paid

    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'amount': self.amount,
            'is_paid': self.is_paid
        }

    @staticmethod
    def from_dict(data: Dict) -> 'ExpenseSplit':
        """從字典建立分帳明細物件"""
        return ExpenseSplit(
            user_id=data['user_id'],
            user_name=data['user_name'],
            amount=data['amount'],
            is_paid=data.get('is_paid', False)
        )
