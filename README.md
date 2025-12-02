# LINE Bot 多人記帳分帳系統

一個基於 Flask 和 Firebase 的 LINE Bot，提供多人共同記帳與自動分帳功能。

## 功能特色

### 記帳功能
- 🎯 **LIFF 互動表單**：視覺化記帳介面，支援平均分帳、自訂金額
- ✅ **多人記帳**：支援群組多人共同記帳
- ✅ **快速記帳**：文字指令快速記帳，平均分配給所有成員
- ✅ **智慧結算**：自動計算最優化還款方案（最少轉帳次數）
- ✅ **帳目查詢**：查看群組帳目、個人收支統計

### 待辦清單功能
- 📝 **LIFF 表單管理**：新增、編輯、刪除待辦事項
- 👥 **負責人分配**：指定群組成員負責
- 📁 **類別管理**：支援多種類別分類（工作、學習、生活等）
- 📅 **到期日提醒**：設定待辦事項截止日期
- 🎯 **優先度設定**：低、中、高三個優先等級
- ✅ **狀態追蹤**：待處理、進行中、已完成、已取消
- 📊 **統計報表**：按類別、負責人統計待辦事項

### 共同特色
- ✅ **Flex Message**：精美的卡片式訊息顯示
- ✅ **Quick Reply**：快速回覆按鈕，操作更便捷
- ✅ **Firebase 雲端儲存**：資料安全可靠，支援多裝置同步

## 技術架構

- **後端框架**：Flask
- **LINE Bot SDK**：line-bot-sdk 3.21.0
- **LIFF**：LINE Front-end Framework
- **資料庫**：Firebase Firestore
- **互動元素**：Quick Reply、Flex Message
- **Python 版本**：3.8+

## 專案結構

```
Bill/
├── app.py                      # Flask 主程式（含 API）
├── config.py                   # 設定檔
├── requirements.txt            # 套件依賴
├── .env                        # 環境變數
├── templates/                  # 模板
│   ├── base.html               # 基礎模板
│   └── liff/                   # LIFF 頁面
│       ├── liff.html           # LIFF 載入頁
│       ├── expense_form.html   # 記帳表單
│       └── todo_list.html      # 待辦清單
├── static/                     # 靜態資源
│   ├── css/
│   │   ├── base.css            # 基礎樣式
│   │   ├── expense_form.css    # 記帳表單樣式
│   │   └── todo_list.css       # 待辦清單樣式
│   └── js/
│       ├── base.js             # 基礎工具函數
│       ├── expense_form.js     # 記帳表單邏輯
│       └── todo_list.js        # 待辦清單邏輯
├── models/                     # 資料模型
│   ├── user.py
│   ├── group.py
│   ├── expense.py
│   ├── settlement.py
│   └── todo.py
├── services/                   # 服務層
│   ├── firebase_service.py
│   ├── expense_service.py
│   ├── settlement_service.py
│   └── todo_service.py
├── handlers/                   # 處理器
│   ├── message_handler.py
│   ├── expense_handler.py
│   ├── settlement_handler.py
│   └── todo_handler.py
└── utils/                      # 工具
    ├── parser.py
    ├── formatter.py
    ├── quick_reply.py          # Quick Reply
    └── flex_message.py         # Flex Message
```

## 快速開始

### 1. 環境準備

確保已安裝 Python 3.8 或以上版本：

```bash
python --version
```

### 2. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 3. 設定 LINE Bot

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立 Messaging API Channel
3. 取得 Channel Secret 和 Channel Access Token
4. 將憑證填入 `.env` 檔案

### 4. 設定 LIFF（支援多種尺寸）

1. 在 LINE Developers Console 的 Messaging API 頻道中
2. 點選「LIFF」分頁，建立 LIFF 應用程式（可建立 3 個不同尺寸）：

| 尺寸 | Endpoint URL | 用途 |
|------|-------------|------|
| Full | `https://your-domain.com/liff/full` | 全螢幕模式 |
| Tall | `https://your-domain.com/liff/tall` | 高版面模式 |
| Compact | `https://your-domain.com/liff/compact` | 精簡模式 |

3. 記帳表單 Endpoint：`https://your-domain.com/liff/full/expense`
4. 複製各尺寸的 LIFF ID 並加入 `.env`

### 5. 設定 Firebase

