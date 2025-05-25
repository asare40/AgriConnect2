import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="AgriConnect Farmer Portal", layout="wide")

DB_PATH = "agriconnect_farmers.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if password:
        c.execute("SELECT user_id, username FROM users WHERE username=? AND password=?", (username, password))
    else:
        c.execute("SELECT user_id, username FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(username, password):
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM facilities WHERE user_id=?", conn, params=(user_id,))
    conn.close()
    return df

def add_facility(user_id, name, location):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO facilities (user_id, name, location) VALUES (?, ?, ?)", (user_id, name, location))
    conn.commit()
    conn.close()

def get_crops(facility_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM crops WHERE facility_id=?", conn, params=(facility_id,))
    conn.close()
    return df

def add_crop(facility_id, crop_name, quantity):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO crops (facility_id, crop_name, quantity) VALUES (?, ?, ?)", (facility_id, crop_name, quantity))
    conn.commit()
    conn.close()

def get_temp_logs(facility_id, limit=20):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM temp_logs WHERE facility_id=? ORDER BY log_time DESC LIMIT ?",
        conn, params=(facility_id, limit)
    )
    conn.close()
    return df

def add_temp_log(facility_id, temperature):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO temp_logs (facility_id, temperature, log_time) VALUES (?, ?, ?)", (facility_id, temperature, log_time))
    conn.commit()
    conn.close()

def get_facility_name(facility_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM facilities WHERE facility_id=?", (facility_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else "Unknown"

# --- PHYSICAL THRESHOLDS for PHL risk (example values) ---
CROP_TEMP_THRESHOLDS = {
    "maize": 27,
    "rice": 25,
    "cassava": 25,
    "wheat": 26,
    "yam": 24,
    "other": 26
}

def phl_prompt(crop_name, temp):
    thresh = CROP_TEMP_THRESHOLDS.get(crop_name.lower(), CROP_TEMP_THRESHOLDS["other"])
    if temp > thresh:
        return f"⚠️ Storage temperature ({temp}°C) is too high for {crop_name.title()}! Reduce temperature to below {thresh}°C to prevent post-harvest losses."
    return f"✅ Temperature is safe for {crop_name.title()}."

# ----------- APP START -----------
init_db()

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