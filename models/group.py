from typing import Dict


class Group:
    """群組資料模型"""

    def __init__(self, line_group_id: str, group_name: str, members: Dict = None):
        self.line_group_id = line_group_id
        self.group_name = group_name
        self.members = members or {}

    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            'line_group_id': self.line_group_id,
            'group_name': self.group_name,
            'members': self.members
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Group':
        """從字典建立群組物件"""
        return Group(
            line_group_id=data['line_group_id'],
            group_name=data.get('group_name', ''),
            members=data.get('members', {})
        )

    def get_member_names(self) -> list:
        """取得所有成員名稱列表"""
        return [member['display_name'] for member in self.members.values()]

    def get_member_ids(self) -> list:
        """取得所有成員 ID 列表"""
        return list(self.members.keys())
