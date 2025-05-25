import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
import io

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

# --------- SQLite Data Integration ----------
DB_PATH_MAIN = "agriconnect.db"
DB_PATH_FARMERS = "agriconnect_farmers.db"

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

def populate_sample_farmer():
    conn = sqlite3.connect(DB_PATH_FARMERS)
    c = conn.cursor()
    username, password = "testfarmer", "test123"
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    c.execute("SELECT user_id FROM users WHERE username=?", (username,))
    user_id = c.fetchone()[0]
    c.execute("INSERT OR IGNORE INTO facilities (user_id, name, location) VALUES (?, ?, ?)",
              (user_id, "Test Storage A", "Kano"))
    conn.commit()
    c.execute("SELECT facility_id FROM facilities WHERE user_id=? AND name=?", (user_id, "Test Storage A"))
    facility_id = c.fetchone()[0]
    c.execute("INSERT OR IGNORE INTO crops (facility_id, crop_name, quantity) VALUES (?, ?, ?)",
              (facility_id, "Maize", 10))
    c.execute("INSERT OR IGNORE INTO crops (facility_id, crop_name, quantity) VALUES (?, ?, ?)",
              (facility_id, "Rice", 5))
    conn.commit()
    now = datetime.now()
    temp_data = [
        (facility_id, 28, (now - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S")),
        (facility_id, 26, (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")),
        (facility_id, 29, (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")),
        (facility_id, 27, (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")),
        (facility_id, 24, (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
        (facility_id, 25, (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
        (facility_id, 30, now.strftime("%Y-%m-%d %H:%M:%S")),
    ]
    for entry in temp_data:
        c.execute("INSERT INTO temp_logs (facility_id, temperature, log_time) VALUES (?, ?, ?)", entry)
    conn.commit()
    conn.close()

# --------- SIDEBAR NAVIGATION ----------
init_farmer_db()
with st.sidebar:
    st.markdown('<div class="sidebar-content"><h2>🌾 AgriConnect</h2><p style="font-size: 1.1rem;">Smart Credit & PHL Risk Insights</p></div>', unsafe_allow_html=True)
    nav_opt = st.radio("Navigation", ["Analytics Dashboard", "Farmer Portal"])
    if st.button("Populate sample farmer data (test/demo)"):
        populate_sample_farmer()
        st.success("Sample farmer account and data created!\nUsername: testfarmer\nPassword: test123")
    st.markdown("---")
    st.header("🔎 Filters")

# --------- MAIN APP ---------
if nav_opt == "Analytics Dashboard":
    # (Your dashboard code unchanged. Paste your full dashboard code here, starting from your DB loads, filters, metrics, and tabs...)

    # --------- LOAD DATA FROM SQLITE ---------
    try:
        df = get_data()
        regions = df['region'].dropna().unique().tolist()
        min_score = float(df['predicted_credit_score'].min())
        max_score = float(df['predicted_credit_score'].max())
        interventions = df['interventions_adopted'].dropna().unique().tolist()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()
    selected_regions = st.sidebar.multiselect("Region", options=regions, default=regions)
    credit_range = st.sidebar.slider("Credit Score", min_value=min_score, max_value=max_score, value=(min_score, max_score))
    selected_interventions = st.sidebar.multiselect("Interventions", options=interventions, default=interventions)
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2025 AgriConnect")

    # ... (Paste the rest of your dashboard code, unchanged, here!)

    # For brevity, please see your original code block above for all tabs, metrics, and insight cards.
    # The dashboard will work as before.

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