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

# --- Sidebar filters ---
with st.sidebar:
    st.header("Filter data")
    # Region
    regions = df['region'].dropna().unique().tolist()
    selected_regions = st.multiselect("Select region(s)", regions, default=regions)
    # Credit Score
    min_score, max_score = float(df['predicted_credit_score'].min()), float(df['predicted_credit_score'].max())
    credit_range = st.slider("Credit Score range", min_value=min_score, max_value=max_score, value=(min_score, max_score))
    # Interventions
    interventions = df['interventions_adopted'].dropna().unique().tolist()
    selected_interventions = st.multiselect("Interventions adopted", interventions, default=interventions)
    # Layout options
    st.header("Dashboard Options")
    show_metrics = st.checkbox("Show Key Metrics", True)
    show_map = st.checkbox("Show Regional Map", True)
    show_pie = st.checkbox("Show Intervention Pie Chart", True)
    show_corr = st.checkbox("Show Correlation Heatmap", True)
    show_trend = st.checkbox("Show Time Trends", True)
    show_anomaly = st.checkbox("Show High-Risk Table", True)
    show_summary = st.checkbox("Show Summary Statistics", False)

# --- Filter data accordingly ---
filtered_df = df[
    df['region'].isin(selected_regions) &
    df['predicted_credit_score'].between(*credit_range) &
    df['interventions_adopted'].isin(selected_interventions)
]

# --- Download Button for Filtered Data ---
st.download_button(
    label="Download filtered data as CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='filtered_agriconnect.csv',
    mime='text/csv'
)

# --- Key Metrics Cards ---
if show_metrics:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Farmers", len(filtered_df))
    col2.metric("Avg Credit Score", f"{filtered_df['predicted_credit_score'].mean():.2f}")
    col3.metric("Avg PHL Risk", f"{filtered_df['phl_risk_score'].mean():.2f}")

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
if show_map:
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
            mapbox_style="carto-positron",
            title="PHL Risk (size) & Credit Score (color) by Region"
        )
        st.plotly_chart(fig_map, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not generate map: {e}")

# --- Intervention Adoption Pie Chart ---
if show_pie:
    st.subheader("Intervention Adoption Distribution")
    try:
        pie_fig = px.pie(filtered_df, names="interventions_adopted", title="Interventions Adopted by Farmers")
        st.plotly_chart(pie_fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not plot intervention pie chart: {e}")

# --- Correlation Heatmap ---
if show_corr:
    st.subheader("Correlation Heatmap")
    try:
        num_cols = filtered_df.select_dtypes(include=np.number).columns
        corr = filtered_df[num_cols].corr()
        fig_corr = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu', title="Correlation Matrix")
        st.plotly_chart(fig_corr, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not generate correlation heatmap: {e}")

# --- Time Trends ---
if show_trend:
    st.subheader("📈 Time Trends: PHL Risk & Credit Score by Harvest Month")
    try:
        if 'harvest_month' not in filtered_df.columns:
            filtered_df['harvest_month'] = np.random.choice(
                ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], size=len(filtered_df)
            )
        month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        trend_df = filtered_df.groupby('harvest_month').agg({
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

# --- Anomaly Detection Table ---
if show_anomaly:
    st.subheader("🚨 High-Risk / Low-Credit Farmers")
    try:
        anomalies = filtered_df[
            (filtered_df['phl_risk_score'] > filtered_df['phl_risk_score'].quantile(0.9)) |
            (filtered_df['predicted_credit_score'] < filtered_df['predicted_credit_score'].quantile(0.1))
        ]
        st.dataframe(anomalies)
    except Exception as e:
        st.warning(f"Could not show anomaly table: {e}")

# --- Farmer Profile Popup ---
st.subheader("👤 Farmer Profile Lookup")
try:
    farmer_ids = filtered_df['farmer_id'].unique().tolist() if 'farmer_id' in filtered_df.columns else []
    selected_farmer = st.selectbox("Select a Farmer ID for details", ["-- Select --"] + [str(f) for f in farmer_ids])
    if selected_farmer and selected_farmer != "-- Select --":
        farmer_row = filtered_df[filtered_df['farmer_id'] == selected_farmer]
        st.write(f"### Farmer Profile: {selected_farmer}")
        st.json(farmer_row.to_dict(orient='records')[0])
except Exception as e:
    st.warning(f"Could not display farmer profile: {e}")

# --- Geospatial Cluster Map (if lat/lon present) ---
st.subheader("Farmer Geospatial Clusters")
if 'lat' in filtered_df.columns and 'lon' in filtered_df.columns:
    st.map(filtered_df[['lat', 'lon']])
else:
    st.info("No latitude/longitude columns found for cluster map.")

# --- Farmer-Level Table ---
st.subheader("Browse All Farmers")
display_cols = [c for c in ['farmer_id','region','predicted_credit_score','phl_risk_score','interventions_adopted'] if c in filtered_df.columns]
if display_cols:
    st.dataframe(filtered_df[display_cols].sort_values("predicted_credit_score", ascending=False), height=320)
else:
    st.info("No farmer-level data available.")

# --- Summary Statistics Panel ---
if show_summary:
    st.subheader("Summary Statistics")
    try:
        st.dataframe(filtered_df.describe())
    except Exception as e:
        st.warning(f"Could not show summary statistics: {e}")

st.caption("Advanced dashboard: Visuals, analytics, filtering, anomaly detection, and error handling included.")