from typing import Dict


class User:
    """使用者資料模型"""

    def __init__(self, line_user_id: str, display_name: str):
        self.line_user_id = line_user_id
        self.display_name = display_name

    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            'line_user_id': self.line_user_id,
            'display_name': self.display_name
        }

    @staticmethod
    def from_dict(data: Dict) -> 'User':
        """從字典建立使用者物件"""
        return User(
            line_user_id=data['line_user_id'],
            display_name=data['display_name']
        )
