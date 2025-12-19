from typing import Dict, List, Optional
from datetime import datetime
import random
import string


class Group:
    """群組資料模型"""

    def __init__(
        self,
        group_name: str,
        created_by: str,
        group_code: Optional[str] = None,
        members: Optional[List[str]] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None
    ):
        self.group_name = group_name
        self.created_by = created_by
        self.group_code = group_code or self._generate_group_code()
        self.members = members or [created_by]  # 建立者自動加入
        self.is_active = is_active
        self.created_at = created_at or datetime.now()

    @staticmethod
    def _generate_group_code() -> str:
        """生成 6 位數群組代碼"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            'group_name': self.group_name,
            'group_code': self.group_code,
            'created_by': self.created_by,
            'members': self.members,
            'is_active': self.is_active,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Group':
        """從字典建立群組物件"""
        return Group(
            group_name=data.get('group_name', ''),
            created_by=data.get('created_by', ''),
            group_code=data.get('group_code'),
            members=data.get('members', []),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at')
        )

    def add_member(self, user_id: str) -> bool:
        """新增成員"""
        if user_id not in self.members:
            self.members.append(user_id)
            return True
        return False

    def remove_member(self, user_id: str) -> bool:
        """移除成員"""
        if user_id in self.members:
            self.members.remove(user_id)
            return True
        return False

    def get_member_ids(self) -> List[str]:
        """取得所有成員 ID 列表"""
        return self.members
