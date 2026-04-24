import streamlit as st
import pandas as pd
import requests
from datetime import date
from supabase import create_client, Client

st.set_page_config(page_title="WholeFood Tracker", page_icon="🍎")

# === 語言設定 ===
if "language" not in st.session_state:
    st.session_state.language = "zh"

# ==================== 語言字典 ====================
TEXT = {
    "zh": {
        "stats_title": "📊 今日營養統計",
        "query_date": "🔍 查詢日期",
        "no_record": "📭 還沒有記錄",
        "today_intake": "📈 今日攝取量",
        "protein": "🥩 蛋白質",
        "iron": "🩸 鐵",
        "vitamin_c": "🍊 維生素C",
        "fiber": "🌾 膳食纖維",
        "sugar": "🍬 糖",
        "calcium": "🦴 鈣",
        "carbs": "🍚 碳水化合物",
        "daily_goal": "📌 以下是根據你的個人資料計算的每日攝取目標",
        "progress": "🎯 今日進度",
        
        "logout": "🚪 登出",
        "profile_settings": "⚙️ 個人資料設定",
        "gender_male": "男",
        "gender_female": "女",
        "age": "年齡",
        "height": "身高 (公分)",
        "weight": "體重 (公斤)",
        "activity_level": "活動量",
        "activity_1": "久坐（辦公室工作，幾乎不運動）",
        "activity_2": "輕度活動（每週運動1-3天）",
        "activity_3": "中度活動（每週運動3-5天）",
        "activity_4": "高度活動（每週運動6-7天）",
        "activity_5": "極高度活動（體力勞動或每天訓練兩次）",
        "save": "💾 儲存個人資料",
        "saved": "✅ 已儲存！",
        "daily_calories": "🔥 每日熱量",
        "protein_goal": "🥩 蛋白質目標",
        "iron_goal": "🩸 鐵目標",
        "vitamin_c_goal": "🍊 維生素C目標",
        "fiber_goal": "🌾 膳食纖維目標",
        "calcium_goal": "🦴 鈣目標",
        "carbs_goal": "🍚 碳水化合物目標",
        
        "hide_foods": "🙈 隱藏不用的食物",
        "hide_caption": "勾選你想隱藏的食物",
        "food_category": "🥘 食物",
        "drink_category": "🥤 飲品",
        "snack_category": "🍪 點心",
        "save_hide": "💾 儲存隱藏設定",
        
        "custom_foods": "📝 自訂你的食物清單",
        "custom_caption": "搜尋英文食物名稱（資料來源：USDA 美國農業部）",
        "search_placeholder": "輸入英文食物名稱",
        "search_btn": "搜尋",
        "searching": "搜尋中...",
        "not_found": "找不到",
        "add_food": "➕ 食物",
        "add_drink": "🥤 飲品",
        "add_snack": "🍪 點心",
        "added": "已加入",
        
        "nutrition_helper": "💡 營養小幫手",
        "select_nutrient": "選擇你想補充的營養素",
        "iron_tip": "🩸 想補鐵？",
        "calcium_tip": "🦴 想補鈣？",
        "protein_tip": "🥩 想補蛋白質？",
        "vitamin_c_tip": "🍊 想補維生素C？",
        "iron_warning": "💡 茶和咖啡會抓住鐵，讓鐵排出體外",
        
        "record_title": "➕ 記錄飲食",
        "record_date": "記錄日期",
        "category_food": "食物",
        "category_vegfruit": "蔬果",
        "category_snack": "點心",
        "category_drink": "飲品",
        "category_oil": "油",  # 中文版
        "select_item": "選擇項目",
        "grams": "重量 (克)",
        "portion": "份量",
        "about_grams": "約",
        "meal_type": "餐別",
        "breakfast": "早餐",
        "lunch": "午餐",
        "dinner": "晚餐",
        "snack": "點心",
        "record_btn": "📝 記錄",
        "recorded": "✅ 已記錄",
        "no_items": "沒有可顯示的",
        
        "feedback": "💬 回饋與建議",
        "feedback_type": "類型",
        "bug": "🐛 回報 Bug",
        "suggestion": "💡 功能建議",
        "general": "📝 一般意見",
        "title": "標題",
        "content": "詳細內容",
        "image_url": "圖片網址（選填）",
        "submit": "📨 送出回饋",
        "submitted": "✅ 已送出，感謝你的回饋！",
        "fill_title": "請填寫標題和內容",
        
        "admin": "🔧 管理留言（僅限管理員）",
        "unread": "📬 有 {} 則未讀留言",
        "mark_read": "📖 標記已讀",
        "delete": "🗑️ 刪除",
        "no_feedback": "目前沒有留言",
        
        "login_register": "🔐 登入或註冊",
        "login_tab": "🔐 登入",
        "register_tab": "📝 註冊",
        "username": "名字",
        "password": "密碼",
        "confirm_password": "確認密碼",
        "remember_me": "記住我（30天內自動登入）",
        "login_btn": "登入",
        "register_btn": "註冊",
        "welcome_back": "歡迎回來，{}！",
        "login_error": "登入錯誤，請聯絡管理員：chinescha@gmail.com",
        "fill_username_password": "請輸入名字和密碼",
        "password_mismatch": "兩次密碼輸入不一致",
        "user_exists": "這個名字已經被註冊了，請改用其他名字",
        "register_success": "✅ 註冊成功！",
        "register_failed": "註冊失敗，請稍後再試",
        "fill_username_password_reg": "請填寫名字和密碼",
        "forgot_password": "📧 忘記密碼？請來信：chinescha@gmail.com，我會協助你重設",
        
        "mobile_tip": "📱 點擊左上角「☰」或「>」打開側邊欄",
        "disclaimer": "⚠️ **免責聲明**：本應用程式之營養數據主要來自美國農業部（USDA）FoodData Central 資料庫，僅供參考。",
        
        "iron_foods": """
**推薦食物**（每100g含量）：
- 🥩 豬肝：11mg
- 🥩 牛肉：2.6mg
- 🥬 菠菜：2.7mg
- 🥬 紅莧菜：11.8mg
- 🥚 蛋黃：5.5mg
- 🌰 黑芝麻：10.5mg
- 🦐 蝦皮：12mg

**⚠️ 注意事項**：
- 搭配維生素C（如橙、奇異果）幫助吸收
- 鈣會干擾鐵吸收，避免高鈣食物同時吃
""",
        "calcium_foods": """
**推薦食物**（每100g含量）：
- 🥛 牛奶：120mg
- 🧀 起司：700mg
- 🥬 芥藍菜：180mg
- 🥬 雨衣甘藍：150mg
- 🥚 雞蛋：50mg
- 🐟 小魚干：2200mg
- 🌰 黑芝麻：975mg

**⚠️ 注意事項**：
- 搭配維生素D（曬太陽）幫助吸收
- 咖啡、茶、可樂會影響鈣吸收
- 分次吃比一次吃效果好
""",
        "protein_foods": """
**推薦食物**（每100g含量）：
- 🍗 雞胸肉：31g
- 🥩 牛肉：26g
- 🐟 鮭魚：20g
- 🥚 雞蛋：12.6g
- 🥛 牛奶：3.3g
- 🥬 毛豆：11g
- 🥬 豆腐：8.1g

**⚠️ 注意事項**：
- 平均分配在三餐，吸收效果更好
- 運動後30分鐘內補充，幫助肌肉修復
- 植物性蛋白（豆類）和動物性蛋白交替吃
""",
        "vitaminc_foods": """
**推薦食物**（每100g含量）：
- 🥝 奇異果：92mg
- 🍊 橙：53mg
- 🥬 雨衣甘藍：120mg
- 🫑 彩椒：128mg
- 🥦 綠花椰菜：89mg
- 🍓 草莓：59mg
- 🍅 小蕃茄：25mg

**⚠️ 注意事項**：
- 維生素C怕熱，生吃或快炒最好
- 幫助鐵質吸收（補鐵時搭配吃）
- 幫助膠原蛋白生成
""",
    },
    "en": {
        "stats_title": "📊 Today's Nutrition Stats",
        "query_date": "🔍 Query Date",
        "no_record": "📭 No records yet",
        "today_intake": "📈 Today's Intake",
        "protein": "🥩 Protein",
        "iron": "🩸 Iron",
        "vitamin_c": "🍊 Vitamin C",
        "fiber": "🌾 Fiber",
        "sugar": "🍬 Sugar",
        "calcium": "🦴 Calcium",
        "carbs": "🍚 Carbs",
        "daily_goal": "📌 Daily nutrition goals based on your profile",
        "progress": "🎯 Today's Progress",
        
        "logout": "🚪 Logout",
        "profile_settings": "⚙️ Profile Settings",
        "gender_male": "Male",
        "gender_female": "Female",
        "age": "Age",
        "height": "Height (cm)",
        "weight": "Weight (kg)",
        "activity_level": "Activity Level",
        "activity_1": "Sedentary (office job, little exercise)",
        "activity_2": "Light (exercise 1-3 days/week)",
        "activity_3": "Moderate (exercise 3-5 days/week)",
        "activity_4": "Active (exercise 6-7 days/week)",
        "activity_5": "Very Active (physical labor or twice daily training)",
        "save": "💾 Save Profile",
        "saved": "✅ Saved!",
        "daily_calories": "🔥 Daily Calories",
        "protein_goal": "🥩 Protein Goal",
        "iron_goal": "🩸 Iron Goal",
        "vitamin_c_goal": "🍊 Vitamin C Goal",
        "fiber_goal": "🌾 Fiber Goal",
        "calcium_goal": "🦴 Calcium Goal",
        "carbs_goal": "🍚 Carbs Goal",
        
        "hide_foods": "🙈 Hide Unused Foods",
        "hide_caption": "Check foods you want to hide",
        "food_category": "🥘 Food",
        "drink_category": "🥤 Drink",
        "snack_category": "🍪 Snack",
        "save_hide": "💾 Save Hide Settings",
        
        "custom_foods": "📝 Custom Food List",
        "custom_caption": "Search English food name (Source: USDA FoodData Central)",
        "search_placeholder": "Enter English food name",
        "search_btn": "Search",
        "searching": "Searching...",
        "not_found": "Not found",
        "add_food": "➕ Food",
        "add_drink": "🥤 Drink",
        "add_snack": "🍪 Snack",
        "added": "Added",
        
        "nutrition_helper": "💡 Nutrition Helper",
        "select_nutrient": "Select nutrient",
        "iron_tip": "🩸 Want more Iron?",
        "calcium_tip": "🦴 Want more Calcium?",
        "protein_tip": "🥩 Want more Protein?",
        "vitamin_c_tip": "🍊 Want more Vitamin C?",
        "iron_warning": "💡 Tea and coffee can reduce iron absorption",
        
        "record_title": "➕ Log Food",
        "record_date": "Date",
        "category_food": "Food",
        "category_vegfruit": "Veg/Fruit",
        "category_snack": "Snack",
        "category_drink": "Drink",
        "select_item": "Select item",
        "grams": "Weight (g)",
        "portion": "Portion",
        "about_grams": "approx",
        "meal_type": "Meal",
        "breakfast": "Breakfast",
        "lunch": "Lunch",
        "dinner": "Dinner",
        "snack": "Snack",
        "record_btn": "📝 Log",
        "recorded": "✅ Logged",
        "no_items": "No items to show",
        
        "feedback": "💬 Feedback",
        "feedback_type": "Type",
        "bug": "🐛 Bug Report",
        "suggestion": "💡 Feature Suggestion",
        "general": "📝 General",
        "title": "Title",
        "content": "Content",
        "image_url": "Image URL (optional)",
        "submit": "📨 Submit",
        "submitted": "✅ Submitted, thank you!",
        "fill_title": "Please fill in title and content",
        
        "admin": "🔧 Manage Feedback (Admin only)",
        "unread": "📬 {} unread messages",
        "mark_read": "📖 Mark as read",
        "delete": "🗑️ Delete",
        "no_feedback": "No feedback yet",
        
        "login_register": "🔐 Login or Register",
        "login_tab": "🔐 Login",
        "register_tab": "📝 Register",
        "username": "Username",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "remember_me": "Remember me (30 days auto-login)",
        "login_btn": "Login",
        "register_btn": "Register",
        "welcome_back": "Welcome back, {}!",
        "login_error": "Login error, please contact: chinescha@gmail.com",
        "fill_username_password": "Please enter username and password",
        "password_mismatch": "Passwords do not match",
        "user_exists": "This username is already taken",
        "register_success": "✅ Registration successful!",
        "register_failed": "Registration failed, please try again",
        "fill_username_password_reg": "Please enter username and password",
        "forgot_password": "📧 Forgot password? Email: chinescha@gmail.com",
        
        "mobile_tip": "📱 Click the arrow in the top-left corner to open the sidebar",
        "disclaimer": "⚠️ **Disclaimer**: Nutrition data from USDA FoodData Central database. For reference only.",
        
        "iron_foods": """
**Recommended Foods** (per 100g):
- 🥩 Pork Liver: 11mg
- 🥩 Beef: 2.6mg
- 🥬 Spinach: 2.7mg
- 🥬 Red Amaranth: 11.8mg
- 🥚 Egg Yolk: 5.5mg
- 🌰 Black Sesame: 10.5mg
- 🦐 Dried Shrimp: 12mg

**⚠️ Tips**:
- Pair with Vitamin C (oranges, kiwi) for better absorption
- Calcium interferes with iron absorption
""",
        "calcium_foods": """
**Recommended Foods** (per 100g):
- 🥛 Milk: 120mg
- 🧀 Cheese: 700mg
- 🥬 Kale: 150mg
- 🥬 Chinese Broccoli: 180mg
- 🥚 Egg: 50mg
- 🐟 Small Dried Fish: 2200mg
- 🌰 Black Sesame: 975mg

**⚠️ Tips**:
- Pair with Vitamin D (sunlight) for better absorption
- Coffee, tea, soda reduce calcium absorption
""",
        "protein_foods": """
**Recommended Foods** (per 100g):
- 🍗 Chicken Breast: 31g
- 🥩 Beef: 26g
- 🐟 Salmon: 20g
- 🥚 Egg: 12.6g
- 🥛 Milk: 3.3g
- 🥬 Edamame: 11g
- 🥬 Tofu: 8.1g

**⚠️ Tips**:
- Spread protein intake throughout the day
- Consume within 30 min post-workout
""",
        "vitaminc_foods": """
**Recommended Foods** (per 100g):
- 🥝 Kiwi: 92mg
- 🍊 Orange: 53mg
- 🥬 Kale: 120mg
- 🫑 Bell Pepper: 128mg
- 🥦 Broccoli: 89mg
- 🍓 Strawberry: 59mg
- 🍅 Cherry Tomato: 25mg

**⚠️ Tips**:
- Vitamin C is heat sensitive, eat raw or quick-cook
- Helps iron absorption
""",
    }
}

