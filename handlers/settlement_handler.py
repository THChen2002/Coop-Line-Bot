from services.firebase_service import FirebaseService
from services.settlement_service import SettlementService
from utils.formatter import MessageFormatter


class SettlementHandler:
    """結算處理器"""

    def __init__(self, firebase_service):
        self.firebase_service: FirebaseService = firebase_service
        self.settlement_service: SettlementService = SettlementService()

    def handle_settlement(self, group_id: str):
        """處理結算請求"""
        try:
            # 取得未結算的支出
            expenses = self.firebase_service.get_group_expenses(
                group_id, is_settled=False
            )

            if not expenses:
                return {
                    'type': 'text',
                    'message': "目前沒有未結算的帳目",
                    'quick_reply': 'main_menu'
                }

            # 計算淨收支
            balances = self.settlement_service.calculate_balances(expenses)

            # 計算最優化還款方案
            payment_plans = self.settlement_service.calculate_optimal_payments(balances)

            # 格式化並返回結算結果（帶 Quick Reply）
            return {
                'type': 'flex',
                'message': MessageFormatter.format_settlement(balances, payment_plans),
                'quick_reply': 'settlement_menu'
            }

        except Exception as e:
            return MessageFormatter.format_error(f'結算失敗: {str(e)}')

    def handle_clear_expenses(
        self,
        group_id: str,
        user_id: str,
        user_name: str
    ) -> str:
        """處理清帳請求"""
        try:
            # 取得未結算的支出
            expenses = self.firebase_service.get_group_expenses(
                group_id, is_settled=False
            )

            if not expenses:
                return "目前沒有未結算的帳目"

            count = len(expenses)

            # 計算結算資料
            balances = self.settlement_service.calculate_balances(expenses)
            payment_plans = self.settlement_service.calculate_optimal_payments(balances)

            # 建立結算記錄
            settlement_data = self.settlement_service.create_settlement_data(
                group_id=group_id,
                balances=balances,
                payment_plans=payment_plans,
                settled_by=user_id,
                settled_by_name=user_name
            )

            # 儲存結算記錄
            self.firebase_service.create_settlement(settlement_data)

            # 將所有支出標記為已結算
            self.firebase_service.settle_expenses(group_id)

            return MessageFormatter.format_clear_success(count)

        except Exception as e:
            return MessageFormatter.format_error(f'清帳失敗: {str(e)}')
