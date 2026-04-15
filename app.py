import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import date
import os

st.set_page_config(page_title="營養計算器", page_icon="🍎")
st.title("🍎 每日營養計算器")

# === 你的 USDA API Key ===
USDA_API_KEY = "M3DXYo47JeVwPjPI6UVHq9zei9YNPqx6Vtnrhsfh"

# === 初始化 SQLite ===
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
DB_PATH = os.path.join(current_dir, 'nutrition.db')
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 食物表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS foods (
        food_id INTEGER PRIMARY KEY,
        food_name TEXT,
        category TEXT,
        protein_g_per_100g REAL,
        iron_mg_per_100g REAL,
        vitamin_c_mg_per_100g REAL,
        calories_per_100g INTEGER,
        common_unit TEXT,
        common_gram REAL,
        fiber_g_per_100g REAL,
        sugar_g_per_100g REAL,
        calcium_mg_per_100g REAL,
        carbs_g_per_100g REAL,
        vitamin_k_mcg_per_100g REAL,
        vitamin_b_mg_per_100g REAL,
        iodine_ug_per_100g REAL,
        created_by TEXT DEFAULT 'system'
    )
''')

# 隱藏食物記錄表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS hidden_foods (
        user_name TEXT,
        food_id INTEGER,
        PRIMARY KEY (user_name, food_id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS meal_logs (
        log_id INTEGER PRIMARY KEY,
        user_name TEXT,
        log_date TEXT,
        meal_type TEXT,
        food_id INTEGER,
        grams REAL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_profile (
        user_name TEXT PRIMARY KEY,
        gender TEXT,
        age INTEGER,
        height REAL,
        weight REAL,
        activity_level TEXT
    )
''')

