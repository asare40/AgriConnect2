import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import sqlite3
from datetime import datetime
import os

from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
from shapely.geometry import shape, Point

# --- Config ---
st.set_page_config(page_title="AgriConnect Dashboard", layout="wide")
DB_PATH = "agriconnect.db"

# --- Utility Functions ---
def get_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM farmers", conn)
    conn.close()
    return df

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

# --- Sidebar Navigation ---
with st.sidebar:
    st.title("🌾 AgriConnect")
    nav_opt = st.radio("Navigation", [
        "Analytics Dashboard", 
        "Geospatial Analytics", 
        "Farmer Portal"
    ])
    st.caption("© 2025 AgriConnect")

# ------------- ANALYTICS DASHBOARD ---------------
if nav_opt == "Analytics Dashboard":
    df = get_data()
    if df.empty:
        st.warning("No farmer data available.")
        st.stop()
    regions = sorted(df['region'].dropna().unique().tolist())
    interventions = sorted(df['interventions_adopted'].dropna().unique().tolist())
    min_score, max_score = int(df['predicted_credit_score'].min()), int(df['predicted_credit_score'].max())

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

    st.markdown("## 📊 Credit & PHL Analytics Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Farmers", len(filtered_df))
    c2.metric("Avg Credit Score", f"{filtered_df['predicted_credit_score'].mean():.2f}")
    c3.metric("Avg PHL Risk", f"{filtered_df['phl_risk_score'].mean():.2f}")

    tabnames = [
        "Overview Map", "Analytics", "Profiles", "Table",
        "Leaderboards", "Intervention", "Correlations/Download",
        "Distributions", "Advanced"
    ]
    tabs = st.tabs(tabnames)

    # --- Overview Map ---
    with tabs[0]:
        st.subheader("Regional Hotspots Map")
        region_coords = {
            "Kano": (12.0, 8.5), "Oyo": (7.85, 3.93), "Benue": (7.34, 8.77),
            "Kaduna": (10.52, 7.44), "Plateau": (9.22, 9.52), "Sokoto": (13.06, 5.24),
            "Niger": (9.63, 6.54), "Bauchi": (10.31, 9.84)
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
            color_continuous_scale=px.colors.sequential.YlGnBu,
            size_max=30,
            zoom=5,
            mapbox_style="carto-positron"
        )
        st.plotly_chart(fig_map, use_container_width=True)
        insight_card(
            "Regional Hotspots Map",
            "Shows clusters of high PHL risk and credit scores. Use this to target interventions.",
            color="#d1c4e9"
        )

    # --- Analytics ---
    with tabs[1]:
        st.subheader("Key Analytics")
        st.bar_chart(filtered_df.groupby("region")["predicted_credit_score"].mean())
        st.bar_chart(filtered_df.groupby("region")["phl_risk_score"].mean())
        insight_card(
            "PHL & Credit Score by Region",
            "Visualize mean risk and credit scores by region for data-driven decisions.",
            color="#f8bbd0"
        )

    # --- Profiles ---
    with tabs[2]:
        st.subheader("Farmer Profiles")
        st.dataframe(filtered_df.head(20))
        insight_card(
            "Sample Farmer Profiles",
            "Review individual farmer records for detailed insights.",
            color="#f0f4c3"
        )

    # --- Table ---
    with tabs[3]:
        st.subheader("Full Farmer Data Table")
        st.dataframe(filtered_df)
        insight_card(
            "Data Table",
            "View and export the full filtered dataset for external analysis.",
            color="#ffe0b2"
        )

    # --- Leaderboards ---
    with tabs[4]:
        st.subheader("Leaderboards")
        st.write("Top 5 Farmers by Credit Score:")
        st.dataframe(filtered_df.sort_values(by="predicted_credit_score", ascending=False).head(5))
        st.write("Top 5 Regions by Avg Credit Score:")
        st.dataframe(
            filtered_df.groupby("region")["predicted_credit_score"].mean().sort_values(ascending=False).head(5)
            .reset_index().rename(columns={"predicted_credit_score": "Avg Credit Score"})
        )
        insight_card(
            "Leaderboards",
            "See which farmers and regions are performing best.",
            color="#b2ebf2"
        )

    # --- Intervention ---
    with tabs[5]:
        st.subheader("Intervention Adoption")
        st.bar_chart(filtered_df["interventions_adopted"].value_counts())
        insight_card(
            "Intervention Analysis",
            "Which interventions are most widely adopted?",
            color="#ffecb3"
        )

    # --- Correlations/Download ---
    with tabs[6]:
        st.subheader("Correlations")
        st.write(filtered_df[["predicted_credit_score", "phl_risk_score"]].corr())
        st.download_button("Download Filtered Data as CSV", data=filtered_df.to_csv(), file_name="filtered_farmers.csv")
        insight_card(
            "Correlations & Download",
            "Explore correlations and download your filtered dataset.",
            color="#c8e6c9"
        )

    # --- Distributions ---
    with tabs[7]:
        st.subheader("Distributions")
        st.plotly_chart(
            px.histogram(filtered_df, x="predicted_credit_score", nbins=20, title="Credit Score Distribution"),
            use_container_width=True
        )
        st.plotly_chart(
            px.histogram(filtered_df, x="phl_risk_score", nbins=20, title="PHL Risk Score Distribution"),
            use_container_width=True
        )
        insight_card(
            "Distributions",
            "Visualize the spread of key farmer metrics.",
            color="#dcedc8"
        )

    # --- ADVANCED TAB ---
    with tabs[8]:
        st.subheader("Advanced Analytics")

        # 1. Correlation Matrix (Heatmap)
        st.markdown("**Correlation Matrix (Heatmap)**")
        numeric_cols = ["predicted_credit_score", "phl_risk_score", "latitude", "longitude"]
        corr = filtered_df[numeric_cols].corr()
        fig_corr = ff.create_annotated_heatmap(
            z=corr.values,
            x=list(corr.columns),
            y=list(corr.columns),
            annotation_text=np.round(corr.values, 2),
            colorscale='Viridis')
        st.plotly_chart(fig_corr, use_container_width=True)
        insight_card(
            "Correlation Matrix",
            "This chart uncovers which variables are strongly related. For example, a high correlation between PHL risk and latitude may reveal geography-driven losses. Strong correlations can inform predictive modeling or targeted interventions."
        )

        # 2. Parallel Categories (Intervention Adoption by Credit, Region, Risk)
        st.markdown("**Parallel Categories: Interventions, Regions, Credit, PHL Risk**")
        fig_parallel = px.parallel_categories(
            filtered_df,
            dimensions=["region", "interventions_adopted", "predicted_credit_score", "phl_risk_score"],
            color="predicted_credit_score",
            color_continuous_scale=px.colors.sequential.Inferno
        )
        st.plotly_chart(fig_parallel, use_container_width=True)
        insight_card(
            "Parallel Categories Analysis",
            "See how regions, interventions, and farmer scores interconnect. For example, you may discover some regions adopt certain interventions more often and tend to have lower PHL risk or higher credit scores."
        )

        # 3. Box Plot: PHL Risk by Intervention
        st.markdown("**Box Plot: PHL Risk by Intervention**")
        fig_box = px.box(
            filtered_df,
            x="interventions_adopted",
            y="phl_risk_score",
            color="interventions_adopted",
            points="all"
        )
        st.plotly_chart(fig_box, use_container_width=True)
        insight_card(
            "PHL Risk by Intervention",
            "This box plot compares the distribution of post-harvest loss risk across different interventions. Interventions with lower median risk and less variability are likely most effective."
        )

        # 4. Credit Score vs PHL Risk (Scatter with Trendline)
        st.markdown("**Scatter: Credit Score vs PHL Risk (with Trendline)**")
        fig_scatter = px.scatter(
            filtered_df,
            x="predicted_credit_score",
            y="phl_risk_score",
            color="region",
            trendline="ols",
            hover_data=["interventions_adopted"]
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        insight_card(
            "Credit Score vs. PHL Risk",
            "Investigate how creditworthiness relates to post-harvest loss risk. Outliers may indicate farmers with strong credit but high risk (or vice versa), suggesting areas for targeted support."
        )

        # 5. Sunburst: Region → Intervention → PHL Risk Quantile
        st.markdown("**Sunburst: Region → Intervention → PHL Risk Quantile**")
        filtered_df["phl_risk_quantile"] = pd.qcut(filtered_df["phl_risk_score"], 3, labels=["Low", "Medium", "High"])
        filtered_df["phl_risk_quantile"] = filtered_df["phl_risk_quantile"].astype(str)  # Fix for Categorical error
        fig_sunburst = px.sunburst(
            filtered_df,
            path=["region", "interventions_adopted", "phl_risk_quantile"],
            values="predicted_credit_score",
            color="phl_risk_quantile",
            color_discrete_map={"Low":"#66bb6a", "Medium":"#ffa726", "High":"#ef5350"}
        )
        st.plotly_chart(fig_sunburst, use_container_width=True)
        insight_card(
            "Sunburst: Region → Intervention → PHL Risk",
            "This nested chart shows how interventions are distributed across regions and how they impact PHL risk. Use it to spot which interventions drive risk down in specific regions."
        )

        # 6. Violin Plot: Credit Score Distribution by Region
        st.markdown("**Violin Plot: Credit Score by Region**")
        fig_violin = px.violin(
            filtered_df,
            y="predicted_credit_score",
            x="region",
            box=True,
            points="all",
            color="region"
        )
        st.plotly_chart(fig_violin, use_container_width=True)
        insight_card(
            "Credit Score Distribution by Region",
            "Violin plots reveal the full distribution of credit scores within each region, highlighting disparities and regions with more uniform or extreme credit profiles."
        )

# ------------- GEOSPATIAL ANALYTICS ---------------
if nav_opt == "Geospatial Analytics":
    st.title("🌍 Interactive Geospatial Analytics")
    df = get_data()
    if df.empty:
        st.warning("No farmer data available.")
        st.stop()

    mean_lat = df["latitude"].mean()
    mean_lon = df["longitude"].mean()
    m = folium.Map(location=[mean_lat, mean_lon], zoom_start=6, tiles="CartoDB positron")

    # Weather overlay (OpenWeatherMap Clouds)
    folium.raster_layers.TileLayer(
        tiles="https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid=7f99963df27b79b5916b0272ad753f62",
        attr="OpenWeatherMap",
        name="Clouds (live)",
        overlay=True,
        control=True,
        opacity=0.6
    ).add_to(m)
    # Satellite imagery
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="ESRI Satellite",
        name="Satellite",
        overlay=True,
        control=True
    ).add_to(m)

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

    Draw(export=True).add_to(m)
    folium.LayerControl().add_to(m)
    output = st_folium(m, width=900, height=600, returned_objects=["last_drawn"])

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
                "These statistics are calculated for only the farmers within your selected region.",
                color="#b2dfdb"
            )
        else:
            st.info("No farmers found in this region.")

    insight_card(
        "WOW Feature: Interactive Geospatial Analysis",
        "- Dynamic map with weather and satellite overlays.<br>"
        "- Draw/select regions for hyperlocal analytics.",
        color="#ffe0b2"
    )

# -------------- FARMER PORTAL (Demo) -------------
if nav_opt == "Farmer Portal":
    st.title("👤 Farmer Portal (Demo)")
    st.write("This is a demonstration portal. Login, registration, and storage/crop monitoring features can be added here as needed.")
    st.info("For demo, please use Analytics or Geospatial Analytics tabs.")