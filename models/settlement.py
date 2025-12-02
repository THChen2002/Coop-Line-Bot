from typing import Dict, List


class Settlement:
    """結算記錄資料模型"""

    def __init__(
        self,
        group_id: str,
        settlement_data: List[Dict],
        balance_summary: Dict,
        settled_by: str,
        settled_by_name: str,
        settlement_id: str = None
    ):
        self.id = settlement_id
        self.group_id = group_id
        self.settlement_data = settlement_data
        self.balance_summary = balance_summary
        self.settled_by = settled_by
        self.settled_by_name = settled_by_name

    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        data = {
            'group_id': self.group_id,
            'settlement_data': self.settlement_data,
            'balance_summary': self.balance_summary,
            'settled_by': self.settled_by,
            'settled_by_name': self.settled_by_name
        }
        if self.id:
            data['id'] = self.id
        return data

    @staticmethod
    def from_dict(data: Dict) -> 'Settlement':
        """從字典建立結算物件"""
        return Settlement(
            settlement_id=data.get('id'),
            group_id=data['group_id'],
            settlement_data=data['settlement_data'],
            balance_summary=data['balance_summary'],
            settled_by=data['settled_by'],
            settled_by_name=data['settled_by_name']
        )


class PaymentPlan:
    """還款計畫資料模型"""

    def __init__(
        self,
        from_user_id: str,
        from_user_name: str,
        to_user_id: str,
        to_user_name: str,
        amount: float
    ):
        self.from_user_id = from_user_id
        self.from_user_name = from_user_name
        self.to_user_id = to_user_id
        self.to_user_name = to_user_name
        self.amount = amount

    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            'from_user_id': self.from_user_id,
            'from_user_name': self.from_user_name,
            'to_user_id': self.to_user_id,
            'to_user_name': self.to_user_name,
            'amount': self.amount
        }

    @staticmethod
    def from_dict(data: Dict) -> 'PaymentPlan':
        """從字典建立還款計畫物件"""
        return PaymentPlan(
            from_user_id=data['from_user_id'],
            from_user_name=data['from_user_name'],
            to_user_id=data['to_user_id'],
            to_user_name=data['to_user_name'],
            amount=data['amount']
        )