1. 前往 [Firebase Console](https://console.firebase.google.com/)
2. 建立新專案
3. 啟用 Firestore Database
4. 在「專案設定」→「服務帳戶」下載服務帳戶金鑰（JSON 格式）
5. 將整個 JSON 內容複製到 `.env` 的 `FIREBASE_CREDENTIALS`

### 6. 設定環境變數

編輯 `.env` 檔案：

```env
CHANNEL_SECRET=你的Channel_Secret
CHANNEL_ACCESS_TOKEN=你的Channel_Access_Token

# LIFF 設定（至少設定一個）
LIFF_ID_FULL=你的LIFF_ID_FULL
LIFF_ID_TALL=你的LIFF_ID_TALL
LIFF_ID_COMPACT=你的LIFF_ID_COMPACT

# Firebase 憑證（JSON 字串）
FIREBASE_CREDENTIALS={"type":"service_account","project_id":"your-project",...}
```

### 7. 執行應用程式

```bash
python app.py
```

應用程式會在 `http://localhost:5000` 啟動。

### 8. 設定 Webhook

開發環境可使用 [ngrok](https://ngrok.com/) 建立公開 URL：

```bash
ngrok http 5000
```

將 ngrok 提供的 HTTPS URL 加上 `/callback` 設定到 LINE Developers Console 的 Webhook URL。

例如：`https://abc123.ngrok.io/callback`

## 使用說明

### 記帳相關

**🎯 推薦：使用 LIFF 表單**

1. 在 LINE 群組中輸入 `開啟記帳表單` 或 `記帳表單`
2. 會開啟視覺化的記帳介面
3. 填寫以下資訊：
   - 項目名稱（例如：午餐、計程車）
   - 總金額
   - 選擇付款人
   - 選擇分帳方式：
     - **平均分帳**：自動平均分配給所有成員
     - **自訂金額**：可為每個人設定不同金額
4. 勾選要分帳的成員
5. 若選擇自訂金額，可輸入每人應付金額
6. 系統會自動驗證總金額是否相符
7. 送出後關閉視窗即完成

**📝 快速記帳指令**

```
記帳 500 午餐
```
自己付款，平均分給所有群組成員

```
記帳 500 午餐 小明
```
小明付款，平均分給所有群組成員

### 查詢相關

- `帳目` - 顯示所有未結算帳目
- `我的帳目` - 顯示個人收支統計
- `統計` - 顯示群組總支出統計

### 結算相關

- `結算` - 計算應收應付金額及最佳還款方案
- `清帳` - 將所有帳目標記為已結算

### 其他

- `刪除 3` - 刪除編號 3 的帳目（僅限建立者）
- `說明` - 顯示使用說明

## Firebase Firestore 資料結構

### users（使用者集合）
```javascript
{
  line_user_id: string,
  display_name: string,
  created_at: timestamp,
  updated_at: timestamp
}
```

### groups（群組集合）
```javascript
{
  line_group_id: string,
  group_name: string,
  created_at: timestamp,
  is_active: boolean,
  members: {
    [user_id]: {
      display_name: string,
      joined_at: timestamp
    }
  }
}
```

### expenses（支出記錄集合）
```javascript
{
  group_id: string,
  payer_id: string,
  payer_name: string,
  amount: number,
  description: string,
  split_type: string,
  splits: [{
    user_id: string,
    user_name: string,
    amount: number,
    is_paid: boolean
  }],
  created_by: string,
  created_at: timestamp,
  is_settled: boolean,
  expense_number: number
}
```

### settlements（結算記錄集合）
```javascript
{
  group_id: string,
  settlement_data: [{
    from_user_id: string,
    from_user_name: string,
    to_user_id: string,
    to_user_name: string,
    amount: number
  }],
  balance_summary: {
    [user_id]: {
      user_name: string,
      net_amount: number
    }
  },
  settled_at: timestamp,
  settled_by: string,
  settled_by_name: string
}
```

## 部署

### 使用 Heroku

1. 建立 `Procfile`：
```
web: gunicorn app:app
```

2. 部署到 Heroku：
```bash
heroku create your-app-name
git push heroku main
```

3. 設定環境變數：
```bash
heroku config:set CHANNEL_SECRET=你的值
heroku config:set CHANNEL_ACCESS_TOKEN=你的值
```

4. 上傳 Firebase 憑證（建議使用環境變數）

### 使用 Google Cloud Run

適合搭配 Firebase 使用，詳見 [Google Cloud Run 文件](https://cloud.google.com/run/docs)。

## 開發注意事項

1. **環境變數保護**
   - `.env` 和 `firebase_config.json` 不應提交到版本控制
   - 已在 `.gitignore` 中排除

2. **Firebase 免費方案限制**
   - 每日讀取：50,000 次
   - 每日寫入：20,000 次
   - 儲存空間：1 GB

3. **安全性**
   - Webhook 會驗證 LINE Platform 的簽章
   - Firestore 設定為只允許服務帳戶存取

## 故障排除

### Firebase 初始化失敗
- 確認 `firebase_config.json` 路徑正確
- 確認 Firebase 專案已啟用 Firestore

### LINE Bot 無回應
- 確認 Webhook URL 設定正確（必須是 HTTPS）
- 檢查 Channel Secret 和 Channel Access Token
- 查看應用程式日誌

### 找不到使用者
- 確認指令中的名稱與 LINE 顯示名稱完全一致
- 使用者必須先在群組中發言過一次

## 授權

MIT License

## 聯絡方式

如有問題或建議，歡迎開 Issue 討論。

---

**版本**：1.0.0
**最後更新**：2025-11-29