def t(key):
    return TEXT[st.session_state.language].get(key, key)

# === 使用 Secrets 讀取金鑰 ===
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
USDA_API_KEY = st.secrets["usda"]["api_key"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === 登入狀態管理 ===
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_user_name" not in st.session_state:
    st.session_state.login_user_name = ""
if "log_date" not in st.session_state:
    st.session_state.log_date = date.today()
if "view_date" not in st.session_state:
    st.session_state.view_date = date.today()

# === 登入/註冊函數 ===
def login_user(user_name, password):
    try:
        result = supabase.table("user_profile").select("password").eq("user_name", user_name).execute()
        if result.data and result.data[0]["password"] == password:
            return True
        return False
    except Exception as e:
        st.error(f"Login error: {e}")
        return False

def register_user(user_name, password, gender, age, height, weight, activity_level):
    try:
        supabase.table("user_profile").insert({
            "user_name": user_name,
            "password": password,
            "gender": gender,
            "age": int(age),
            "height": float(height),
            "weight": float(weight),
            "activity_level": activity_level
        }).execute()
        return True
    except Exception as e:
        st.error(f"Registration error: {e}")
        return False

def user_exists(user_name):
    try:
        result = supabase.table("user_profile").select("user_name").eq("user_name", user_name).execute()
        return len(result.data) > 0
    except Exception:
        return False

# === 輔助函數 ===
def get_user_profile(user_name):
    try:
        result = supabase.table("user_profile").select("*").eq("user_name", user_name).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception:
        return None

def save_user_profile(user_name, gender, age, height, weight, activity_level):
    try:
        supabase.table("user_profile").update({
            "gender": gender,
            "age": int(age),
            "height": float(height),
            "weight": float(weight),
            "activity_level": activity_level
        }).eq("user_name", user_name).execute()
        return True
    except Exception:
        return False

def get_foods(user_name, category):
    try:
        hidden = supabase.table("hidden_foods").select("food_id").eq("user_name", user_name).execute()
        hidden_ids = [h["food_id"] for h in hidden.data]
        result = supabase.table("foods").select("*").eq("category", category).in_("created_by", ["system", user_name]).execute()
        foods = [f for f in result.data if f["food_id"] not in hidden_ids]
        return foods
    except Exception:
        return []

def save_meal_log(user_name, log_date, meal_type, food_id, grams):
    try:
        supabase.table("meal_logs").insert({
            "user_name": user_name,
            "log_date": log_date.strftime("%Y-%m-%d"),
            "meal_type": meal_type,
            "food_id": food_id,
            "grams": float(grams)
        }).execute()
        return True
    except Exception:
        return False

def get_today_stats(user_name, target_date):
    try:
        result = supabase.table("meal_logs").select("""
            food_id,
            foods!inner(food_name, protein_g_per_100g, iron_mg_per_100g, 
                       vitamin_c_mg_per_100g, fiber_g_per_100g, sugar_g_per_100g,
                       calcium_mg_per_100g, carbs_g_per_100g),
            grams
        """).eq("user_name", user_name).eq("log_date", target_date.strftime("%Y-%m-%d")).execute()
        
        stats = []
        for record in result.data:
            food = record["foods"]
            grams = record["grams"]
            stats.append({
                "food_name": food["food_name"],
                "grams": grams,
                "protein": food["protein_g_per_100g"] * grams / 100,
                "iron": food["iron_mg_per_100g"] * grams / 100,
                "vitamin_c": food["vitamin_c_mg_per_100g"] * grams / 100,
                "fiber": food.get("fiber_g_per_100g", 0) * grams / 100,
                "sugar": food.get("sugar_g_per_100g", 0) * grams / 100,
                "calcium": food.get("calcium_mg_per_100g", 0) * grams / 100,
                "carbs": food.get("carbs_g_per_100g", 0) * grams / 100
            })
        return stats
    except Exception:
        return []

def toggle_hide_food(user_name, food_id, is_hidden):
    try:
        if is_hidden:
            supabase.table("hidden_foods").insert({"user_name": user_name, "food_id": food_id}).execute()
        else:
            supabase.table("hidden_foods").delete().eq("user_name", user_name).eq("food_id", food_id).execute()
        return True
    except Exception:
        return False

def search_usda_food(query):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"api_key": USDA_API_KEY, "query": query, "pageSize": 3}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        results = []
        for food in data.get("foods", []):
            nutrients = {n["nutrientName"]: n["value"] for n in food.get("foodNutrients", [])}
            results.append({
                "name": food["description"],
                "protein": nutrients.get("Protein", 0),
                "iron": nutrients.get("Iron, Fe", 0),
                "vitamin_c": nutrients.get("Vitamin C, total ascorbic acid", 0),
                "calories": nutrients.get("Energy", 0),
                "fiber": nutrients.get("Fiber, total dietary", 0),
                "calcium": nutrients.get("Calcium, Ca", 0),
                "carbs": nutrients.get("Carbohydrate, by difference", 0)
            })
        return results
    except Exception:
        return []

