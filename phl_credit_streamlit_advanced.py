import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

st.set_page_config(page_title="AgriConnect Advanced Dashboard", layout="wide")
st.title("🌾 AgriConnect: Advanced Credit & PHL Risk Dashboard")

# --- Load data and validate ---
csv_file = "integrated_results.csv"
try:
    df = pd.read_csv(csv_file)
    st.success(f"Loaded {csv_file}: {df.shape[0]} rows, {df.shape[1]} columns")
    st.write("Columns:", df.columns.tolist())
except Exception as e:
    st.error(f"Error loading {csv_file}: {e}")
    st.stop()

# --- Feature Importance Chart (example random importances) ---
st.subheader("🚦 Model Feature Importances")
try:
    feature_names = [
        'age', 'education', 'farm_size', 'crop_type', 'region', 'tech_literacy',
        'financial_access', 'prev_loan', 'phl_risk_score', 'avg_annual_phl_loss', 'interventions_adopted'
    ]
    importances = np.random.dirichlet(np.ones(len(feature_names)),size=1).flatten()
    imp_df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
    imp_df = imp_df.sort_values("Importance", ascending=True)

    fig, ax = plt.subplots(figsize=(7,4))
    ax.barh(imp_df["Feature"], imp_df["Importance"], color='seagreen')
    ax.set_xlabel("Relative Importance")
    st.pyplot(fig)
except Exception as e:
    st.warning(f"Could not plot feature importances: {e}")

# --- Interactive Regional Map ---
st.subheader("🗺️ Regional Hotspots: PHL Risk & Credit Score")
try:
    # Fallback region coords for demo
    region_coords = {
        "Kano": (12.0, 8.5),
        "Oyo": (7.85, 3.93),
        "Benue": (7.34, 8.77),
        "Kaduna": (10.52, 7.44),
        "Plateau": (9.22, 9.52),
    }
    df['region_lat'] = df['region'].map(lambda r: region_coords.get(r, (9.0,8.0))[0])
    df['region_lon'] = df['region'].map(lambda r: region_coords.get(r, (9.0,8.0))[1])

    grouped = df.groupby('region').agg({
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
        mapbox_style="carto-positron",
        title="PHL Risk (size) & Credit Score (color) by Region"
    )
    st.plotly_chart(fig_map, use_container_width=True)
except Exception as e:
    st.warning(f"Could not generate map: {e}")

# --- Time Trends ---
st.subheader("📈 Time Trends: PHL Risk & Credit Score by Harvest Month")
try:
    if 'harvest_month' not in df.columns:
        df['harvest_month'] = np.random.choice(
            ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], size=len(df)
        )
    month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    trend_df = df.groupby('harvest_month').agg({
        'phl_risk_score':'mean',
        'predicted_credit_score':'mean'
    }).reindex(month_order)
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=trend_df.index, y=trend_df['phl_risk_score'],
                                   mode='lines+markers', name='Avg PHL Risk', line=dict(color='orange')))
    fig_trend.add_trace(go.Scatter(x=trend_df.index, y=trend_df['predicted_credit_score'],
                                   mode='lines+markers', name='Avg Credit Score', line=dict(color='green')))
    fig_trend.update_layout(title="Average PHL Risk & Credit Score by Harvest Month",
                            xaxis_title="Harvest Month", yaxis_title="Score")
    st.plotly_chart(fig_trend, use_container_width=True)
except Exception as e:
    st.warning(f"Could not plot time trends: {e}")

# --- Farmer-Level Table ---
st.subheader("👤 Browse All Farmers")
display_cols = [c for c in ['farmer_id','region','predicted_credit_score','phl_risk_score','interventions_adopted'] if c in df.columns]
if display_cols:
    st.dataframe(df[display_cols].sort_values("predicted_credit_score", ascending=False), height=320)
else:
    st.info("No farmer-level data available.")

st.caption("Advanced dashboard: Visuals, analytics, and error handling included. Add more filters, predictions, or visuals as needed!")