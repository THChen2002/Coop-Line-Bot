# LINE Bot 多人記帳分帳系統

一個基於 Flask 和 Firebase 的 LINE Bot,提供多人共同記帳與自動分帳功能。Bot 以一對一聊天模式運作,使用者可建立群組進行記帳與待辦管理。

## 功能特色

### 群組管理
- 👥 **建立群組**：透過 LIFF 建立分帳群組
- 🔗 **邀請碼加入**：使用 6 位代碼邀請成員加入
- 📱 **分享功能**：一鍵分享群組邀請連結

### 記帳功能
- 🎯 **LIFF 互動表單**：視覺化記帳介面，支援平均分帳、自訂金額、指定成員
- ✅ **多人記帳**：群組內多人共同記帳
- ✅ **智慧結算**：自動計算最優化還款方案（最少轉帳次數）
- ✅ **帳目查詢**：查看群組帳目、篩選未結算/已結算帳目

### 待辦清單功能
- 📝 **LIFF 表單管理**：透過群組詳細頁進入待辦管理
- ✅ **新增/編輯待辦**：填寫標題、描述、負責人、截止日期
- 👥 **負責人分配**：從群組成員中指定負責人
- 📁 **類別管理**：工作、學習、生活、購物、其他
- 📅 **到期日設定**：設定待辦事項截止日期
- 🎯 **優先度管理**：低、中、高三個優先等級
- ✅ **狀態追蹤**：待處理、進行中、已完成、已取消

### 共同特色
- ✅ **Flex Message**：精美的卡片式訊息顯示
- ✅ **Firebase 雲端儲存**：資料安全可靠，支援多裝置同步
- ✅ **LINE 選單**：透過 Rich Menu 快速存取功能

## 技術架構

- **後端框架**：Flask
- **LINE Bot SDK**：line-bot-sdk 3.21.0
- **LIFF**：LINE Front-end Framework
- **資料庫**：Firebase Firestore
- **互動元素**：Rich Menu、Flex Message
- **Python 版本**：3.8+

## 專案結構

