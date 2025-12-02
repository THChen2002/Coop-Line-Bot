import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """應用程式配置"""

    # LINE Bot 配置
    CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')
    CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
    LIFF_ID = os.getenv('LIFF_ID', '')  # LIFF 應用程式 ID

    # Firebase 配置
    FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS', '')

    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # 日誌配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @staticmethod
    def validate():
        """驗證必要的配置是否存在"""
        required_vars = ['CHANNEL_SECRET', 'CHANNEL_ACCESS_TOKEN']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise ValueError(f"缺少必要的環境變數: {', '.join(missing_vars)}")

        return True
