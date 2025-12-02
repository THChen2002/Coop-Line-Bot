from typing import Dict, List, Tuple
from models.settlement import PaymentPlan


class SettlementService:
    """結算與分帳演算法服務"""

    @staticmethod
    def calculate_balances(expenses: List[Dict]) -> Dict[str, Dict]:
        """
        計算每個成員的淨收支
        返回 {user_id: {user_name, net_amount}}
        net_amount 正數表示應收，負數表示應付
        """
        balances = {}

        for expense in expenses:
            payer_id = expense.get('payer_id')
            payer_name = expense.get('payer_name')
            amount = expense.get('amount', 0)
            splits = expense.get('splits', [])

            # 付款人收入
            if payer_id not in balances:
                balances[payer_id] = {
                    'user_name': payer_name,
                    'net_amount': 0
                }
            balances[payer_id]['net_amount'] += amount

            # 各成員支出
            for split in splits:
                user_id = split.get('user_id')
                user_name = split.get('user_name')
                split_amount = split.get('amount', 0)

                if user_id not in balances:
                    balances[user_id] = {
                        'user_name': user_name,
                        'net_amount': 0
                    }
                balances[user_id]['net_amount'] -= split_amount

        return balances

    @staticmethod
    def calculate_optimal_payments(balances: Dict[str, Dict]) -> List[Dict]:
        """
        使用貪婪演算法計算最優化還款方案（最少轉帳次數）
        """
        # 分離債權人和債務人
        creditors = []  # (user_id, user_name, amount)
        debtors = []    # (user_id, user_name, amount)

        for user_id, data in balances.items():
            net_amount = data.get('net_amount', 0)
            user_name = data.get('user_name', '未知')

            if net_amount > 0.01:  # 應收（使用小數容差）
                creditors.append([user_id, user_name, net_amount])
            elif net_amount < -0.01:  # 應付
                debtors.append([user_id, user_name, abs(net_amount)])

        payment_plans = []

        # 貪婪演算法：最大債務人向最大債權人還款
        while creditors and debtors:
            # 排序（從大到小）
            creditors.sort(key=lambda x: x[2], reverse=True)
            debtors.sort(key=lambda x: x[2], reverse=True)

            creditor = creditors[0]
            debtor = debtors[0]

            # 計算還款金額（取較小值）
            payment_amount = min(creditor[2], debtor[2])

            # 建立還款計畫
            plan = PaymentPlan(
                from_user_id=debtor[0],
                from_user_name=debtor[1],
                to_user_id=creditor[0],
                to_user_name=creditor[1],
                amount=payment_amount
            )
            payment_plans.append(plan.to_dict())

            # 更新金額
            creditor[2] -= payment_amount
            debtor[2] -= payment_amount

            # 移除已結清的
            if creditor[2] < 0.01:
                creditors.pop(0)
            if debtor[2] < 0.01:
                debtors.pop(0)

        return payment_plans

    @staticmethod
    def create_settlement_data(
        group_id: str,
        balances: Dict[str, Dict],
        payment_plans: List[Dict],
        settled_by: str,
        settled_by_name: str
    ) -> Dict:
        """
        建立結算記錄資料
        """
        return {
            'group_id': group_id,
            'settlement_data': payment_plans,
            'balance_summary': balances,
            'settled_by': settled_by,
            'settled_by_name': settled_by_name
        }

    @staticmethod
    def get_user_balance(user_id: str, expenses: List[Dict]) -> Tuple[float, float, float]:
        """
        計算特定使用者的收支
        返回 (已付款, 應分攤, 淨收支)
        """
        paid_total = 0
        owed_total = 0

        for expense in expenses:
            # 計算已付款
            if expense.get('payer_id') == user_id:
                paid_total += expense.get('amount', 0)

            # 計算應分攤
            for split in expense.get('splits', []):
                if split.get('user_id') == user_id:
                    owed_total += split.get('amount', 0)

        net = paid_total - owed_total
        return paid_total, owed_total, net
