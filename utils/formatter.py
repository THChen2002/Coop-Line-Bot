from typing import Dict, List, Union
from datetime import datetime
from linebot.v3.messaging import FlexMessage
from utils.flex_message import FlexMessageHelper


class MessageFormatter:
    """訊息格式化工具"""

    @staticmethod
    def format_expense_success(expense: Dict, splits: List[Dict]) -> Union[str, FlexMessage]:
        """格式化記帳成功訊息"""
        try:
            return FlexMessageHelper.create_expense_success(expense, splits)
        except Exception as e:
            # 降級回純文字
            split_type_names = {
                'equal': '平均分帳',
                'selected': '指定成員分帳',
                'ratio': '比例分帳'
            }

            message = f"✅ 記帳成功！\n\n項目：{expense['description']}\n金額：NT$ {int(expense['amount'])}\n付款人：{expense['payer_name']}\n分帳方式：{split_type_names.get(expense['split_type'], '平均分帳')}\n\n分帳明細："

            for split in splits:
                message += f"\n• {split['user_name']}：NT$ {int(split['amount'])}"

            message += f"\n\n編號：#{expense.get('expense_number', 0):03d}"
            return message

    @staticmethod
    def format_expense_list(expenses: List[Dict]) -> Union[str, FlexMessage]:
        """格式化帳目清單"""
        try:
            return FlexMessageHelper.create_expense_list(expenses)
        except Exception as e:
            # 降級回純文字
            if not expenses:
                return "📋 目前沒有未結算的帳目"

            message = "📋 群組帳目清單\n"
            total = 0

            for expense in expenses:
                expense_num = expense.get('expense_number', 0)
                desc = expense.get('description', '未命名')
                amount = expense.get('amount', 0)
                payer = expense.get('payer_name', '未知')

                message += f"\n#{expense_num:03d} - {desc} (NT$ {int(amount)})"
                message += f"\n付款：{payer}\n"
                total += amount

            message += f"\n總計：NT$ {int(total)}"
            return message

    @staticmethod
    def format_user_expenses(user_id: str, user_name: str, expenses: List[Dict]) -> FlexMessage:
        """格式化個人帳目"""
        paid_total = 0
        owed_total = 0

        for expense in expenses:
            if expense.get('payer_id') == user_id:
                paid_total += expense.get('amount', 0)

            for split in expense.get('splits', []):
                if split.get('user_id') == user_id:
                    owed_total += split.get('amount', 0)

        net = paid_total - owed_total

        # 準備統計資料
        stat_data = {
            "已付款": f"NT$ {int(paid_total)}",
            "應分攤": f"NT$ {int(owed_total)}"
        }

        if net > 0:
            stat_data[""] = "—————"
            stat_data["💚 淨收入"] = f"+NT$ {int(net)}"
            stat_data["提示"] = f"其他人欠你 NT$ {int(net)}"
        elif net < 0:
            stat_data[""] = "—————"
            stat_data["💸 淨支出"] = f"-NT$ {int(abs(net))}"
            stat_data["提示"] = f"你欠其他人 NT$ {int(abs(net))}"
        else:
            stat_data[""] = "—————"
            stat_data["✅ 淨收支"] = "NT$ 0"
            stat_data["提示"] = "已結清"

        return FlexMessageHelper.create_statistics_message(
            f"💰 {user_name} 的帳目",
            stat_data
        )

    @staticmethod
    def format_statistics(expenses: List[Dict], members: Dict) -> FlexMessage:
        """格式化統計資訊"""
        if not expenses:
            return FlexMessageHelper.create_info_message(
                "📊 群組統計",
                "目前沒有支出記錄"
            )

        total_amount = sum(expense.get('amount', 0) for expense in expenses)
        member_stats = {}

        # 計算每個成員的支出
        for expense in expenses:
            payer_id = expense.get('payer_id')
            payer_name = expense.get('payer_name', '未知')
            amount = expense.get('amount', 0)

            if payer_id not in member_stats:
                member_stats[payer_id] = {
                    'name': payer_name,
                    'paid': 0,
                    'count': 0
                }

            member_stats[payer_id]['paid'] += amount
            member_stats[payer_id]['count'] += 1

        # 準備統計資料
        stat_data = {
            "總支出": f"NT$ {int(total_amount)}",
            "總筆數": f"{len(expenses)} 筆",
            "": "—————"
        }

        # 依支出金額排序
        sorted_stats = sorted(
            member_stats.items(),
            key=lambda x: x[1]['paid'],
            reverse=True
        )

        for i, (_, stats) in enumerate(sorted_stats):
            percentage = (stats['paid'] / total_amount * 100) if total_amount > 0 else 0
            stat_data[f"👤 {stats['name']}"] = f"NT$ {int(stats['paid'])} ({percentage:.1f}%)"
            # 使用隱藏後綴確保 key 唯一，但顯示時會被 strip() 去除
            unique_suffix = " " * (i + 1)
            stat_data[f"  筆數{unique_suffix}"] = f"{stats['count']} 筆"

        return FlexMessageHelper.create_statistics_message(
            "📊 群組統計",
            stat_data
        )

    @staticmethod
    def format_settlement(balance_summary: Dict, payment_plans: List[Dict]) -> Union[str, FlexMessage]:
        """格式化結算結果"""
        try:
            return FlexMessageHelper.create_settlement_result(balance_summary, payment_plans)
        except Exception as e:
            # 降級回純文字
            message = "💰 結算結果\n"

            # 分類應收和應付
            creditors = []
            debtors = []

            for user_id, data in balance_summary.items():
                net_amount = data.get('net_amount', 0)
                user_name = data.get('user_name', '未知')

                if net_amount > 0:
                    creditors.append((user_name, net_amount))
                elif net_amount < 0:
                    debtors.append((user_name, abs(net_amount)))

            if creditors:
                message += "\n應收：\n"
                for name, amount in sorted(creditors, key=lambda x: x[1], reverse=True):
                    message += f"• {name}：+NT$ {int(amount)}\n"

            if debtors:
                message += "\n應付：\n"
                for name, amount in sorted(debtors, key=lambda x: x[1], reverse=True):
                    message += f"• {name}：-NT$ {int(amount)}\n"

            if not creditors and not debtors:
                message += "\n所有帳目已結清！✨"
                return message

            if payment_plans:
                message += "\n建議還款方式：\n"
                for i, plan in enumerate(payment_plans, 1):
                    from_name = plan.get('from_user_name', '未知')
                    to_name = plan.get('to_user_name', '未知')
                    amount = plan.get('amount', 0)
                    message += f"{i}. {from_name} → {to_name} NT$ {int(amount)}\n"

                message += f"\n共需 {len(payment_plans)} 筆轉帳"

            return message

    @staticmethod
    def format_delete_success(expense_number: int) -> FlexMessage:
        """格式化刪除成功訊息"""
        return FlexMessageHelper.create_success_message(
            f"已刪除帳目 #{expense_number:03d}"
        )

    @staticmethod
    def format_clear_success(count: int) -> FlexMessage:
        """格式化清帳成功訊息"""
        return FlexMessageHelper.create_success_message(
            f"已清除 {count} 筆帳目，標記為已結算"
        )

    @staticmethod
    def format_error(error_message: str) -> str:
        """格式化錯誤訊息"""
        return f"❌ {error_message}"
