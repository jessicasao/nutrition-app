# 🥑 WholeFood Dairy

> 一個專注計算「原型食物」營養的 Web APP

🔗 **線上試用**：https://nutrition-food-app.streamlit.app/

📂 **GitHub**：https://github.com/jessicasao/nutrition-app

---

## 📌 專案簡介

**一句話說明**：記錄每天吃的原型食物，自動計算營養夠不夠。

**為什麼做這個？**
市面上飲食 APP 大多計算「加工食品」的熱量，但我找不到一個簡單工具可以計算「原型食物」的營養。與其等，不如自己做。

**解決什麼問題？**
- 不知道每天吃的蛋白質、鐵、維生素C夠不夠？
- 不知道自己的每日營養目標是多少？
- 找不到專注「原型食物」的 APP

---

## 🛠 技術架構

| 層級 | 技術 | 說明 |
|------|------|------|
| 前端/框架 | **Streamlit** | Python 網頁框架，快速開發 |
| 資料庫 | **Supabase** | 雲端 PostgreSQL，免費方案 |
| API 串接 | **USDA FoodData Central** | 美國農業部官方營養資料 |
| 部署 | **Streamlit Cloud** | 連接 GitHub，自動部署 |
| 版本控制 | **Git + GitHub** | 程式碼管理 |


**流程說明**：
1. 使用者打開瀏覽器，連到 Streamlit Cloud
2. APP 從 Supabase 讀取使用者資料和飲食記錄
3. 搜尋新食物時，從 USDA API 獲取營養資料
4. 記錄飲食後，資料寫回 Supabase

---

## 📁 資料庫設計

### 5 張表格

| 表格 | 用途 | 關鍵欄位 |
|------|------|---------|
| `user_profile` | 使用者資料 | user_name, password, gender, age, height, weight |
| `foods` | 食物資料庫 | food_name, category, 營養素欄位, created_by |
| `meal_logs` | 飲食記錄 | user_name, log_date, food_id, grams |
| `hidden_foods` | 隱藏食物 | user_name, food_id |
| `feedbacks` | 留言回饋 | user_name, title, content, is_read |

### 關聯說明
- `user_profile` 與 `meal_logs`：一對多（一個使用者有多筆記錄）
- `foods` 與 `meal_logs`：一對多（一個食物可被多次記錄）
- `hidden_foods` 記錄每個使用者隱藏了哪些食物

---

## 🔧 核心功能

| 功能 | 說明 |
|------|------|
| 🔐 使用者系統 | 註冊 / 登入 / 個人資料設定 |
| 📝 飲食記錄 | 食物/飲品/點心分類，支援單位換算（克、個、碗、杯） |
| 📊 營養計算 | 蛋白質、鐵、維生素C、膳食纖維、鈣、碳水化合物 |
| 🎯 個人目標 | 根據身高體重自動計算每日營養目標 |
| 🙈 食物管理 | 隱藏不吃的食物、從 USDA 搜尋新增 |
| 💬 回饋系統 | 留言板，管理員可標記已讀 |

---

## 📐 營養計算公式

| 營養素 | 計算方式 | 來源 |
|--------|---------|------|
| 熱量 (TDEE) | Mifflin-St Jeor + 活動係數 | 營養學通用公式 |
| 蛋白質 | 體重 × 1.1g | 一般成人建議 |
| 鐵 | 男 10mg / 女 15mg | 台灣衛福部 DRI |
| 維生素C | 100mg | 台灣衛福部 DRI |
| 膳食纖維 | 25g | FDA 每日參考值 |
| 鈣 | 1000mg | FDA 每日參考值 |
| 碳水化合物 | 250g | 一般建議值 |


---

## 🚀 開發流程

### 階段 1：需求分析
- 發現市場缺口：沒有好用的「原型食物」營養計算器
- 定義 MVP 功能：記錄飲食、計算營養、個人目標

### 階段 2：技術選型
- 選擇 Streamlit（只會 Python，不用學前端）
- 選擇 Supabase（免費雲端資料庫，資料不消失）
- 選擇 USDA API（官方免費營養資料）

### 階段 3：資料庫設計
- 設計 5 張表格 + 建立關聯
- 考慮擴充性（created_by 區分系統/使用者食物）

### 階段 4：功能開發
- 使用者系統（註冊/登入/個人資料）
- 飲食記錄 CRUD
- 營養計算邏輯
- 食物管理（隱藏、USDA 搜尋新增）
- 留言板

### 階段 5：部署上線
- 連接 Supabase 雲端資料庫
- 部署到 Streamlit Cloud
- 設定 Secrets 保護 API Key

### 階段 6：持續迭代
- 新增點心分類
- 新增膳食纖維、鈣、碳水化合物
- 加入留言板管理功能
- 手機版優化

---

## 🐛 遇到的困難與解決

| 困難 | 解決方式 |
|------|---------|
| 資料每次重新部署就消失 | 從 SQLite 改用 Supabase 雲端資料庫 |
| 不同使用者的食物混在一起 | 加入 `created_by` 欄位區分系統/個人食物 |
| 使用者隱私問題 | 加入密碼登入系統 |
| USDA API 單位換算複雜 | 建立 `common_unit` 和 `common_gram` 欄位 |
| 手機版側邊欄不好找 | 加入提示文字「按左上角箭頭打開」 |

---

## 📈 未來規劃

- [ ] 忘記密碼功能（Email 驗證）
- [ ] 營養圖表（週/月趨勢）
- [ ] 匯出飲食記錄為 CSV
- [ ] 更多原型食物營養資料
- [ ] PWA 安裝功能

---

## 💡 我學到了什麼

**硬技能**
- Streamlit 快速開發 Web APP
- Supabase 雲端資料庫操作
- RESTful API 串接（USDA）
- 資料庫設計與關聯
- Git 版本控制與雲端部署

**軟技能**
- 從 0 到 1 獨立開發完整專案
- 需求分析與功能規劃
- 問題解決與除錯能力
- 使用者體驗思考（手機版優化）

---

---

## 🔑 環境變數設定

在 Streamlit Cloud 的 Secrets 中設定：

```toml
supabase = {
    url = "https://your-project.supabase.co"
    key = "your-anon-key"
}

usda = {
    api_key = "your-usda-api-key"
}