# 插入預設食物
cursor.execute("SELECT COUNT(*) FROM foods WHERE created_by = 'system'")
if cursor.fetchone()[0] == 0:
    foods_data = [
        ('雞胸肉', '食物', 31.0, 0.9, 0, 165, '克', 1.0, 0, 0, 11, 0, 0, 0, 0, 'system'),
        ('白飯', '食物', 2.7, 0.2, 0, 130, '碗', 200.0, 0.4, 0, 5, 28, 0, 0.1, 0, 'system'),
        ('綠花椰菜', '食物', 2.8, 0.7, 89.2, 34, '克', 1.0, 2.6, 1.7, 47, 6.6, 101, 0.2, 0, 'system'),
        ('蘋果', '食物', 0.3, 0.1, 4.6, 52, '個', 200.0, 2.4, 10, 6, 14, 2.2, 0.04, 0, 'system'),
        ('雞蛋', '食物', 12.6, 1.2, 0, 155, '個', 55.0, 0, 0.4, 50, 1.1, 0.3, 0.6, 25, 'system'),
        ('牛肉', '食物', 26.0, 2.6, 0, 250, '克', 1.0, 0, 0, 18, 0, 1.5, 0.4, 0, 'system'),
        ('鮭魚', '食物', 20.0, 0.8, 0, 208, '克', 1.0, 0, 0, 12, 0, 0.5, 0.6, 0, 'system'),
        ('吐司', '食物', 8.5, 0.9, 0, 265, '片', 35.0, 2.7, 2.5, 100, 49, 0, 0.2, 0, 'system'),
        ('鯖魚', '食物', 20.8, 1.8, 0, 262, '條', 150.0, 0, 0, 15, 0, 0.5, 0.4, 0, 'system'),
        ('豆腐', '食物', 8.1, 1.5, 0, 76, '盒', 300.0, 1.5, 1, 350, 2, 0, 0.1, 20, 'system'),
        ('雞蛋三文治', '食物', 12.0, 1.5, 2, 250, '份', 150.0, 2, 3, 150, 30, 5, 0.3, 10, 'system'),
        ('藍莓', '食物', 0.7, 0.3, 9.7, 57, '盒', 125.0, 2.4, 10, 6, 14, 19, 0.05, 0, 'system'),
        ('橙', '食物', 0.9, 0.1, 53.2, 47, '個', 150.0, 2.4, 9, 40, 12, 0, 0.06, 0, 'system'),
        ('香蕉', '食物', 1.1, 0.3, 8.7, 89, '根', 120.0, 2.6, 12, 5, 23, 0.5, 0.4, 0, 'system'),
        ('生菜', '食物', 1.4, 0.5, 9.2, 15, '克', 1.0, 1.3, 0.8, 36, 2.9, 126, 0.1, 0, 'system'),
        ('雨衣甘藍', '食物', 4.3, 1.6, 120, 49, '克', 1.0, 3.6, 0.4, 150, 8, 817, 0.2, 0, 'system'),
        ('南瓜', '食物', 1.0, 0.8, 9.0, 26, '克', 1.0, 0.5, 2.8, 21, 6.5, 1.1, 0.1, 0, 'system'),
        ('山葯', '食物', 1.9, 0.5, 17, 67, '克', 1.0, 4.1, 0.7, 17, 16, 2.3, 0.2, 0, 'system'),
        ('紅蘿蔔', '食物', 0.9, 0.3, 5.9, 41, '根', 60.0, 2.8, 4.7, 33, 9.6, 13, 0.1, 0, 'system'),
        ('彩椒', '食物', 1.0, 0.4, 128, 31, '個', 150.0, 1.5, 4.2, 10, 6, 4.9, 0.2, 0, 'system'),
        ('牛油果', '食物', 2.0, 0.6, 10, 160, '個', 150.0, 6.7, 0.7, 12, 8.5, 21, 0.2, 0, 'system'),
        ('青瓜', '食物', 0.7, 0.3, 2.8, 15, '根', 200.0, 0.5, 1.7, 16, 3.6, 16, 0.1, 0, 'system'),
        ('小蕃茄', '食物', 0.9, 0.3, 25, 18, '粒', 15.0, 1.2, 2.5, 10, 3.9, 7, 0.1, 0, 'system'),
        ('堅果（綜合）', '食物', 15.0, 2.5, 0, 600, '克', 1.0, 8.0, 4, 100, 20, 0, 0.3, 0, 'system'),
        ('芝士（起司）', '食物', 25.0, 0.5, 0, 400, '片', 20.0, 0, 0.5, 700, 1.5, 0, 0.2, 30, 'system'),
        ('牛奶', '飲品', 3.3, 0.1, 0, 62, '杯', 240.0, 0, 5, 120, 4.8, 0.3, 0.1, 40, 'system'),
        ('豆漿', '飲品', 3.3, 0.5, 0, 54, '杯', 240.0, 0.5, 4, 25, 6, 0, 0.1, 15, 'system'),
        ('檸檬茶', '飲品', 0.1, 0.1, 2, 35, '杯', 240.0, 0, 9, 5, 8.5, 0, 0, 0, 'system'),
        ('檸檬水', '飲品', 0, 0, 2, 5, '杯', 240.0, 0, 1, 5, 1, 0, 0, 0, 'system'),
        ('黑咖啡', '飲品', 0.1, 0, 0, 1, '杯', 240.0, 0, 0, 4, 0.2, 0, 0, 0, 'system'),
        ('奶啡', '飲品', 0.8, 0, 0, 20, '杯', 240.0, 0, 2, 50, 2, 0, 0.1, 10, 'system'),
        ('奶茶', '飲品', 0.5, 0, 0, 30, '杯', 240.0, 0, 7, 40, 6, 0, 0.1, 8, 'system'),
        ('抹茶', '飲品', 0.3, 0.1, 2, 10, '杯', 240.0, 0.5, 0, 10, 2, 0, 0.2, 5, 'system'),
        ('紅茶', '飲品', 0, 0, 0, 1, '杯', 240.0, 0, 0, 4, 0.2, 0, 0, 0, 'system'),
        ('綠茶', '飲品', 0, 0, 0, 1, '杯', 240.0, 0, 0, 4, 0.2, 0, 0, 0, 'system'),
    ]
    cursor.executemany('''
        INSERT INTO foods (food_name, category, protein_g_per_100g, iron_mg_per_100g, vitamin_c_mg_per_100g,
                          calories_per_100g, common_unit, common_gram, fiber_g_per_100g, sugar_g_per_100g,
                          calcium_mg_per_100g, carbs_g_per_100g, vitamin_k_mcg_per_100g, vitamin_b_mg_per_100g,
                          iodine_ug_per_100g, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', foods_data)
    conn.commit()

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
    return {
        "protein_per_kg": 1.1,
        "iron_male": 10,
        "iron_female": 15,
        "vitamin_c": 100,
        "fiber": 25,
        "calcium": 1000,
        "carbs": 250,
    }

def search_usda_food(query):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "api_key": USDA_API_KEY,
        "query": query,
        "pageSize": 3
    }
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
                "calories": nutrients.get("Energy", 0)
            })
        return results
    except Exception as e:
        st.error(f"搜尋失敗：{e}")
        return []

# === 側邊欄 ===
with st.sidebar:
    st.header("👤 使用者")
    
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    
    user_name = st.text_input("你的名字", value=st.session_state.user_name)
    if user_name:
        st.session_state.user_name = user_name
    
    st.divider()
    
    # 個人資料設定
    with st.expander("⚙️ 個人資料設定"):
        if st.session_state.user_name:
            cursor.execute("SELECT * FROM user_profile WHERE user_name = ?", (st.session_state.user_name,))
            profile = cursor.fetchone()
            
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
            ], index=0 if not profile else 0)
            
            # 儲存按鈕（會變色 + 文字改變）
            if "save_clicked" not in st.session_state:
                st.session_state.save_clicked = False
            
            if st.button("💾 儲存個人資料", type="primary" if not st.session_state.save_clicked else "secondary"):
                cursor.execute('''
                    INSERT OR REPLACE INTO user_profile (user_name, gender, age, height, weight, activity_level)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (st.session_state.user_name, gender, int(age), height, weight, activity_level))
                conn.commit()
                st.session_state.save_clicked = True
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
        else:
            st.info("請先輸入名字")
    
    st.divider()
    
    # 隱藏食物管理
    if st.session_state.user_name:
        with st.expander("🙈 隱藏不用的食物"):
            st.caption("勾選你想隱藏的食物（不會刪除，只是不顯示）")
            
            cursor.execute("SELECT food_id, food_name, category FROM foods WHERE created_by = 'system' ORDER BY category, food_name")
            all_system_foods = cursor.fetchall()
            
            cursor.execute("SELECT food_id FROM hidden_foods WHERE user_name = ?", (st.session_state.user_name,))
            hidden_ids = set([row["food_id"] for row in cursor.fetchall()])
            
            col1, col2 = st.columns(2)
            food_items = [f for f in all_system_foods if f["category"] == "食物"]
            drink_items = [f for f in all_system_foods if f["category"] == "飲品"]
            
            with col1:
                st.subheader("🥘 食物")
                for f in food_items:
                    is_hidden = f["food_id"] in hidden_ids
                    if st.checkbox(f"{f['food_name']}", value=is_hidden, key=f"hide_{f['food_id']}"):
                        if not is_hidden:
                            cursor.execute("INSERT INTO hidden_foods (user_name, food_id) VALUES (?, ?)", (st.session_state.user_name, f["food_id"]))
                    else:
                        if is_hidden:
                            cursor.execute("DELETE FROM hidden_foods WHERE user_name = ? AND food_id = ?", (st.session_state.user_name, f["food_id"]))
            
            with col2:
                st.subheader("🥤 飲品")
                for f in drink_items:
                    is_hidden = f["food_id"] in hidden_ids
                    if st.checkbox(f"{f['food_name']}", value=is_hidden, key=f"hide_{f['food_id']}"):
                        if not is_hidden:
                            cursor.execute("INSERT INTO hidden_foods (user_name, food_id) VALUES (?, ?)", (st.session_state.user_name, f["food_id"]))
                    else:
                        if is_hidden:
                            cursor.execute("DELETE FROM hidden_foods WHERE user_name = ? AND food_id = ?", (st.session_state.user_name, f["food_id"]))
            
            if st.button("💾 儲存隱藏設定"):
                conn.commit()
                st.success("已儲存")
                st.rerun()
    
    st.divider()
    
    # USDA 新增食物（移到隱藏食物上面）
    if st.session_state.user_name:
        with st.expander("🔍 從 USDA 新增食物"):
            st.caption("搜尋英文食物名稱，可選擇加入「食物」或「飲品」")
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
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"➕ 加入食物", key=f"add_food_{i}"):
                                cursor.execute('''
                                    INSERT INTO foods (food_name, category, protein_g_per_100g, iron_mg_per_100g, vitamin_c_mg_per_100g,
                                                      calories_per_100g, common_unit, common_gram, created_by)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (food['name'], '食物', food['protein'], food['iron'], food['vitamin_c'], food['calories'], '克', 1.0, st.session_state.user_name))
                                conn.commit()
                                st.success(f"已加入：{food['name']}")
                                del st.session_state.search_results
                                st.rerun()
                        with col_b:
                            if st.button(f"➕ 加入飲品", key=f"add_drink_{i}"):
                                cursor.execute('''
                                    INSERT INTO foods (food_name, category, protein_g_per_100g, iron_mg_per_100g, vitamin_c_mg_per_100g,
                                                      calories_per_100g, common_unit, common_gram, created_by)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (food['name'], '飲品', food['protein'], food['iron'], food['vitamin_c'], food['calories'], '杯', 240.0, st.session_state.user_name))
                                conn.commit()
                                st.success(f"已加入飲品：{food['name']}")
                                del st.session_state.search_results
                                st.rerun()
    
    st.divider()
    
    # 記錄飲食
    st.header("➕ 記錄飲食")
    if not st.session_state.user_name:
        st.warning("⚠️ 請先輸入名字")
    else:
        log_date = st.date_input("日期", date.today())
        selected_category = st.radio("分類", ["食物", "飲品"], horizontal=True)
        
        cursor.execute("""
            SELECT f.food_id, f.food_name, f.common_unit, f.common_gram 
            FROM foods f
            WHERE (f.created_by = 'system' OR f.created_by = ?) 
              AND f.category = ?
              AND f.food_id NOT IN (SELECT food_id FROM hidden_foods WHERE user_name = ?)
            ORDER BY f.food_name
        """, (st.session_state.user_name, selected_category, st.session_state.user_name))
        foods = cursor.fetchall()
        
        if foods:
            food_options = {f["food_name"]: {"id": f["food_id"], "unit": f["common_unit"], "gram": f["common_gram"]} for f in foods}
            selected_food_name = st.selectbox("選擇項目", list(food_options.keys()))
            selected_food = food_options[selected_food_name]
            
            if selected_food["unit"] == "克":
                grams = st.number_input("重量 (克)", min_value=1, max_value=2000, value=100)
            else:
                portion = st.number_input(f"份量 ({selected_food['unit']})", min_value=0.25, max_value=10.0, value=1.0, step=0.25)
                grams = selected_food["gram"] * portion
                st.caption(f"約 {grams:.0f} 克")
            
            meal_type = st.selectbox("餐別", ["早餐", "午餐", "晚餐", "點心"])
            if st.button("📝 記錄"):
                cursor.execute('''
                    INSERT INTO meal_logs (user_name, log_date, meal_type, food_id, grams)
                    VALUES (?, ?, ?, ?, ?)
                ''', (st.session_state.user_name, log_date.strftime("%Y-%m-%d"), meal_type, selected_food["id"], grams))
                conn.commit()
                st.success(f"✅ 已記錄 {selected_food_name}")
                st.rerun()
        else:
            st.info(f"沒有可顯示的{selected_category}，請檢查隱藏設定")

