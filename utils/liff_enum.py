# -*- coding: utf-8 -*-
from enum import Enum
import os


class LIFF(Enum):
    """LIFF 應用程式尺寸枚舉"""
    FULL = os.getenv('LIFF_ID_FULL', '')
    TALL = os.getenv('LIFF_ID_TALL', '')
    COMPACT = os.getenv('LIFF_ID_COMPACT', '')

    @classmethod
    def get_liff_id(cls, size: str, default_to_tall: bool = True) -> str:
        """
        根據尺寸參數取得 LIFF ID
        Args:
            size (str): LIFF 尺寸 (FULL, TALL, COMPACT)
            default_to_tall (bool): 當無效時是否預設返回 TALL 尺寸
        Returns:
            str: LIFF ID
        """
        size_upper = size.upper()

        if size_upper in [liff_type.name for liff_type in cls]:
            liff_id = getattr(cls, size_upper).value
            if liff_id:
                return liff_id

        if default_to_tall and cls.TALL.value:
            return cls.TALL.value

        # 如果都沒有設定，返回空字串
        return ''
