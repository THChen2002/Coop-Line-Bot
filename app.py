# -*- coding: utf-8 -*-
"""Main Flask application - Modular structure with Blueprints"""

from flask import Flask
import logging

from config import Config

# 初始化 Flask
app = Flask(__name__)

# 設定日誌
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 驗證配置
try:
    Config.validate()
    logger.info("配置驗證成功")
except ValueError as e:
    logger.error(f"配置驗證失敗: {e}")
    raise


# ===== 註冊 Blueprints =====

from blueprints.linebot_app import linebot_bp
from blueprints.liff_app import liff_bp
from blueprints.api_app import api_bp

app.register_blueprint(linebot_bp)
app.register_blueprint(liff_bp)
app.register_blueprint(api_bp)


@app.route("/", methods=['GET'])
def index():
    return "LINE Bot 記帳系統運行中", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