def add_user_food(user_name, food_name, category, protein, iron, vitamin_c, calories, unit, gram, fiber=0, calcium=0, carbs=0):
    try:
        supabase.table("foods").insert({
            "food_name": food_name, "category": category,
            "protein_g_per_100g": float(protein), "iron_mg_per_100g": float(iron),
            "vitamin_c_mg_per_100g": float(vitamin_c), "calories_per_100g": int(calories),
            "common_unit": unit, "common_gram": float(gram), "created_by": user_name,
            "fiber_g_per_100g": float(fiber), "calcium_mg_per_100g": float(calcium),
            "carbs_g_per_100g": float(carbs)
        }).execute()
        return True
    except Exception:
        return False

def save_feedback(user_name, fb_type, title, content, image_url):
    try:
        supabase.table("feedbacks").insert({
            "user_name": user_name, "feedback_type": fb_type,
            "title": title, "content": content, "image_url": image_url
        }).execute()
        return True
    except Exception:
        return False

def get_feedbacks():
    try:
        result = supabase.table("feedbacks").select("*").order("created_at", desc=True).execute()
        return result.data
    except Exception:
        return []

def mark_feedback_read(feedback_id):
    try:
        supabase.table("feedbacks").update({"is_read": 1}).eq("feedback_id", feedback_id).execute()
        return True
    except Exception:
        return False

