import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
from datetime import datetime, timedelta
import random
import os

# Geospatial tools
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
from shapely.geometry import shape, Point

st.set_page_config(page_title="AgriConnect Dashboard", layout="wide")

# --- Utility Functions ---
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
    now = datetime.now()
    for i in range(7):
        temp = 25 + (i % 4)
        log_time = (now - timedelta(days=6-i)).strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO temp_logs (facility_id, temperature, log_time) VALUES (?, ?, ?)", (facility_id, temp, log_time))
    conn.commit()
    conn.close()

def prepare_sample_weather_csv():
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

init_farmer_db()
with st.sidebar:
    st.markdown('<div class="sidebar-content"><h2>🌾 AgriConnect</h2><p style="font-size: 1.1rem;">Smart Credit & PHL Risk Insights</p></div>', unsafe_allow_html=True)
    nav_opt = st.radio("Navigation", ["Analytics Dashboard", "Geospatial Analytics", "Farmer Portal"])
    if st.button("Populate full demo farmer + weather"):
        populate_farmer_with_full_crop_and_temps()
        prepare_sample_weather_csv()
        st.success("Demo farmer, crop, temperature logs, and sample weather file created!\nUsername: demo_farmer\nPassword: securepass")
    st.markdown("---")
    st.caption("© 2025 AgriConnect")

# ----------------- Analytics Dashboard -----------------
if nav_opt == "Analytics Dashboard":
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

    with st.sidebar:
        st.header("🔎 Filters")
        selected_regions = st.multiselect("Region", options=regions, default=regions, key="region_analytics")
        credit_range = st.slider("Credit Score", min_value=min_score, max_value=max_score, value=(min_score, max_score), key="credit_analytics")
        selected_interventions = st.multiselect("Interventions", options=interventions, default=interventions, key="intv_analytics")
        st.markdown("---")

    filtered_df = df[
        df['region'].isin(selected_regions) &
        df['predicted_credit_score'].between(*credit_range) &
        df['interventions_adopted'].isin(selected_interventions)
    ]

    if filtered_df.empty:
        st.info("No data matches your filter selection.")
        st.stop()

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

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "Overview Map", "Analytics", "Profiles", "Table",
        "Leaderboards", "Intervention", "Correlations/Download",
        "Distributions", "Advanced"
    ])

    with tab1:
        with st.expander("ℹ️ About this map"):
            st.markdown("This map visualizes average PHL risk and credit score by region. Bubble size = Avg PHL Risk, Color = Avg Credit Score.")
        st.subheader("Regional Hotspots")
        try:
            region_coords = {
                "Kano": (12.0, 8.5),
                "Oyo": (7.85, 3.93),
                "Benue": (7.34, 8.77),
                "Kaduna": (10.52, 7.44),
                "Plateau": (9.22, 9.52),
            }
            filtered_df['region_lat'] = filtered_df['region'].map(lambda r: region_coords.get(r, (9.0,8.0))[0])
            filtered_df['region_lon'] = filtered_df['region'].map(lambda r: region_coords.get(r, (9.0,8.0))[1])
            grouped = filtered_df.groupby('region').agg({
                'phl_risk_score':'mean',
                'predicted_credit_score':'mean',
                'region_lat':'first',
                'region_lon':'first'
            }).reset_index()
            fig_map = px.scatter_mapbox(
                grouped,
                lat="region_lat", lon="region_lon",
                size="phl_risk_score",
                color="predicted_credit_score",
                hover_name="region",
                hover_data={"phl_risk_score":":.2f", "predicted_credit_score":":.2f"},
                color_continuous_scale=px.colors.sequential.YlGnBu,
                size_max=30,
                zoom=5,
                mapbox_style="carto-positron"
            )
            fig_map.update_traces(
                hovertemplate="<b>Region:</b> %{hovertext}<br>" +
                              "<b>Avg PHL Risk:</b> %{customdata[0]:.2f}<br>" +
                              "<b>Avg Credit Score:</b> %{customdata[1]:.2f}<br>" +
                              "<extra></extra>"
            )
            st.plotly_chart(fig_map, use_container_width=True)
            insight_card(
                "Regional Hotspots Map",
                "This map identifies regional clusters of high PHL risk and varying credit scores. Use it to target interventions where they're needed most.",
                color="#d1c4e9"
            )
        except Exception as e:
            st.warning(f"Could not generate map: {e}")

    # ... [rest of analytics tabs: see previous code for all tabs with insight_card and info expanders] ...
    # (for brevity, only the Geospatial and Farmer Portal are fully expanded here)