```
Coop-Line-Bot/
├── app.py                      # Flask 主程式
├── config.py                   # 設定檔
├── requirements.txt            # 套件依賴
├── .env                        # 環境變數
├── blueprints/                 # Flask Blueprints
│   ├── linebot_app.py          # LINE Webhook 處理
│   ├── liff_app.py             # LIFF 頁面路由
│   └── api_app.py              # RESTful API
├── templates/                  # 模板
│   ├── base.html               # 基礎模板（含 LIFF SDK）
│   └── liff/                   # LIFF 頁面
│       ├── groups_list.html    # 群組列表
│       ├── group_create.html   # 建立群組
│       ├── group_join.html     # 加入群組（邀請碼）
│       ├── group_detail.html   # 群組詳細頁（帳目列表）
│       ├── expense_form.html   # 記帳表單
│       ├── settlement.html     # 結算頁面
│       ├── todo_form.html      # 待辦事項表單
│       └── liff.html           # LIFF 動態路由頁面
├── static/                     # 靜態資源
│   ├── css/
│   │   ├── base.css            # 基礎樣式與共用組件
│   │   ├── groups_list.css     # 群組列表樣式
│   │   ├── group_form.css      # 群組表單樣式
│   │   ├── group_detail.css    # 群組詳細頁樣式
│   │   ├── expense_form.css    # 記帳表單樣式
│   │   ├── settlement.css      # 結算頁面樣式
│   │   └── todo_form.css       # 待辦表單樣式
│   └── js/
│       ├── base.js             # 基礎工具函數（LIFF、API、Loading）
│       ├── groups_list.js      # 群組列表邏輯
│       ├── group_create.js     # 建立群組邏輯
│       ├── group_join.js       # 加入群組邏輯
│       ├── group_utils.js      # 群組共用工具
│       ├── group_detail.js     # 群組詳細頁邏輯
│       ├── expense_form.js     # 記帳表單邏輯
│       ├── settlement.js       # 結算頁面邏輯
│       └── todo_form.js        # 待辦表單邏輯
├── models/                     # 資料模型
│   ├── user.py                 # 使用者模型
│   ├── group.py                # 群組模型（含邀請碼生成）
│   ├── expense.py              # 支出模型
│   ├── settlement.py           # 結算模型
│   └── todo.py                 # 待辦事項模型
├── services/                   # 服務層
│   ├── firebase_service.py     # Firebase Firestore 操作（Singleton）
│   ├── expense_service.py      # 支出業務邏輯
│   ├── settlement_service.py   # 結算計算（最少交易算法）
│   └── todo_service.py         # 待辦事項業務邏輯
├── handlers/                   # 處理器
│   └── message_handler.py      # LINE 訊息處理（主選單）
└── utils/                      # 工具
    ├── liff_enum.py            # LIFF 尺寸枚舉
    ├── formatter.py            # 格式化工具
    └── flex_message.py         # Flex Message 訊息卡片
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

### 開始使用

1. 加入 LINE Bot 為好友
2. 透過下方選單點擊「我的群組」開啟群組列表
3. 選擇「建立新群組」或使用邀請碼「加入群組」

### 群組管理

**建立群組**
1. 點選「建立新群組」
2. 輸入群組名稱
3. 系統自動生成 6 位邀請碼
4. 分享邀請連結給成員

**加入群組**
1. 點選「加入群組」
2. 輸入 6 位邀請碼
3. 成功加入群組

### 記帳操作

**新增支出（使用 LIFF 表單）**
1. 進入群組詳細頁面
2. 點擊「新增支出」
3. 填寫以下資訊：
   - 項目名稱（例如：午餐、計程車）
   - 總金額（僅整數）
   - 選擇付款人
   - 選擇分帳方式：
     - **平均分帳**：自動平均分配給選中的成員
     - **自訂金額**：可為每個人設定不同金額
     - **指定成員**：只選擇特定成員分帳
4. 勾選要分帳的成員
5. 若選擇自訂金額，可輸入每人應付金額
6. 系統會自動驗證總金額是否相符
7. 送出後自動發送 Flex Message 到 LINE 聊天室

**查詢帳目**
- 群組詳細頁面提供三個篩選標籤：全部、未結算、已結算
- 點擊支出項目可查看詳細資訊或刪除

**結算**
1. 進入群組詳細頁面
2. 點擊「結算」按鈕
3. 系統自動計算最優化還款方案
4. 確認後將所有帳目標記為已結算

### 待辦管理

**新增待辦**
1. 進入群組詳細頁面
2. 點擊右上角「待辦」按鈕
3. 在待辦表單中填寫：
   - 標題（必填）
   - 描述（選填）
   - 負責人（從群組成員中選擇）
   - 類別（工作、學習、生活、購物、其他）
   - 優先度（低、中、高）
   - 截止日期（選填）
4. 點擊「新增待辦」送出

**編輯/刪除待辦**
- 在待辦表單頁面可查看所有待辦事項
- 點擊待辦項目進入編輯模式
- 可更新狀態：待處理 → 進行中 → 已完成
- 也可選擇刪除待辦事項

### 文字指令

- `說明` 或 `主選單` - 顯示歡迎訊息
- 其他功能請透過 LINE 選單開啟 LIFF 頁面操作

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
  group_name: string,
  group_code: string,        // 6 位邀請碼
  created_by: string,         // 建立者 user_id
  created_at: timestamp,
  is_active: boolean,
  members: [user_id, ...]     // 成員 ID 陣列
}
```

### chats（一對一聊天記錄）
```javascript
{
  line_user_id: string,
  user_name: string,
  created_at: timestamp,
  updated_at: timestamp,
  is_active: boolean
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

### todos（待辦事項集合）
```javascript
{
  group_id: string,
  title: string,
  description: string,
  category: string,          // 工作、學習、生活、購物、其他
  assignee_id: string,
  assignee_name: string,
  status: string,            // pending、in_progress、completed、cancelled
  priority: string,          // low、medium、high
  due_date: timestamp,       // 截止日期（選填）
  created_at: timestamp,
  updated_at: timestamp,
  completed_at: timestamp    // 完成時間（選填）
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

### LIFF 頁面無法開啟
- 確認 LIFF_ID 設定正確
- 確認 Endpoint URL 已正確設定
- 檢查是否已啟用 HTTPS

### 群組功能問題
- 確認使用者已加入 LINE Bot 好友
- 確認已透過 LIFF 頁面建立或加入群組

## 授權

MIT License

## 聯絡方式

如有問題或建議，歡迎開 Issue 討論。

---