def delete_feedback(feedback_id):
    try:
        supabase.table("feedbacks").delete().eq("feedback_id", feedback_id).execute()
        return True
    except Exception:
        return False

def calculate_bmr(gender, weight, height, age):
    if gender == "男":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_tdee(bmr, activity_level):
    activity_factors = {
        "久坐（辦公室工作，幾乎不運動）": 1.2,
        "輕度活動（每週運動1-3天）": 1.375,
        "中度活動（每週運動3-5天）": 1.55,
        "高度活動（每週運動6-7天）": 1.725,
        "極高度活動（體力勞動或每天訓練兩次）": 1.9
    }
    return bmr * activity_factors.get(activity_level, 1.2)

def get_nutrition_goals(gender, age):
    return {"protein_per_kg": 1.1, "iron_male": 10, "iron_female": 15, "vitamin_c": 100, "fiber": 25, "calcium": 1000, "carbs": 250}

# === 自動登入檢查 ===
if not st.session_state.logged_in:
    auto_login = st.query_params.get("auto_login", [""])[0]
    if auto_login:
        st.session_state.logged_in = True
        st.session_state.login_user_name = auto_login
        st.rerun()

# === 登入/註冊畫面 ===

  # === 登入/註冊畫面 ===
if not st.session_state.logged_in:
    st.markdown("""
    <div style="background-color: #f0fdf4; padding: 1.5rem; border-radius: 1rem; margin-bottom: 1rem; text-align: center;">
        <h1 style="color: #166534;">🥗 WholeFood Tracker</h1>
        <p>Whole foods only, no processed foods.</p>
        <p>Want to know if you're getting enough nutrition?<br>Protein? Iron? Vitamin C? Fiber?</p>
        <p><strong>You'll find the answer here.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("📧 Forgot password? Email: chinescha@gmail.com")
    
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "login"
    
    col_tab1, col_tab2 = st.columns(2)
    with col_tab1:
        if st.button("🔐 Login", use_container_width=True, type="primary" if st.session_state.active_tab == "login" else "secondary"):
            st.session_state.active_tab = "login"
            st.rerun()
    with col_tab2:
        if st.button("📝 Register", use_container_width=True, type="primary" if st.session_state.active_tab == "register" else "secondary"):
            st.session_state.active_tab = "register"
            st.rerun()
    
    st.divider()
    
    if st.session_state.active_tab == "login":
        with st.container():
            login_name = st.text_input("Username", key="login_name")
            login_password = st.text_input("Password", type="password", key="login_password")
            remember_me = st.checkbox("Remember me (30 days auto-login)")
            
            if st.button("Login", type="primary"):
                if login_name and login_password:
                    if login_user(login_name, login_password):
                        st.session_state.logged_in = True
                        st.session_state.login_user_name = login_name
                        if remember_me:
                            st.query_params["auto_login"] = login_name
                        st.success(f"Welcome back, {login_name}!")
                        st.rerun()
                    else:
                        st.error("Login error, please contact: chinescha@gmail.com")
                else:
                    st.warning("Please enter username and password")
    else:
        with st.container():
            reg_name = st.text_input("Username", key="reg_name")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
            
            reg_gender = st.selectbox("Gender", ["Male", "Female"])
            reg_age = st.number_input("Age", min_value=15, max_value=120, value=30)
            reg_height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
            reg_weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=65)
            reg_activity = st.selectbox("Activity Level", [
                "Sedentary (office job, little exercise)",
                "Light (exercise 1-3 days/week)",
                "Moderate (exercise 3-5 days/week)",
                "Active (exercise 6-7 days/week)",
                "Very Active (physical labor or twice daily training)"
            ])
            
            if st.button("Register", type="primary"):
                if reg_name and reg_password:
                    if reg_password != reg_password_confirm:
                        st.error("Passwords do not match")
                    elif user_exists(reg_name):
                        st.error("This username is already taken")
                    else:
                        if register_user(reg_name, reg_password, reg_gender, reg_age, reg_height, reg_weight, reg_activity):
                            st.success("✅ Registration successful!")
                            st.balloons()
                            st.session_state.active_tab = "login"
                            st.rerun()
                        else:
                            st.error("Registration failed, please try again")
                else:
                    st.warning("Please enter username and password")
    
    st.stop()

# === 已登入後的 APP 內容 ===
user_name = st.session_state.login_user_name

# 側邊欄
with st.sidebar:
    # 語言切換（只有登入後才顯示）
    col_lang1, col_lang2 = st.columns(2)
    with col_lang1:
        if st.button("🌐 中文", use_container_width=True, type="primary" if st.session_state.language == "zh" else "secondary"):
            st.session_state.language = "zh"
            st.rerun()
    with col_lang2:
        if st.button("🌐 English", use_container_width=True, type="primary" if st.session_state.language == "en" else "secondary"):
            st.session_state.language = "en"
            st.rerun()
    
    st.divider()
    
    if st.button(t("logout")):
        st.session_state.logged_in = False
        st.session_state.login_user_name = ""
        st.rerun()
    

    
    st.divider()
    st.header(f"👤 {user_name}")
    st.divider()
    
    # 個人資料設定
    with st.expander(t("profile_settings")):
        profile = get_user_profile(user_name)
        
        gender = st.selectbox(t("gender"), [t("gender_male"), t("gender_female")], index=0 if not profile else (0 if profile["gender"] == "男" else 1))
        age = st.number_input(t("age"), min_value=15.0, max_value=120.0, value=float(profile["age"]) if profile else 30.0)
        height = st.number_input(t("height"), min_value=100.0, max_value=250.0, value=float(profile["height"]) if profile else 170.0)
        weight = st.number_input(t("weight"), min_value=30.0, max_value=200.0, value=float(profile["weight"]) if profile else 65.0)
        activity_level = st.selectbox(t("activity_level"), [
            t("activity_1"), t("activity_2"), t("activity_3"), t("activity_4"), t("activity_5")
        ], index=0 if not profile else 0)
        
        if st.button(t("save"), type="primary"):
            gender_val = "男" if gender == t("gender_male") else "女"
            if save_user_profile(user_name, gender_val, age, height, weight, activity_level):
                st.success(t("saved"))
                st.rerun()
        
        if profile or (user_name and age):
            gender_val = "男" if gender == t("gender_male") else "女"
            bmr = calculate_bmr(gender_val, weight, height, age)
            tdee = calculate_tdee(bmr, activity_level)
            goals = get_nutrition_goals(gender_val, age)
            protein_goal = weight * goals["protein_per_kg"]
            iron_goal = goals["iron_female"] if gender_val == "女" else goals["iron_male"]
            vitamin_c_goal = goals["vitamin_c"]
            fiber_goal = goals["fiber"]
            calcium_goal = goals["calcium"]
            carbs_goal = goals["carbs"]
            
            st.divider()
            st.metric(t("daily_calories"), f"{int(tdee)} kcal")
            st.metric(t("protein_goal"), f"{protein_goal:.0f} g")
            st.metric(t("iron_goal"), f"{iron_goal:.0f} mg")
            st.metric(t("vitamin_c_goal"), f"{vitamin_c_goal:.0f} mg")
            st.metric(t("fiber_goal"), f"{fiber_goal:.0f} g")
            st.metric(t("calcium_goal"), f"{calcium_goal:.0f} mg")
            st.metric(t("carbs_goal"), f"{carbs_goal:.0f} g")
            
            st.session_state.protein_goal = protein_goal
            st.session_state.iron_goal = iron_goal
            st.session_state.vitamin_c_goal = vitamin_c_goal
            st.session_state.fiber_goal = fiber_goal
            st.session_state.calcium_goal = calcium_goal
            st.session_state.carbs_goal = carbs_goal
    
    st.divider()
    
    # 隱藏食物管理
    with st.expander(t("hide_foods")):
        st.caption(t("hide_caption"))
        try:
            all_foods = supabase.table("foods").select("*").eq("created_by", "system").execute()
            food_items = [f for f in all_foods.data if f["category"] == "食物"]
            drink_items = [f for f in all_foods.data if f["category"] == "飲品"]
            snack_items = [f for f in all_foods.data if f["category"] == "點心"]
            
            user_foods = supabase.table("foods").select("*").eq("created_by", user_name).execute()
            for f in user_foods.data:
                if f["category"] == "食物" and f not in food_items:
                    food_items.append(f)
                elif f["category"] == "飲品" and f not in drink_items:
                    drink_items.append(f)
                elif f["category"] == "點心" and f not in snack_items:
                    snack_items.append(f)
            
            hidden = supabase.table("hidden_foods").select("food_id").eq("user_name", user_name).execute()
            hidden_ids = set([h["food_id"] for h in hidden.data])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader(t("food_category"))
                for f in food_items:
                    is_hidden = f["food_id"] in hidden_ids
                    if st.checkbox(f"{f['food_name']}", value=is_hidden, key=f"hide_{f['food_id']}"):
                        if not is_hidden:
                            toggle_hide_food(user_name, f["food_id"], True)
                    else:
                        if is_hidden:
                            toggle_hide_food(user_name, f["food_id"], False)
            with col2:
                st.subheader(t("drink_category"))
                for f in drink_items:
                    is_hidden = f["food_id"] in hidden_ids
                    if st.checkbox(f"{f['food_name']}", value=is_hidden, key=f"hide_{f['food_id']}"):
                        if not is_hidden:
                            toggle_hide_food(user_name, f["food_id"], True)
                    else:
                        if is_hidden:
                            toggle_hide_food(user_name, f["food_id"], False)
            with col3:
                st.subheader(t("snack_category"))
                for f in snack_items:
                    is_hidden = f["food_id"] in hidden_ids
                    if st.checkbox(f"{f['food_name']}", value=is_hidden, key=f"hide_{f['food_id']}"):
                        if not is_hidden:
                            toggle_hide_food(user_name, f["food_id"], True)
                    else:
                        if is_hidden:
                            toggle_hide_food(user_name, f["food_id"], False)
            
            if st.button(t("save_hide")):
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.divider()
    
    # 自訂食物清單
    with st.expander(t("custom_foods")):
        st.caption(t("custom_caption"))
        search_term = st.text_input(t("search_placeholder"))
        if st.button(t("search_btn")):
            if search_term:
                with st.spinner(t("searching")):
                    results = search_usda_food(search_term)
                    if results:
                        st.session_state.search_results = results
                    else:
                        st.warning(t("not_found"))
        
        if "search_results" in st.session_state:
            for i, food in enumerate(st.session_state.search_results):
                with st.expander(f"{food['name'][:50]}"):
                    st.write(f"{t('protein')}: {food['protein']:.1f}g | {t('iron')}: {food['iron']:.1f}mg | {t('vitamin_c')}: {food['vitamin_c']:.1f}mg")
                    st.write(f"{t('fiber')}: {food['fiber']:.1f}g | {t('calcium')}: {food['calcium']:.0f}mg | {t('carbs')}: {food['carbs']:.1f}g")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button(f"{t('add_food')}", key=f"add_food_{i}"):
                            if add_user_food(user_name, food['name'], '食物', food['protein'], food['iron'], food['vitamin_c'], food['calories'], '克', 1.0, food['fiber'], food['calcium'], food['carbs']):
                                st.success(f"{t('added')}：{food['name']}")
                                del st.session_state.search_results
                                st.rerun()
                    with col_b:
                        if st.button(f"{t('add_drink')}", key=f"add_drink_{i}"):
                            if add_user_food(user_name, food['name'], '飲品', food['protein'], food['iron'], food['vitamin_c'], food['calories'], '杯', 240.0, food['fiber'], food['calcium'], food['carbs']):
                                st.success(f"{t('added')}：{food['name']}")
                                del st.session_state.search_results
                                st.rerun()
                    with col_c:
                        if st.button(f"{t('add_snack')}", key=f"add_snack_{i}"):
                            if add_user_food(user_name, food['name'], '點心', food['protein'], food['iron'], food['vitamin_c'], food['calories'], '克', 1.0, food['fiber'], food['calcium'], food['carbs']):
                                st.success(f"{t('added')}：{food['name']}")
                                del st.session_state.search_results
                                st.rerun()
    
    st.divider()
    
    # === 營養小幫手 ===
    with st.expander(t("nutrition_helper")):
        st.caption(t("select_nutrient"))
        
        nutrient = st.selectbox(
            t("select_nutrient"),
            ["🩸 Iron", "🦴 Calcium", "🥩 Protein", "🍊 Vitamin C"]
        )
        
        st.markdown("---")
        
        if nutrient == "🩸 Iron":
            st.subheader(t("iron_tip"))
            st.markdown(t("iron_foods"))
            st.markdown(f'<span style="color: gray; font-size: 0.8rem;">{t("iron_warning")}</span>', unsafe_allow_html=True)
        elif nutrient == "🦴 Calcium":
            st.subheader(t("calcium_tip"))
            st.markdown(t("calcium_foods"))
        elif nutrient == "🥩 Protein":
            st.subheader(t("protein_tip"))
            st.markdown(t("protein_foods"))
        elif nutrient == "🍊 Vitamin C":
            st.subheader(t("vitamin_c_tip"))
            st.markdown(t("vitaminc_foods"))
    
    st.divider()
    
    # 記錄飲食
    st.header(t("record_title"))
    
    log_date = st.date_input(t("record_date"), value=st.session_state.log_date, key="log_date_picker")
    st.session_state.log_date = log_date
    
    selected_category = st.radio(t("category"), [t("category_food"), t("category_vegfruit"), t("category_snack"), t("category_drink"), t("category_oil")], horizontal=True)
    
    # 映射分類到資料庫值
    category_map = {
        t("category_food"): "食物",
        t("category_vegfruit"): "蔬果",
        t("category_snack"): "點心",
        t("category_drink"): "飲品",
        t("category_oil"): "油"
    }
    db_category = category_map[selected_category]
    
    foods = get_foods(user_name, db_category)
    
    if foods:
        food_options = {f["food_name"]: f for f in foods}
        selected_food_name = st.selectbox(t("select_item"), list(food_options.keys()))
        selected_food = food_options[selected_food_name]
        
        if selected_food["common_unit"] == "克":
            grams = st.number_input(t("grams"), min_value=1, max_value=2000, value=100)
        else:
            portion = st.number_input(f"{t('portion')} ({selected_food['common_unit']})", min_value=0.25, max_value=10.0, value=1.0, step=0.25)
            grams = selected_food["common_gram"] * portion
            st.caption(f"{t('about_grams')} {grams:.0f} {t('grams')}")
        
        meal_type = st.selectbox(t("meal_type"), [t("breakfast"), t("lunch"), t("dinner"), t("snack")])
        
        # 映射餐別
        meal_map = {t("breakfast"): "早餐", t("lunch"): "午餐", t("dinner"): "晚餐", t("snack"): "點心"}
        
        if st.button(t("record_btn")):
            if save_meal_log(user_name, log_date, meal_map[meal_type], selected_food["food_id"], grams):
                st.success(f"{t('recorded')} {selected_food_name} {t('to')} {log_date}")
                st.session_state.view_date = log_date
                st.rerun()
    else:
        st.info(f"{t('no_items')} {selected_category}")
    
    st.divider()
    
    # 留言板
    with st.expander(t("feedback")):
        fb_type = st.selectbox(t("feedback_type"), [t("bug"), t("suggestion"), t("general")])
        fb_title = st.text_input(t("title"), placeholder=t("title"))
        fb_content = st.text_area(t("content"), height=100, placeholder=t("content"))
        fb_image_url = st.text_input(t("image_url"), placeholder="https://...")
        
        if st.button(t("submit")):
            if fb_title and fb_content:
                if save_feedback(user_name, fb_type, fb_title, fb_content, fb_image_url):
                    st.success(t("submitted"))
                    st.rerun()
            else:
                st.warning(t("fill_title"))
    
    # 管理留言
    if user_name == "Jessica Sara Lei ENFJ":
        with st.expander(t("admin")):
            feedbacks = get_feedbacks()
            if feedbacks:
                unread_count = len([f for f in feedbacks if not f["is_read"]])
                if unread_count > 0:
                    st.warning(t("unread").format(unread_count))
                
                for fb in feedbacks:
                    with st.container():
                        status = "✅ Read" if fb["is_read"] else "🆕 Unread"
                        st.markdown(f"**{fb['feedback_type']}** | {status} | 📅 {fb['created_at'][:16]}")
                        st.markdown(f"**{fb['title']}**")
                        st.caption(f"👤 {fb['user_name'] or 'Anonymous'}")
                        st.write(fb['content'])
                        if fb['image_url']:
                            st.markdown(f"[🔗 View Image]({fb['image_url']})")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if not fb["is_read"] and st.button(t("mark_read"), key=f"read_{fb['feedback_id']}"):
                                mark_feedback_read(fb['feedback_id'])
                                st.rerun()
                        with col2:
                            if st.button(t("delete"), key=f"del_{fb['feedback_id']}"):
                                delete_feedback(fb['feedback_id'])
                                st.rerun()
                        st.divider()
            else:
                st.info(t("no_feedback"))

# === 主畫面 ===
# 只在手機上顯示的提示
st.markdown(f"""
<style>
@media screen and (max-width: 768px) {{
    .mobile-only {{
        display: block;
    }}
}}
@media screen and (min-width: 769px) {{
    .mobile-only {{
        display: none;
    }}
}}
</style>
<div class="mobile-only" style="background-color: #e0f2fe; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 1rem; text-align: center; border-left: 4px solid #0284c7;">
    {t('mobile_tip')}
</div>
""", unsafe_allow_html=True)

st.header(t("stats_title"))

view_date = st.date_input(t("query_date"), value=st.session_state.view_date, key="view_date_picker")
st.session_state.view_date = view_date

stats = get_today_stats(user_name, view_date)

st.markdown("---")
st.caption(f"{t('user_label')}：{user_name}")
st.caption(f"{t('query_date')}：{view_date}")
st.markdown("---")

if stats:
    df = pd.DataFrame(stats)
    st.dataframe(df[["food_name", "grams", "protein", "iron", "vitamin_c", "fiber", "calcium", "carbs"]], use_container_width=True)
    
    total_protein = df["protein"].sum()
    total_iron = df["iron"].sum()
    total_vitamin_c = df["vitamin_c"].sum()
    total_fiber = df["fiber"].sum()
    total_sugar = df["sugar"].sum()
    total_calcium = df["calcium"].sum()
    total_carbs = df["carbs"].sum()
    
    st.subheader(t("today_intake"))
    
    col1, col2, col3 = st.columns(3)
    col1.metric(t("protein"), f"{total_protein:.1f} g")
    col2.metric(t("iron"), f"{total_iron:.1f} mg")
    col3.metric(t("vitamin_c"), f"{total_vitamin_c:.1f} mg")
    
    col4, col5, col6 = st.columns(3)
    col4.metric(t("fiber"), f"{total_fiber:.1f} g")
    col5.metric(t("sugar"), f"{total_sugar:.1f} g")
    col6.metric(t("calcium"), f"{total_calcium:.0f} mg")
    
    col7, col8, col9 = st.columns(3)
    col7.metric(t("carbs"), f"{total_carbs:.1f} g")
    
    if "protein_goal" in st.session_state:
        st.markdown("---")
        st.caption(t("daily_goal"))
        
        goal_col1, goal_col2, goal_col3, goal_col4 = st.columns(4)
        goal_col1.metric(t("protein_goal"), f"{st.session_state.protein_goal:.0f} g")
        goal_col2.metric(t("iron_goal"), f"{st.session_state.iron_goal:.0f} mg")
        goal_col3.metric(t("vitamin_c_goal"), f"{st.session_state.vitamin_c_goal:.0f} mg")
        goal_col4.metric(t("fiber_goal"), f"{st.session_state.fiber_goal:.0f} g")
        
        goal_col5, goal_col6, goal_col7 = st.columns(3)
        goal_col5.metric(t("calcium_goal"), f"{st.session_state.calcium_goal:.0f} mg")
        goal_col6.metric(t("carbs_goal"), f"{st.session_state.carbs_goal:.0f} g")
        
        st.subheader(t("progress"))
        
        prog_col1, prog_col2 = st.columns(2)
        with prog_col1:
            protein_pct = min(100, total_protein / st.session_state.protein_goal * 100)
            st.write(f"{t('protein')}：{total_protein:.1f} / {st.session_state.protein_goal:.0f} g ({protein_pct:.0f}%)")
            st.progress(protein_pct / 100)
            
            iron_pct = min(100, total_iron / st.session_state.iron_goal * 100)
            st.write(f"{t('iron')}：{total_iron:.1f} / {st.session_state.iron_goal:.0f} mg ({iron_pct:.0f}%)")
            st.progress(iron_pct / 100)
            
            fiber_pct = min(100, total_fiber / st.session_state.fiber_goal * 100)
            st.write(f"{t('fiber')}：{total_fiber:.1f} / {st.session_state.fiber_goal:.0f} g ({fiber_pct:.0f}%)")
            st.progress(fiber_pct / 100)
        
        with prog_col2:
            vitamin_c_pct = min(100, total_vitamin_c / st.session_state.vitamin_c_goal * 100)
            st.write(f"{t('vitamin_c')}：{total_vitamin_c:.1f} / {st.session_state.vitamin_c_goal:.0f} mg ({vitamin_c_pct:.0f}%)")
            st.progress(vitamin_c_pct / 100)
            
            calcium_pct = min(100, total_calcium / st.session_state.calcium_goal * 100)
            st.write(f"{t('calcium')}：{total_calcium:.0f} / {st.session_state.calcium_goal:.0f} mg ({calcium_pct:.0f}%)")
            st.progress(calcium_pct / 100)
            
            carbs_pct = min(100, total_carbs / st.session_state.carbs_goal * 100)
            st.write(f"{t('carbs')}：{total_carbs:.1f} / {st.session_state.carbs_goal:.0f} g ({carbs_pct:.0f}%)")
            st.progress(carbs_pct / 100)
else:
    st.info(t("no_record"))

# === 免責聲明 ===
st.markdown("---")
st.caption(t("disclaimer"))