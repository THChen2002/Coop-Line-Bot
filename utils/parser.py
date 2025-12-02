import re
from typing import Dict, List, Optional, Tuple


class CommandParser:
    """指令解析器"""

    @staticmethod
    def parse_expense_command(
        text: str,
        members: Dict,
        current_user_id: str,
        current_user_name: str
    ) -> Optional[Dict]:
        """
        解析記帳指令

        支援格式:
        1. 記帳 [金額] [項目] → 付款人 = 傳訊者，平均分帳
        2. 記帳 [金額] [項目] [付款人] → 付款人 = 指定成員，平均分帳

        Args:
            text: 使用者輸入的文字
            members: 群組成員字典 {user_id: {'display_name': str}}
            current_user_id: 傳訊者的 user_id
            current_user_name: 傳訊者的顯示名稱

        Returns:
            解析結果字典或 None
        """
        text = text.strip()

        # 格式 1: 記帳 [金額] [項目]（無付款人）
        pattern_no_payer = r'^記帳\s+(\d+(?:\.\d+)?)\s+(.+?)$'
        match = re.match(pattern_no_payer, text)

        if match:
            amount_str, description = match.groups()

            try:
                amount = float(amount_str)
            except ValueError:
                return None

            if amount <= 0:
                return None

            # 付款人預設為傳訊者
            return {
                'valid': True,
                'amount': amount,
                'description': description.strip(),
                'payer_id': current_user_id,
                'payer_name': current_user_name,
                'split_type': 'equal',
                'split_members': []  # 空列表表示所有成員
            }

        # 格式 2: 記帳 [金額] [項目] [付款人]
        pattern_with_payer = r'^記帳\s+(\d+(?:\.\d+)?)\s+(.+?)\s+(.+?)$'
        match = re.match(pattern_with_payer, text)

        if match:
            amount_str, description, payer_name = match.groups()

            try:
                amount = float(amount_str)
            except ValueError:
                return None

            if amount <= 0:
                return None

            # 尋找付款人 ID
            payer_id = CommandParser._find_user_id_by_name(
                payer_name.strip(),
                members
            )

            if not payer_id:
                return {
                    'error': f'找不到付款人：{payer_name}\n\n💡 提示：如果要自己付款，請使用「記帳 {amount_str} {description}」',
                    'valid': False
                }

            return {
                'valid': True,
                'amount': amount,
                'description': description.strip(),
                'payer_id': payer_id,
                'payer_name': payer_name.strip(),
                'split_type': 'equal',
                'split_members': []
            }

        return None

    @staticmethod
    def parse_delete_command(text: str) -> Optional[int]:
        """
        解析刪除指令
        格式：刪除 [編號]
        """
        pattern = r'^刪除\s+#?(\d+)$'
        match = re.match(pattern, text.strip())

        if match:
            return int(match.group(1))

        return None

    @staticmethod
    def is_query_command(text: str) -> bool:
        """檢查是否為查詢帳目指令"""
        return text.strip() in ['帳目', '查詢帳目']

    @staticmethod
    def is_my_expenses_command(text: str) -> bool:
        """檢查是否為我的帳目指令"""
        return text.strip() == '我的帳目'

    @staticmethod
    def is_statistics_command(text: str) -> bool:
        """檢查是否為統計指令"""
        return text.strip() == '統計'

    @staticmethod
    def is_settlement_command(text: str) -> bool:
        """檢查是否為結算指令"""
        return text.strip() == '結算'

    @staticmethod
    def is_clear_command(text: str) -> bool:
        """檢查是否為清帳指令"""
        return text.strip() == '清帳'

    @staticmethod
    def is_help_command(text: str) -> bool:
        """檢查是否為說明指令"""
        return text.strip() in ['說明', '幫助', 'help']

    @staticmethod
    def _find_user_id_by_name(name: str, members: list) -> Optional[str]:
        """根據名稱尋找使用者 ID

        Args:
            name: 要搜尋的名稱
            members: 成員列表 [{'id': user_id, 'name': display_name, 'picture_url': url}, ...]

        Returns:
            找到的 user_id，若找不到則返回 None
        """
        name = name.strip()
        for member in members:
            if member.get('name', '').strip() == name:
                return member.get('id')
        return None

    @staticmethod
    def get_help_message() -> str:
        """取得說明訊息"""
        return """📖 記帳與待辦機器人使用說明

【💰 記帳功能】

🎯 推薦：使用 LIFF 表單
• 點選「記帳」→「開啟表單」
• 支援指定成員、比例分帳、自訂金額等進階功能

✏️ 快速記帳指令：
• 記帳 [金額] [項目]
  → 自己付款，平均分給所有人
  範例：記帳 500 午餐

• 記帳 [金額] [項目] [付款人]
  → 指定付款人，平均分給所有人
  範例：記帳 500 午餐 小明

【📊 查詢功能】
• 查帳目 - 顯示所有未結算帳目
• 我的帳目 - 個人收支統計
• 統計 - 群組總支出統計

【💸 結算功能】
• 結算 - 計算最佳還款方案
• 清帳 - 標記所有帳目為已結算

【🗑️ 管理功能】
• 刪除 [編號] - 刪除指定帳目（僅限建立者）
  範例：刪除 3

【✅ 待辦清單】
• 點選「待辦」可新增、查看、管理待辦事項

---
💡 使用 Quick Reply 快速選單更方便！"""