# === 主畫面 ===
st.header("📊 今日營養統計")

if not st.session_state.user_name:
    st.info("👈 請輸入名字開始")
else:
    view_date = st.date_input("查詢日期", date.today())
    
    cursor.execute('''
        SELECT 
            f.food_name,
            f.category,
            SUM(m.grams) as total_grams,
            SUM(f.protein_g_per_100g * m.grams / 100) as protein,
            SUM(f.iron_mg_per_100g * m.grams / 100) as iron,
            SUM(f.vitamin_c_mg_per_100g * m.grams / 100) as vitamin_c,
            SUM(f.fiber_g_per_100g * m.grams / 100) as fiber,
            SUM(f.sugar_g_per_100g * m.grams / 100) as sugar,
            SUM(f.calcium_mg_per_100g * m.grams / 100) as calcium,
            SUM(f.carbs_g_per_100g * m.grams / 100) as carbs
        FROM meal_logs m
        JOIN foods f ON m.food_id = f.food_id
        WHERE m.user_name = ? AND m.log_date = ?
        GROUP BY f.food_name
    ''', (st.session_state.user_name, view_date.strftime("%Y-%m-%d")))
    today_data = cursor.fetchall()
    
    st.caption(f"👤 {st.session_state.user_name} | 📅 {view_date}")
    
    if today_data:
        df = pd.DataFrame([dict(row) for row in today_data])
        st.dataframe(df, use_container_width=True)
        
        total_protein = df["protein"].sum()
        total_iron = df["iron"].sum()
        total_vitamin_c = df["vitamin_c"].sum()
        total_fiber = df["fiber"].sum()
        total_sugar = df["sugar"].sum()
        total_calcium = df["calcium"].sum()
        total_carbs = df["carbs"].sum()
        
        # 今日攝取量（包含新增項目）
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
        
        # 個人目標顯示
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
            
            # 進度條
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
st.caption("⚠️ **免責聲明**：本應用程式之營養數據主要來自美國農業部（USDA）FoodData Central 資料庫，僅供參考與教育用途。")
st.caption("📌 個人的營養需求可能因年齡、性別、活動量、健康狀況而異，建議諮詢專業營養師或醫師。")
st.caption("📌 開發者不對使用本應用程式所做的任何飲食決策承擔責任。")

conn.close()