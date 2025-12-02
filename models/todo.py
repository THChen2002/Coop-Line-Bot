# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Dict, Optional


class Todo:
    """待辦事項模型"""

    def __init__(self,
                 id: str,
                 group_id: str,
                 title: str,
                 description: str = '',
                 category: str = '一般',
                 assignee_id: str = '',
                 assignee_name: str = '',
                 status: str = 'pending',
                 priority: str = 'medium',
                 due_date: Optional[str] = None,
                 created_by: str = '',
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 completed_at: Optional[datetime] = None):
        self.id = id
        self.group_id = group_id
        self.title = title
        self.description = description
        self.category = category
        self.assignee_id = assignee_id
        self.assignee_name = assignee_name
        self.status = status  # pending, in_progress, completed, cancelled
        self.priority = priority  # low, medium, high
        self.due_date = due_date
        self.created_by = created_by
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.completed_at = completed_at

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            'id': self.id,
            'group_id': self.group_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'assignee_id': self.assignee_id,
            'assignee_name': self.assignee_name,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Todo':
        """從字典建立"""
        # 處理日期時間字串
        created_at = None
        updated_at = None
        completed_at = None

        if 'created_at' in data and data['created_at']:
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'])
            elif hasattr(data['created_at'], 'to_pydatetime'):
                created_at = data['created_at'].to_pydatetime()
            else:
                created_at = data['created_at']

        if 'updated_at' in data and data['updated_at']:
            if isinstance(data['updated_at'], str):
                updated_at = datetime.fromisoformat(data['updated_at'])
            elif hasattr(data['updated_at'], 'to_pydatetime'):
                updated_at = data['updated_at'].to_pydatetime()
            else:
                updated_at = data['updated_at']

        if 'completed_at' in data and data['completed_at']:
            if isinstance(data['completed_at'], str):
                completed_at = datetime.fromisoformat(data['completed_at'])
            elif hasattr(data['completed_at'], 'to_pydatetime'):
                completed_at = data['completed_at'].to_pydatetime()
            else:
                completed_at = data['completed_at']

        return cls(
            id=data.get('id', ''),
            group_id=data.get('group_id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            category=data.get('category', '一般'),
            assignee_id=data.get('assignee_id', ''),
            assignee_name=data.get('assignee_name', ''),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            due_date=data.get('due_date'),
            created_by=data.get('created_by', ''),
            created_at=created_at,
            updated_at=updated_at,
            completed_at=completed_at
        )
