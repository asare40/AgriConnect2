import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
import io
import os

st.set_page_config(page_title="AgriConnect Dashboard", layout="wide")

# ---- Insight Card Function ----
def insight_card(title, insight_text, color="#e3f2fd"):
    st.markdown(
        f"""
        <div style="background: {color}; border-radius: 8px; padding: 1rem; margin: 1rem 0 1.5rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
            <strong style="font-size:1.1rem;">{title}</strong>
            <div style="font-size:1rem; color: #333;">
                {insight_text}
            </div>
        </div>
        """, unsafe_allow_html=True
    )

DB_PATH_MAIN = "agriconnect.db"
DB_PATH_FARMERS = "agriconnect_farmers.db"
WEATHER_FILE = "weather_kano.csv"

def get_data(query="SELECT * FROM farmers"):
    conn = sqlite3.connect(DB_PATH_MAIN)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --------- Farmer Portal DB Functions ----------
def init_farmer_db():
    conn = sqlite3.connect(DB_PATH_FARMERS)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS facilities (
            facility_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            location TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS crops (
            crop_id INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_id INTEGER,
            crop_name TEXT,
            quantity REAL,
            FOREIGN KEY(facility_id) REFERENCES facilities(facility_id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS temp_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_id INTEGER,
            temperature REAL,
            log_time TEXT,
            FOREIGN KEY(facility_id) REFERENCES facilities(facility_id)
        )
    """)
    conn.commit()
    conn.close()

def get_user(username, password=None):
    conn = sqlite3.connect(DB_PATH_FARMERS)
    c = conn.cursor()
    if password:
        c.execute("SELECT user_id, username FROM users WHERE username=? AND password=?", (username, password))
    else:
        c.execute("SELECT user_id, username FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(username, password):
    conn = sqlite3.connect(DB_PATH_FARMERS)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_facilities(user_id):
    conn = sqlite3.connect(DB_PATH_FARMERS)
    df = pd.read_sql_query("SELECT * FROM facilities WHERE user_id=?", conn, params=(user_id,))
    conn.close()
    return df

def add_facility(user_id, name, location):
    conn = sqlite3.connect(DB_PATH_FARMERS)
    c = conn.cursor()
    c.execute("INSERT INTO facilities (user_id, name, location) VALUES (?, ?, ?)", (user_id, name, location))
    conn.commit()
    conn.close()

def get_crops(facility_id):
    conn = sqlite3.connect(DB_PATH_FARMERS)
    df = pd.read_sql_query("SELECT * FROM crops WHERE facility_id=?", conn, params=(facility_id,))
    conn.close()
    return df

def add_crop(facility_id, crop_name, quantity):
    conn = sqlite3.connect(DB_PATH_FARMERS)
    c = conn.cursor()
    c.execute("INSERT INTO crops (facility_id, crop_name, quantity) VALUES (?, ?, ?)", (facility_id, crop_name, quantity))
    conn.commit()
    conn.close()

def get_temp_logs(facility_id, limit=20):
    conn = sqlite3.connect(DB_PATH_FARMERS)
    df = pd.read_sql_query(
        "SELECT * FROM temp_logs WHERE facility_id=? ORDER BY log_time DESC LIMIT ?",
        conn, params=(facility_id, limit)
    )
    conn.close()
    return df

def add_temp_log(facility_id, temperature):
    conn = sqlite3.connect(DB_PATH_FARMERS)
    c = conn.cursor()
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO temp_logs (facility_id, temperature, log_time) VALUES (?, ?, ?)", (facility_id, temperature, log_time))
    conn.commit()
    conn.close()

CROP_TEMP_THRESHOLDS = {
    "maize": 27, "rice": 25, "cassava": 25, "wheat": 26, "yam": 24, "other": 26
}
def phl_prompt(crop_name, temp):
    thresh = CROP_TEMP_THRESHOLDS.get(crop_name.lower(), CROP_TEMP_THRESHOLDS["other"])
    if temp > thresh:
        return f"⚠️ Storage temperature ({temp}°C) is too high for {crop_name.title()}! Reduce temperature to below {thresh}°C to prevent post-harvest losses."
    return f"✅ Temperature is safe for {crop_name.title()}."

def populate_farmer_with_full_crop_and_temps():
    conn = sqlite3.connect(DB_PATH_FARMERS)
    c = conn.cursor()
    username, password = "demo_farmer", "securepass"
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    c.execute("SELECT user_id FROM users WHERE username=?", (username,))
    user_id = c.fetchone()[0]
    c.execute("INSERT OR IGNORE INTO facilities (user_id, name, location) VALUES (?, ?, ?)", (user_id, "Demo Storage", "Kano"))
    conn.commit()
    c.execute("SELECT facility_id FROM facilities WHERE user_id=? AND name=?", (user_id, "Demo Storage"))
    facility_id = c.fetchone()[0]
    c.execute("INSERT OR IGNORE INTO crops (facility_id, crop_name, quantity) VALUES (?, ?, ?)", (facility_id, "Maize", 25))
    conn.commit()
    # Add 7 days of temperature logs
    now = datetime.now()
    for i in range(7):
        temp = 25 + (i % 4)  # Simulate a temp curve
        log_time = (now - timedelta(days=6-i)).strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO temp_logs (facility_id, temperature, log_time) VALUES (?, ?, ?)", (facility_id, temp, log_time))
    conn.commit()
    conn.close()
    print("demo_farmer with crop and temperature logs populated.")

def prepare_sample_weather_csv():
    # If already exists, don't overwrite
    if os.path.exists(WEATHER_FILE):
        return
    today = datetime.now().date()
    days = [today - timedelta(days=6-i) for i in range(7)]
    temp = [32, 31, 33, 30, 29, 28, 31]
    humidity = [65, 68, 64, 70, 73, 71, 67]
    df = pd.DataFrame({
        "date": [str(d) for d in days],
        "temperature": temp,
        "humidity": humidity
    })
    df.to_csv(WEATHER_FILE, index=False)

# --------- SIDEBAR NAVIGATION AND BRANDING ----------
init_farmer_db()
with st.sidebar:
    st.markdown('<div class="sidebar-content"><h2>🌾 AgriConnect</h2><p style="font-size: 1.1rem;">Smart Credit & PHL Risk Insights</p></div>', unsafe_allow_html=True)
    nav_opt = st.radio("Navigation", ["Analytics Dashboard", "Farmer Portal"])
    if st.button("Populate full demo farmer + weather"):
        populate_farmer_with_full_crop_and_temps()
        prepare_sample_weather_csv()
        st.success("Demo farmer, crop, temperature logs, and sample weather file created!\nUsername: demo_farmer\nPassword: securepass")
    st.markdown("---")
    st.caption("© 2025 AgriConnect")

# --------- MAIN APP ---------
if nav_opt == "Analytics Dashboard":
    # --------- LOAD DATA FROM SQLITE ---------
    try:
        df = get_data()
        if df.empty or any([col not in df.columns for col in ("region", "predicted_credit_score", "interventions_adopted")]):
            st.warning("No farmer data available or required columns missing.")
            st.stop()
        regions = df['region'].dropna().unique().tolist()
        min_score = float(df['predicted_credit_score'].min())
        max_score = float(df['predicted_credit_score'].max())
        interventions = df['interventions_adopted'].dropna().unique().tolist()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

    # --------- SIDEBAR FILTER WIDGETS (ONLY IN THIS BLOCK) ---------
    with st.sidebar:
        st.header("🔎 Filters")
        selected_regions = st.multiselect("Region", options=regions, default=regions, key="region_analytics")
        credit_range = st.slider("Credit Score", min_value=min_score, max_value=max_score, value=(min_score, max_score), key="credit_analytics")
        selected_interventions = st.multiselect("Interventions", options=interventions, default=interventions, key="intv_analytics")
        st.markdown("---")

    # --------- FILTER DATA ---------
    filtered_df = df[
        df['region'].isin(selected_regions) &
        df['predicted_credit_score'].between(*credit_range) &
        df['interventions_adopted'].isin(selected_interventions)
    ]

    if filtered_df.empty:
        st.info("No data matches your filter selection.")
        st.stop()

    # --------- HEADER & METRICS ----------
    st.markdown("""
        <h1 style='font-family:Montserrat,sans-serif; font-weight:700;'>📊 AgriConnect Credit & PHL Analytics</h1>
        <span style='font-size:1.2rem;color:#388e3c;'>Empowering smart lending & minimizing post-harvest losses</span>
    """, unsafe_allow_html=True)

    metric1, metric2, metric3 = st.columns(3)
    with metric1:
        st.markdown(f"<div class='metric-card'><h2>{len(filtered_df):,}</h2><div>Total Farmers</div></div>", unsafe_allow_html=True)
    with metric2:
        avg_credit = filtered_df['predicted_credit_score'].mean() if not filtered_df.empty else 0
        st.markdown(f"<div class='metric-card'><h2>{avg_credit:.2f}</h2><div>Avg Credit Score</div></div>", unsafe_allow_html=True)
    with metric3:
        avg_phl = filtered_df['phl_risk_score'].mean() if not filtered_df.empty else 0
        st.markdown(f"<div class='metric-card'><h2>{avg_phl:.2f}</h2><div>Avg PHL Risk</div></div>", unsafe_allow_html=True)

    # --------- TABS ----------
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "Overview Map", "Analytics", "Profiles", "Table",
        "Leaderboards", "Intervention", "Correlations/Download",
        "Distributions", "Advanced"
    ])

    # ... (Tabs code unchanged; see previous message for full code for each tab.)

    # For brevity, you can copy from your previously provided code for each tab.

else:
    # --------- FARMER PORTAL ---------
    if "user" not in st.session_state:
        st.session_state["user"] = None

    def login_page():
        st.header("👤 Farmer Login / Register")
        login_tab, reg_tab = st.tabs(["Login", "Register"])
        with login_tab:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                user = get_user(username, password)
                if user:
                    st.session_state["user"] = {"user_id": user[0], "username": user[1]}
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        with reg_tab:
            new_username = st.text_input("Choose username", key="reg_user")
            new_password = st.text_input("Choose password", type="password", key="reg_pass")
            if st.button("Register"):
                if add_user(new_username, new_password):
                    st.success("Registration successful! Please log in.")
                else:
                    st.error("Username already exists.")

    def main_dashboard():
        st.sidebar.markdown(f"Hello, **{st.session_state['user']['username']}**!")
        if st.sidebar.button("Logout"):
            st.session_state["user"] = None
            st.rerun()

        tabs = st.tabs(["My Facilities", "Add Facility", "Monitor Storage", "PHL Prompts"])
        # ---- Facilities ----
        with tabs[0]:
            st.subheader("My Storage Facilities")
            fdf = get_facilities(st.session_state["user"]["user_id"])
            if len(fdf):
                st.dataframe(fdf[["facility_id", "name", "location"]])
            else:
                st.info("No facilities yet. Add one in 'Add Facility' tab.")

        # ---- Add Facility ----
        with tabs[1]:
            st.subheader("Add New Storage Facility")
            fac_name = st.text_input("Facility Name")
            fac_location = st.text_input("Location")
            if st.button("Add Facility"):
                if fac_name and fac_location:
                    add_facility(st.session_state["user"]["user_id"], fac_name, fac_location)
                    st.success("Facility added!")
                    st.rerun()
                else:
                    st.warning("Fill all fields.")

        # ---- Monitor Storage ----
        with tabs[2]:
            st.subheader("Monitor Storage Facility")
            fdf = get_facilities(st.session_state["user"]["user_id"])
            if len(fdf):
                fac_options = {f"{row['name']} ({row['location']})": row["facility_id"] for i, row in fdf.iterrows()}
                selected_fac = st.selectbox("Select Facility", list(fac_options.keys()))
                fac_id = fac_options[selected_fac]
                st.markdown(f"**Facility:** {selected_fac}")

                # List crops
                st.markdown("#### Crops in This Facility")
                cdf = get_crops(fac_id)
                if len(cdf):
                    st.dataframe(cdf[["crop_name", "quantity"]])
                else:
                    st.info("No crops yet. Add below.")

                # Add crop
                with st.expander("Add Crop to Facility"):
                    crop_name = st.text_input("Crop Name")
                    crop_qty = st.number_input("Quantity (tons)", min_value=0.0)
                    if st.button("Add Crop"):
                        if crop_name:
                            add_crop(fac_id, crop_name, crop_qty)
                            st.success("Crop added!")
                            st.rerun()
                        else:
                            st.warning("Enter a crop name.")

                # Add temp log
                st.markdown("#### Storage Temperature Log")
                temp = st.number_input("Record Temperature (°C)", min_value=0.0)
                if st.button("Log Temperature"):
                    add_temp_log(fac_id, temp)
                    st.success("Temperature logged!")
                    st.rerun()

                # Show logs
                tdf = get_temp_logs(fac_id)
                if len(tdf):
                    st.line_chart(tdf.sort_values("log_time")["temperature"], use_container_width=True)
                    st.dataframe(tdf[["temperature", "log_time"]])
                else:
                    st.info("No temperature logs yet.")

                # --- Weather Integration ---
                st.subheader("Storage vs. Weather Temperature (Kano)")
                # Prepare weather file if not exists
                prepare_sample_weather_csv()
                if os.path.exists(WEATHER_FILE):
                    weather_df = pd.read_csv(WEATHER_FILE, parse_dates=["date"])
                    if not tdf.empty and not weather_df.empty:
                        tdf['date_only'] = pd.to_datetime(tdf['log_time']).dt.date
                        weather_df['date_only'] = pd.to_datetime(weather_df['date']).dt.date
                        merged = pd.merge(
                            tdf[['date_only', 'temperature']].rename(columns={'temperature':'Storage Temp'}),
                            weather_df[['date_only', 'temperature']].rename(columns={'temperature':'Weather Temp'}),
                            on="date_only", how="inner"
                        )
                        if len(merged):
                            st.line_chart(merged.set_index("date_only"))
                            st.dataframe(merged)
                        else:
                            st.info("No overlapping dates between storage logs and weather data.")
                    else:
                        st.info("Insufficient data for weather comparison.")
                else:
                    st.info("Weather file not found.")

            else:
                st.info("Add a storage facility first.")

        # ---- PHL Prompts ----
        with tabs[3]:
            st.subheader("PHL Reduction Prompts")
            fdf = get_facilities(st.session_state["user"]["user_id"])
            if len(fdf):
                for i, row in fdf.iterrows():
                    st.markdown(f"### Facility: {row['name']} ({row['location']})")
                    cdf = get_crops(row["facility_id"])
                    tdf = get_temp_logs(row["facility_id"], limit=1)
                    if len(cdf) and len(tdf):
                        last_temp = tdf.iloc[0]["temperature"]
                        for _, crop in cdf.iterrows():
                            prompt = phl_prompt(crop["crop_name"], last_temp)
                            st.info(f"{crop['crop_name'].title()}: {prompt}")
                    elif len(cdf):
                        st.warning("No temperature logs yet.")
                    else:
                        st.warning("No crops in this facility.")
            else:
                st.info("Add a storage facility first.")

    if st.session_state["user"]:
        main_dashboard()
    else:
        login_page()