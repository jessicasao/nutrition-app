import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import date
import os

st.set_page_config(page_title="營養計算器", page_icon="🍎")
st.title("🍎 每日營養計算器")
st.write("記錄你吃了什麼，自動計算蛋白質、鐵、維生素C")

# === 你的 USDA API Key ===
USDA_API_KEY = "M3DXYo47JeVwPjPI6UVHq9zei9YNPqx6Vtnrhsfh"  # ⚠️ 改成你的 Key

# === 初始化 SQLite ===
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
DB_PATH = os.path.join(current_dir, 'nutrition.db')
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 建立資料表（加入使用者欄位）
cursor.execute('''
    CREATE TABLE IF NOT EXISTS foods (
        food_id INTEGER PRIMARY KEY,
        food_name TEXT,
        protein_g_per_100g REAL,
        iron_mg_per_100g REAL,
        vitamin_c_mg_per_100g REAL,
        calories_per_100g INTEGER
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

# 插入預設食物（如果資料庫是空的）
cursor.execute("SELECT COUNT(*) FROM foods")
if cursor.fetchone()[0] == 0:
    foods_data = [
        ('雞胸肉', 31.0, 0.9, 0, 165),
        ('白飯', 2.7, 0.2, 0, 130),
        ('綠花椰菜', 2.8, 0.7, 89.2, 34),
        ('蘋果', 0.3, 0.1, 4.6, 52),
        ('雞蛋', 12.6, 1.2, 0, 155),
        ('牛肉', 26.0, 2.6, 0, 250),
        ('鮭魚', 20.0, 0.8, 0, 208),
    ]
    cursor.executemany('''
        INSERT INTO foods (food_name, protein_g_per_100g, iron_mg_per_100g, vitamin_c_mg_per_100g, calories_per_100g)
        VALUES (?, ?, ?, ?, ?)
    ''', foods_data)
    conn.commit()

# === 搜尋 USDA 食物 ===
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

# === 側邊欄：使用者名稱 ===
with st.sidebar:
    st.header("👤 使用者")
    
    # 使用者名稱輸入
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    
    user_name = st.text_input("你的名字", value=st.session_state.user_name)
    if user_name:
        st.session_state.user_name = user_name
    
    st.divider()
    
    st.header("➕ 記錄飲食")
    
    # 只有輸入名字才能記錄
    if not st.session_state.user_name:
        st.warning("⚠️ 請先在上方輸入你的名字")
    else:
        log_date = st.date_input("日期", date.today())
        
        tab1, tab2 = st.tabs(["📋 我的食物", "🔍 搜尋新食物"])
        
        with tab1:
            cursor.execute("SELECT food_id, food_name FROM foods")
            foods = cursor.fetchall()
            food_options = {f["food_name"]: f["food_id"] for f in foods}
            selected_food = st.selectbox("選擇食物", list(food_options.keys()))
            grams = st.number_input("重量 (克)", min_value=1, max_value=2000, value=100, key="grams1")
            meal_type = st.selectbox("餐別", ["早餐", "午餐", "晚餐", "點心"])
            
            if st.button("📝 記錄", key="record_btn"):
                food_id = food_options[selected_food]
                cursor.execute('''
                    INSERT INTO meal_logs (user_name, log_date, meal_type, food_id, grams)
                    VALUES (?, ?, ?, ?, ?)
                ''', (st.session_state.user_name, log_date.strftime("%Y-%m-%d"), meal_type, food_id, grams))
                conn.commit()
                st.success(f"✅ 已記錄 {selected_food} {grams}g")
                st.rerun()
        
        with tab2:
            search_term = st.text_input("輸入食物名稱（英文）")
            if st.button("🔍 搜尋"):
                if search_term:
                    with st.spinner("搜尋中..."):
                        results = search_usda_food(search_term)
                        if results:
                            st.session_state.search_results = results
                        else:
                            st.warning("找不到結果，請試試其他關鍵字")
            
            if "search_results" in st.session_state:
                for i, food in enumerate(st.session_state.search_results):
                    with st.expander(f"{food['name'][:50]}..."):
                        st.write(f"🥩 蛋白質: {food['protein']:.1f}g / 100g")
                        st.write(f"🩸 鐵: {food['iron']:.1f}mg / 100g")
                        st.write(f"🍊 維生素C: {food['vitamin_c']:.1f}mg / 100g")
                        st.write(f"🔥 熱量: {food['calories']:.0f} kcal / 100g")
                        
                        if st.button(f"➕ 加入我的食物", key=f"add_{i}"):
                            cursor.execute('''
                                INSERT INTO foods (food_name, protein_g_per_100g, iron_mg_per_100g, vitamin_c_mg_per_100g, calories_per_100g)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (food['name'], food['protein'], food['iron'], food['vitamin_c'], food['calories']))
                            conn.commit()
                            st.success(f"已加入：{food['name']}")
                            del st.session_state.search_results
                            st.rerun()

# === 主畫面：今日統計（根據使用者和日期）===
st.header(f"📊 營養統計")

if not st.session_state.user_name:
    st.info("👈 請在左側輸入你的名字開始使用")
else:
    # 讓使用者選擇要查詢的日期
    view_date = st.date_input("查詢日期", date.today())
    
    cursor.execute('''
        SELECT 
            f.food_name,
            SUM(m.grams) as total_grams,
            SUM(f.protein_g_per_100g * m.grams / 100) as protein,
            SUM(f.iron_mg_per_100g * m.grams / 100) as iron,
            SUM(f.vitamin_c_mg_per_100g * m.grams / 100) as vitamin_c
        FROM meal_logs m
        JOIN foods f ON m.food_id = f.food_id
        WHERE m.user_name = ? AND m.log_date = ?
        GROUP BY f.food_name
    ''', (st.session_state.user_name, view_date.strftime("%Y-%m-%d")))
    today_data = cursor.fetchall()
    
    st.caption(f"👤 使用者：{st.session_state.user_name} | 📅 日期：{view_date}")
    
    if today_data:
        df = pd.DataFrame([dict(row) for row in today_data])
        st.dataframe(df, use_container_width=True)
        
        total_protein = df["protein"].sum()
        total_iron = df["iron"].sum()
        total_vitamin_c = df["vitamin_c"].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🥩 蛋白質", f"{total_protein:.1f} g")
        col2.metric("🩸 鐵", f"{total_iron:.1f} mg")
        col3.metric("🍊 維生素C", f"{total_vitamin_c:.1f} mg")
        
        # 簡單目標提示（可自訂）
        st.caption("💡 參考目標：蛋白質 60g/天、鐵 10mg/天、維生素C 100mg/天")
    else:
        st.info(f"📭 {view_date} 還沒有記錄，從左側選單開始吧！")

conn.close()