# ----------------- Geospatial Analytics Tab -----------------
if nav_opt == "Geospatial Analytics":
    st.title("🌍 Interactive Geospatial Analytics")
    with st.expander(
        "ℹ️ How to use this map:"
    ):
        st.markdown(
            """
            - **Pan and zoom** to explore the regions.
            - **Toggle weather/satellite overlays** with the layer control in the top right.
            - **Draw polygons/rectangles** to select a region for hyperlocal analytics.
            - When you draw a region, the dashboard will analyze and summarize all farmers within that area!
            """
        )

    try:
        df = get_data()
        # Require latitude/longitude
        if df.empty or any([col not in df.columns for col in ("region", "latitude", "longitude", "phl_risk_score", "predicted_credit_score")]):
            st.warning("No geospatial farmer data available or required columns missing (need latitude and longitude columns).")
            st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

    mean_lat = df["latitude"].mean()
    mean_lon = df["longitude"].mean()
    m = folium.Map(location=[mean_lat, mean_lon], zoom_start=6, tiles="CartoDB positron")

    # --- Weather Overlay (OpenWeatherMap Clouds) ---
    folium.raster_layers.TileLayer(
        tiles="https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid=7f99963df27b79b5916b0272ad753f62",
        attr="OpenWeatherMap",
        name="Clouds (live)",
        overlay=True,
        control=True,
        opacity=0.6
    ).add_to(m)

    # --- Satellite Imagery ---
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="ESRI Satellite",
        name="Satellite",
        overlay=True,
        control=True
    ).add_to(m)

    # --- Add Farmer Points ---
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=8,
            popup=(f"Region: {row['region']}<br>"
                   f"PHL Risk: {row['phl_risk_score']:.2f}<br>"
                   f"Credit: {row['predicted_credit_score']}"),
            color="blue",
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

    # --- Drawing Tools ---
    Draw(export=True).add_to(m)
    folium.LayerControl().add_to(m)

    # --- Streamlit-Folium Integration ---
    output = st_folium(m, width=900, height=600, returned_objects=["last_drawn"])

    # --- Hyperlocal Analytics ---
    if output and output.get("last_drawn"):
        geometry = output["last_drawn"]["geometry"]
        polygon = shape(geometry)
        df["in_selection"] = df.apply(lambda row: polygon.contains(Point(row["longitude"], row["latitude"])), axis=1)
        subdf = df[df["in_selection"]]
        st.success(f"{len(subdf)} farmers found in the selected region.")
        if len(subdf) > 0:
            st.dataframe(subdf[["region", "latitude", "longitude", "phl_risk_score", "predicted_credit_score"]])
            st.write("**Hyperlocal Summary:**")
            st.metric("Avg PHL Risk", f"{subdf['phl_risk_score'].mean():.2f}")
            st.metric("Avg Credit Score", f"{subdf['predicted_credit_score'].mean():.2f}")
            insight_card(
                "Hyperlocal Analytics",
                "These statistics are calculated for only the farmers within your selected region. "
                "Use this to target interventions or analyze local risk in detail.",
                color="#b2dfdb"
            )
        else:
            st.info("No farmers found in this region.")

    insight_card(
        "WOW Feature: Interactive Geospatial Analysis",
        "- Dynamic, zoomable map with weather and satellite overlays.<br>"
        "- Draw/select custom regions for hyperlocal PHL and credit analytics.<br>"
        "- View real-time clouds and satellite data for your target area.",
        color="#ffe0b2"
    )

# ----------------- Farmer Portal -----------------
if nav_opt == "Farmer Portal":
    if "user" not in st.session_state:
        st.session_state["user"] = None

    def login_page():
        st.header("👤 Farmer Login / Register")
        with st.expander("ℹ️ About the portal"):
            st.markdown(
                """
                The Farmer Portal lets you manage your storage facilities, crops, and monitor storage conditions.<br>
                Register or log in to get started.
                """
            )
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
        with tabs[0]:
            with st.expander("ℹ️ About facilities"):
                st.markdown("Shows your storage facilities and their locations. Add more in the next tab.")
            st.subheader("My Storage Facilities")
            fdf = get_facilities(st.session_state["user"]["user_id"])
            if len(fdf):
                st.dataframe(fdf[["facility_id", "name", "location"]])
            else:
                st.info("No facilities yet. Add one in 'Add Facility' tab.")

        with tabs[1]:
            with st.expander("ℹ️ About adding facilities"):
                st.markdown("Register a new storage facility to track your crops and storage conditions.")
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

        with tabs[2]:
            with st.expander("ℹ️ About monitoring storage"):
                st.markdown(
                    """
                    - Monitor your crop inventories and log storage temperature.<br>
                    - Visualize storage and weather temperature trends.<br>
                    - Add crops and temperature logs as needed.
                    """
                )
            st.subheader("Monitor Storage Facility")
            fdf = get_facilities(st.session_state["user"]["user_id"])
            if len(fdf):
                fac_options = {f"{row['name']} ({row['location']})": row["facility_id"] for i, row in fdf.iterrows()}
                selected_fac = st.selectbox("Select Facility", list(fac_options.keys()))
                fac_id = fac_options[selected_fac]
                st.markdown(f"**Facility:** {selected_fac}")

                st.markdown("#### Crops in This Facility")
                cdf = get_crops(fac_id)
                if len(cdf):
                    st.dataframe(cdf[["crop_name", "quantity"]])
                else:
                    st.info("No crops yet. Add below.")

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

                st.markdown("#### Storage Temperature Log")
                temp = st.number_input("Record Temperature (°C)", min_value=0.0)
                if st.button("Log Temperature"):
                    add_temp_log(fac_id, temp)
                    st.success("Temperature logged!")
                    st.rerun()

                tdf = get_temp_logs(fac_id)
                if len(tdf):
                    st.line_chart(tdf.sort_values("log_time")["temperature"], use_container_width=True)
                    st.dataframe(tdf[["temperature", "log_time"]])
                else:
                    st.info("No temperature logs yet.")

                st.subheader("Storage vs. Weather Temperature (Kano)")
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

        with tabs[3]:
            with st.expander("ℹ️ About PHL prompts"):
                st.markdown(
                    """
                    Get instant advice if your storage temperature is too high for any crop.<br>
                    - Prompts based on your latest temperature log per facility.
                    """
                )
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