import streamlit as st
import pandas as pd
import requests
from datetime import date
from supabase import create_client, Client

st.set_page_config(page_title="營養計算器", page_icon="🍎")
# st.title("🍎 每日營養計算器")

# === 使用 Secrets 讀取金鑰 ===
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
USDA_API_KEY = st.secrets["usda"]["api_key"]

# 初始化 Supabase
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
        st.error(f"登入錯誤：{e}")
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
        st.error(f"註冊失敗：{e}")
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

# === 登入/註冊畫面 ===
if not st.session_state.logged_in:
    st.markdown("""
    <div style="background-color: #f0fdf4; padding: 1.5rem; border-radius: 1rem; margin-bottom: 1rem; text-align: center;">
        <h1 style="color: #166534;">🥗 原型食物計算器</h1>
        <p>只算原型食物，不算加工食品。</p>
        <p>想知道每天吃的營養夠不夠？<br>蛋白質？鐵？維生素C？膳食纖維？</p>
        <p><strong>這裡有答案。</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("📧 忘記密碼？請來信：chinescha@gmail.com，我會協助你重設")
    
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "登入"
    
    col_tab1, col_tab2 = st.columns(2)
    with col_tab1:
        if st.button("🔐 登入", use_container_width=True, type="primary" if st.session_state.active_tab == "登入" else "secondary"):
            st.session_state.active_tab = "登入"
            st.rerun()
    with col_tab2:
        if st.button("📝 註冊", use_container_width=True, type="primary" if st.session_state.active_tab == "註冊" else "secondary"):
            st.session_state.active_tab = "註冊"
            st.rerun()
    
    st.divider()
    
    if st.session_state.active_tab == "登入":
        with st.container():
            login_name = st.text_input("名字", key="login_name")
            login_password = st.text_input("密碼", type="password", key="login_password")
            
            if st.button("登入", type="primary"):
                if login_name and login_password:
                    if login_user(login_name, login_password):
                        st.session_state.logged_in = True
                        st.session_state.login_user_name = login_name
                        st.success(f"歡迎回來，{login_name}！")
                        st.rerun()
                    else:
                        st.error("登入錯誤，請聯絡管理員：chinescha@gmail.com")
                else:
                    st.warning("請輸入名字和密碼")
    else:
        with st.container():
            reg_name = st.text_input("名字", key="reg_name")
            reg_password = st.text_input("密碼", type="password", key="reg_password")
            reg_password_confirm = st.text_input("確認密碼", type="password", key="reg_password_confirm")
            
            reg_gender = st.selectbox("性別", ["男", "女"])
            reg_age = st.number_input("年齡", min_value=15, max_value=120, value=30)
            reg_height = st.number_input("身高 (公分)", min_value=100, max_value=250, value=170)
            reg_weight = st.number_input("體重 (公斤)", min_value=30, max_value=200, value=65)
            reg_activity = st.selectbox("活動量", [
                "久坐（辦公室工作，幾乎不運動）",
                "輕度活動（每週運動1-3天）",
                "中度活動（每週運動3-5天）",
                "高度活動（每週運動6-7天）",
                "極高度活動（體力勞動或每天訓練兩次）"
            ])
            
            if st.button("註冊", type="primary"):
                if reg_name and reg_password:
                    if reg_password != reg_password_confirm:
                        st.error("兩次密碼輸入不一致")
                    elif user_exists(reg_name):
                        st.error("這個名字已經被註冊了，請改用其他名字")
                    else:
                        if register_user(reg_name, reg_password, reg_gender, reg_age, reg_height, reg_weight, reg_activity):
                            st.success("✅ 註冊成功！")
                            st.balloons()
                            st.session_state.active_tab = "登入"
                            st.rerun()
                        else:
                            st.error("註冊失敗，請稍後再試")
                else:
                    st.warning("請填寫名字和密碼")
    
    st.stop()

# === 已登入後的 APP 內容 ===
user_name = st.session_state.login_user_name

# 側邊欄
with st.sidebar:
    if st.button("🚪 登出"):
        st.session_state.logged_in = False
        st.session_state.login_user_name = ""
        st.rerun()
    
    st.divider()
    st.header(f"👤 {user_name}")
    st.divider()
    
    # 個人資料設定
    with st.expander("⚙️ 個人資料設定"):
        profile = get_user_profile(user_name)
        
        gender = st.selectbox("性別", ["男", "女"], index=0 if not profile else (0 if profile["gender"] == "男" else 1))
        age = st.number_input("年齡", min_value=15.0, max_value=120.0, value=float(profile["age"]) if profile else 30.0)
        height = st.number_input("身高 (公分)", min_value=100.0, max_value=250.0, value=float(profile["height"]) if profile else 170.0)
        weight = st.number_input("體重 (公斤)", min_value=30.0, max_value=200.0, value=float(profile["weight"]) if profile else 65.0)
        activity_level = st.selectbox("活動量", [
            "久坐（辦公室工作，幾乎不運動）",
            "輕度活動（每週運動1-3天）",
            "中度活動（每週運動3-5天）",
            "高度活動（每週運動6-7天）",
            "極高度活動（體力勞動或每天訓練兩次）"
        ], index=0 if not profile else [
            "久坐（辦公室工作，幾乎不運動）",
            "輕度活動（每週運動1-3天）",
            "中度活動（每週運動3-5天）",
            "高度活動（每週運動6-7天）",
            "極高度活動（體力勞動或每天訓練兩次）"
        ].index(profile["activity_level"]) if profile else 0)
        
        if st.button("💾 儲存個人資料", type="primary"):
            if save_user_profile(user_name, gender, age, height, weight, activity_level):
                st.success("✅ 已儲存！")
                st.rerun()
        
        if profile or (user_name and age):
            bmr = calculate_bmr(gender, weight, height, age)
            tdee = calculate_tdee(bmr, activity_level)
            goals = get_nutrition_goals(gender, age)
            protein_goal = weight * goals["protein_per_kg"]
            iron_goal = goals["iron_female"] if gender == "女" else goals["iron_male"]
            vitamin_c_goal = goals["vitamin_c"]
            fiber_goal = goals["fiber"]
            calcium_goal = goals["calcium"]
            carbs_goal = goals["carbs"]
            
            st.divider()
            st.metric("🔥 每日熱量", f"{int(tdee)} 大卡")
            st.metric("🥩 蛋白質目標", f"{protein_goal:.0f} 克")
            st.metric("🩸 鐵目標", f"{iron_goal:.0f} 毫克")
            st.metric("🍊 維生素C目標", f"{vitamin_c_goal:.0f} 毫克")
            st.metric("🌾 膳食纖維目標", f"{fiber_goal:.0f} 克")
            st.metric("🦴 鈣目標", f"{calcium_goal:.0f} 毫克")
            st.metric("🍚 碳水化合物目標", f"{carbs_goal:.0f} 克")
            
            st.session_state.protein_goal = protein_goal
            st.session_state.iron_goal = iron_goal
            st.session_state.vitamin_c_goal = vitamin_c_goal
            st.session_state.fiber_goal = fiber_goal
            st.session_state.calcium_goal = calcium_goal
            st.session_state.carbs_goal = carbs_goal
    
    st.divider()
    
    # 隱藏食物管理
    with st.expander("🙈 隱藏不用的食物"):
        st.caption("勾選你想隱藏的食物")
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
                st.subheader("🥘 食物")
                for f in food_items:
                    is_hidden = f["food_id"] in hidden_ids
                    if st.checkbox(f"{f['food_name']}", value=is_hidden, key=f"hide_{f['food_id']}"):
                        if not is_hidden:
                            toggle_hide_food(user_name, f["food_id"], True)
                    else:
                        if is_hidden:
                            toggle_hide_food(user_name, f["food_id"], False)
            with col2:
                st.subheader("🥤 飲品")
                for f in drink_items:
                    is_hidden = f["food_id"] in hidden_ids
                    if st.checkbox(f"{f['food_name']}", value=is_hidden, key=f"hide_{f['food_id']}"):
                        if not is_hidden:
                            toggle_hide_food(user_name, f["food_id"], True)
                    else:
                        if is_hidden:
                            toggle_hide_food(user_name, f["food_id"], False)
            with col3:
                st.subheader("🍪 點心")
                for f in snack_items:
                    is_hidden = f["food_id"] in hidden_ids
                    if st.checkbox(f"{f['food_name']}", value=is_hidden, key=f"hide_{f['food_id']}"):
                        if not is_hidden:
                            toggle_hide_food(user_name, f["food_id"], True)
                    else:
                        if is_hidden:
                            toggle_hide_food(user_name, f["food_id"], False)
            
            if st.button("💾 儲存隱藏設定"):
                st.rerun()
        except Exception as e:
            st.error(f"讀取失敗：{e}")
    
    st.divider()
    
    # USDA 新增食物
       # 自訂食物清單
    with st.expander("📝 自訂你的食物清單"):
        st.caption("搜尋英文食物名稱（資料來源：USDA 美國農業部）")
        search_term = st.text_input("輸入英文食物名稱")
        if st.button("搜尋"):
            if search_term:
                with st.spinner("搜尋中..."):
                    results = search_usda_food(search_term)
                    if results:
                        st.session_state.search_results = results
                    else:
                        st.warning("找不到")
        
        if "search_results" in st.session_state:
            for i, food in enumerate(st.session_state.search_results):
                with st.expander(f"{food['name'][:50]}"):
                    st.write(f"蛋白質: {food['protein']:.1f}g | 鐵: {food['iron']:.1f}mg | 維生素C: {food['vitamin_c']:.1f}mg")
                    st.write(f"膳食纖維: {food['fiber']:.1f}g | 鈣: {food['calcium']:.0f}mg | 碳水化合物: {food['carbs']:.1f}g")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button(f"➕ 食物", key=f"add_food_{i}"):
                            if add_user_food(user_name, food['name'], '食物', food['protein'], food['iron'], food['vitamin_c'], food['calories'], '克', 1.0, food['fiber'], food['calcium'], food['carbs']):
                                st.success(f"已加入：{food['name']}")
                                del st.session_state.search_results
                                st.rerun()
                    with col_b:
                        if st.button(f"🥤 飲品", key=f"add_drink_{i}"):
                            if add_user_food(user_name, food['name'], '飲品', food['protein'], food['iron'], food['vitamin_c'], food['calories'], '杯', 240.0, food['fiber'], food['calcium'], food['carbs']):
                                st.success(f"已加入飲品：{food['name']}")
                                del st.session_state.search_results
                                st.rerun()
                    with col_c:
                        if st.button(f"🍪 點心", key=f"add_snack_{i}"):
                            if add_user_food(user_name, food['name'], '點心', food['protein'], food['iron'], food['vitamin_c'], food['calories'], '克', 1.0, food['fiber'], food['calcium'], food['carbs']):
                                st.success(f"已加入點心：{food['name']}")
                                del st.session_state.search_results
                                st.rerun()
    
    st.divider()
    
    # 記錄飲食
    st.header("➕ 記錄飲食")
    
    log_date = st.date_input("記錄日期", value=st.session_state.log_date, key="log_date_picker")
    st.session_state.log_date = log_date
    
    selected_category = st.radio("分類", ["食物", "蔬果", "點心", "飲品"], horizontal=True)
    
    foods = get_foods(user_name, selected_category)
    
    if foods:
        food_options = {f["food_name"]: f for f in foods}
        selected_food_name = st.selectbox("選擇項目", list(food_options.keys()))
        selected_food = food_options[selected_food_name]
        
        if selected_food["common_unit"] == "克":
            grams = st.number_input("重量 (克)", min_value=1, max_value=2000, value=100)
        else:
            portion = st.number_input(f"份量 ({selected_food['common_unit']})", min_value=0.25, max_value=10.0, value=1.0, step=0.25)
            grams = selected_food["common_gram"] * portion
            st.caption(f"約 {grams:.0f} 克")
        
        meal_type = st.selectbox("餐別", ["早餐", "午餐", "晚餐", "點心"])
        
        if st.button("📝 記錄"):
            if save_meal_log(user_name, log_date, meal_type, selected_food["food_id"], grams):
                st.success(f"✅ 已記錄 {selected_food_name} 到 {log_date}")
                st.session_state.view_date = log_date
                st.rerun()
    else:
        st.info(f"沒有可顯示的{selected_category}")
    
    st.divider()
    
    # 留言板
    with st.expander("💬 回饋與建議"):
        fb_type = st.selectbox("類型", ["🐛 回報 Bug", "💡 功能建議", "📝 一般意見"])
        fb_title = st.text_input("標題", placeholder="簡短描述問題")
        fb_content = st.text_area("詳細內容", height=100, placeholder="請詳細描述...")
        fb_image_url = st.text_input("圖片網址（選填）", placeholder="可貼 Imgur 圖片網址")
        
        if st.button("📨 送出回饋"):
            if fb_title and fb_content:
                if save_feedback(user_name, fb_type, fb_title, fb_content, fb_image_url):
                    st.success("✅ 已送出，感謝你的回饋！")
                    st.rerun()
            else:
                st.warning("請填寫標題和內容")
    
    # 管理留言
    if user_name == "Jessica Sara Lei ENFJ":
        with st.expander("🔧 管理留言（僅限管理員）"):
            feedbacks = get_feedbacks()
            if feedbacks:
                unread_count = len([f for f in feedbacks if not f["is_read"]])
                if unread_count > 0:
                    st.warning(f"📬 有 {unread_count} 則未讀留言")
                
                for fb in feedbacks:
                    with st.container():
                        status = "✅ 已讀" if fb["is_read"] else "🆕 未讀"
                        st.markdown(f"**{fb['feedback_type']}** | {status} | 📅 {fb['created_at'][:16]}")
                        st.markdown(f"**{fb['title']}**")
                        st.caption(f"👤 {fb['user_name'] or '匿名'}")
                        st.write(fb['content'])
                        if fb['image_url']:
                            st.markdown(f"[🔗 查看圖片]({fb['image_url']})")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if not fb["is_read"] and st.button(f"📖 標記已讀", key=f"read_{fb['feedback_id']}"):
                                mark_feedback_read(fb['feedback_id'])
                                st.rerun()
                        with col2:
                            if st.button(f"🗑️ 刪除", key=f"del_{fb['feedback_id']}"):
                                delete_feedback(fb['feedback_id'])
                                st.rerun()
                        st.divider()
            else:
                st.info("目前沒有留言")

# === 主畫面 ===
# 只在手機上顯示的提示
st.markdown("""
<style>
@media screen and (max-width: 768px) {
    .mobile-only {
        display: block;
    }
}
@media screen and (min-width: 769px) {
    .mobile-only {
        display: none;
    }
}
</style>
<div class="mobile-only" style="background-color: #e0f2fe; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 1rem; text-align: center; border-left: 4px solid #0284c7;">
    📱 點擊左上角「☰」或「>」打開側邊欄
</div>
""", unsafe_allow_html=True)

st.header("📊 今日營養統計")

view_date = st.date_input("查詢日期", value=st.session_state.view_date, key="view_date_picker")
st.session_state.view_date = view_date

# 重要：這裡定義 stats 變數
stats = get_today_stats(user_name, view_date)

st.markdown("---")
st.caption(f"👤 使用者：{user_name}")
st.caption(f"🔍 查詢日期：{view_date}")
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
    
    st.subheader("📈 今日攝取量")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🥩 蛋白質", f"{total_protein:.1f} g")
    col2.metric("🩸 鐵", f"{total_iron:.1f} mg")
    col3.metric("🍊 維生素C", f"{total_vitamin_c:.1f} mg")
    
    col4, col5, col6 = st.columns(3)
    col4.metric("🌾 膳食纖維", f"{total_fiber:.1f} g")
    col5.metric("🍬 糖", f"{total_sugar:.1f} g")
    col6.metric("🦴 鈣", f"{total_calcium:.0f} mg")
    
    col7, col8, col9 = st.columns(3)
    col7.metric("🍚 碳水化合物", f"{total_carbs:.1f} g")
    
    if "protein_goal" in st.session_state:
        st.markdown("---")
        st.caption("📌 以下是根據你的個人資料計算的每日攝取目標")
        
        goal_col1, goal_col2, goal_col3, goal_col4 = st.columns(4)
        goal_col1.metric("🥩 蛋白質目標", f"{st.session_state.protein_goal:.0f} 克")
        goal_col2.metric("🩸 鐵目標", f"{st.session_state.iron_goal:.0f} 毫克")
        goal_col3.metric("🍊 維生素C目標", f"{st.session_state.vitamin_c_goal:.0f} 毫克")
        goal_col4.metric("🌾 膳食纖維目標", f"{st.session_state.fiber_goal:.0f} 克")
        
        goal_col5, goal_col6, goal_col7 = st.columns(3)
        goal_col5.metric("🦴 鈣目標", f"{st.session_state.calcium_goal:.0f} 毫克")
        goal_col6.metric("🍚 碳水化合物目標", f"{st.session_state.carbs_goal:.0f} 克")
        
        st.subheader("🎯 今日進度")
        
        prog_col1, prog_col2 = st.columns(2)
        with prog_col1:
            protein_pct = min(100, total_protein / st.session_state.protein_goal * 100)
            st.write(f"🥩 蛋白質：{total_protein:.1f} / {st.session_state.protein_goal:.0f} 克 ({protein_pct:.0f}%)")
            st.progress(protein_pct / 100)
            
            iron_pct = min(100, total_iron / st.session_state.iron_goal * 100)
            st.write(f"🩸 鐵：{total_iron:.1f} / {st.session_state.iron_goal:.0f} 毫克 ({iron_pct:.0f}%)")
            st.progress(iron_pct / 100)
            
            fiber_pct = min(100, total_fiber / st.session_state.fiber_goal * 100)
            st.write(f"🌾 膳食纖維：{total_fiber:.1f} / {st.session_state.fiber_goal:.0f} 克 ({fiber_pct:.0f}%)")
            st.progress(fiber_pct / 100)
        
        with prog_col2:
            vitamin_c_pct = min(100, total_vitamin_c / st.session_state.vitamin_c_goal * 100)
            st.write(f"🍊 維生素C：{total_vitamin_c:.1f} / {st.session_state.vitamin_c_goal:.0f} 毫克 ({vitamin_c_pct:.0f}%)")
            st.progress(vitamin_c_pct / 100)
            
            calcium_pct = min(100, total_calcium / st.session_state.calcium_goal * 100)
            st.write(f"🦴 鈣：{total_calcium:.0f} / {st.session_state.calcium_goal:.0f} 毫克 ({calcium_pct:.0f}%)")
            st.progress(calcium_pct / 100)
            
            carbs_pct = min(100, total_carbs / st.session_state.carbs_goal * 100)
            st.write(f"🍚 碳水化合物：{total_carbs:.1f} / {st.session_state.carbs_goal:.0f} 克 ({carbs_pct:.0f}%)")
            st.progress(carbs_pct / 100)
else:
    st.info(f"📭 {view_date} 還沒有記錄")

# === 免責聲明 ===
st.markdown("---")
st.caption("⚠️ **免責聲明**：本應用程式之營養數據主要來自美國農業部（USDA）FoodData Central 資料庫，僅供參考。")