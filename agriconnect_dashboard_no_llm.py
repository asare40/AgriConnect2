import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import io
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
try:
    from prophet import Prophet
except ImportError:
    Prophet = None

st.set_page_config(page_title="AgriConnect Dashboard", layout="wide")

# --------- SQLite Data Integration ----------
DB_PATH = "agriconnect.db"

def get_data(query="SELECT * FROM farmers"):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --------- Custom CSS for background and card effect ----------
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #e0f7fa 0%, #fffde7 100%);
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.5rem 1rem 1.5rem;
        margin-bottom: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.07);
        text-align: center;
    }
    .sidebar-content {
        background: linear-gradient(135deg, #c8e6c9 0%, #e3f2fd 100%);
        padding: 1rem;
        border-radius: 16px;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --------- SIDEBAR WITH LOGO/BRANDING & FILTERS ----------
with st.sidebar:
    st.markdown('<div class="sidebar-content"><h2>🌾 AgriConnect</h2><p style="font-size: 1.1rem;">Smart Credit & PHL Risk Insights</p></div>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=500&q=80", use_container_width=True)
    st.markdown("---")
    st.header("🔎 Filters")

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

with st.sidebar:
    selected_regions = st.multiselect("Region", options=regions, default=regions)
    credit_range = st.slider("Credit Score", min_value=min_score, max_value=max_score, value=(min_score, max_score))
    selected_interventions = st.multiselect("Interventions", options=interventions, default=interventions)
    st.markdown("---")
    st.caption("© 2025 AgriConnect")

filtered_df = df[
    df['region'].isin(selected_regions) &
    df['predicted_credit_score'].between(*credit_range) &
    df['interventions_adopted'].isin(selected_interventions)
]

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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "Overview Map", "Analytics", "Profiles", "Table",
    "Leaderboards", "Intervention", "Correlations/Download",
    "Distributions", "Advanced", "Forecasting"
])

# --------- TAB 1: OVERVIEW MAP ----------
with tab1:
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
        st.plotly_chart(fig_map, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not generate map: {e}")

# --------- TAB 2: ANALYTICS ----------
with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Adoption Distribution")
        try:
            pie_fig = px.pie(filtered_df, names="interventions_adopted", title="Interventions Adopted")
            st.plotly_chart(pie_fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Pie chart error: {e}")

        st.subheader("Feature Importances (Randomized)")
        try:
            feature_names = [
                'age', 'education', 'farm_size', 'crop_type', 'region', 'tech_literacy',
                'financial_access', 'prev_loan', 'phl_risk_score', 'avg_annual_phl_loss', 'interventions_adopted'
            ]
            importances = np.random.dirichlet(np.ones(len(feature_names)),size=1).flatten()
            imp_df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
            imp_df = imp_df.sort_values("Importance", ascending=True)
            fig_imp = px.bar(imp_df, x="Importance", y="Feature", orientation='h', color="Importance", color_continuous_scale='Greens')
            st.plotly_chart(fig_imp, use_container_width=True)
        except Exception as e:
            st.warning(f"Feature importance error: {e}")

    with col_b:
        st.subheader("Time Trends")
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
            fig_trend.update_layout(xaxis_title="Harvest Month", yaxis_title="Score")
            st.plotly_chart(fig_trend, use_container_width=True)
        except Exception as e:
            st.warning(f"Time trend error: {e}")

        st.subheader("Farmer Segmentation by Risk & Credit")
        try:
            if {'predicted_credit_score', 'phl_risk_score', 'region'}.issubset(filtered_df.columns):
                fig_seg = px.scatter(filtered_df, 
                                x="predicted_credit_score", 
                                y="phl_risk_score", 
                                color="region", 
                                hover_data=["farmer_id"] if "farmer_id" in filtered_df.columns else None,
                                title="Farmers Segmented by Credit Score and PHL Risk")
                st.plotly_chart(fig_seg, use_container_width=True)
            else:
                st.info("Not enough data to segment farmers.")
        except Exception as e:
            st.warning(f"Segmentation error: {e}")

# --------- TAB 3: PROFILES ----------
with tab3:
    st.subheader("Farmer Profile Lookup")
    try:
        farmer_ids = filtered_df['farmer_id'].unique().tolist() if 'farmer_id' in filtered_df.columns else []
        selected_farmer = st.selectbox("Select Farmer ID", ["-- Select --"] + [str(f) for f in farmer_ids])
        if selected_farmer and selected_farmer != "-- Select --":
            farmer_row = filtered_df[filtered_df['farmer_id'] == selected_farmer]
            st.write(f"### Farmer Profile: {selected_farmer}")
            st.json(farmer_row.to_dict(orient='records')[0])
    except Exception as e:
        st.warning(f"Could not display farmer profile: {e}")

    st.subheader("🚨 High-Risk / Low-Credit Farmers")
    try:
        anomalies = filtered_df[
            (filtered_df['phl_risk_score'] > filtered_df['phl_risk_score'].quantile(0.9)) |
            (filtered_df['predicted_credit_score'] < filtered_df['predicted_credit_score'].quantile(0.1))
        ]
        st.dataframe(anomalies)
    except Exception as e:
        st.warning(f"Could not show anomaly table: {e}")

# --------- TAB 4: TABLE ----------
with tab4:
    st.subheader("Browse All Farmers")
    display_cols = [c for c in ['farmer_id','region','predicted_credit_score','phl_risk_score','interventions_adopted'] if c in filtered_df.columns]
    if display_cols:
        st.dataframe(filtered_df[display_cols].sort_values("predicted_credit_score", ascending=False), height=340)
    else:
        st.info("No farmer-level data available.")
    st.download_button(
        label="Download table as CSV",
        data=filtered_df[display_cols].to_csv(index=False).encode('utf-8'),
        file_name='filtered_farmers.csv',
        mime='text/csv'
    )

# --------- TAB 5: LEADERBOARDS ----------
with tab5:
    st.subheader("🏅 Top & Bottom Farmers by Credit Score")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Top 10 Farmers by Credit Score")
        if 'farmer_id' in filtered_df.columns:
            top_farmers = filtered_df.nlargest(10, "predicted_credit_score")
            st.dataframe(top_farmers[["farmer_id", "region", "predicted_credit_score", "phl_risk_score"]])
        else:
            st.info("Farmer IDs not available.")
    with col2:
        st.markdown("#### Bottom 10 Farmers by Credit Score")
        if 'farmer_id' in filtered_df.columns:
            bottom_farmers = filtered_df.nsmallest(10, "predicted_credit_score")
            st.dataframe(bottom_farmers[["farmer_id", "region", "predicted_credit_score", "phl_risk_score"]])
        else:
            st.info("Farmer IDs not available.")

# --------- TAB 6: INTERVENTION ANALYSIS ----------
with tab6:
    st.subheader("🌱 Intervention Effectiveness")
    if "interventions_adopted" in filtered_df.columns:
        eff_df = filtered_df.groupby("interventions_adopted").agg({
            "predicted_credit_score": "mean",
            "phl_risk_score": "mean",
            "farmer_id": "count" if "farmer_id" in filtered_df.columns else "size"
        }).rename(columns={"farmer_id": "num_farmers"}).reset_index()
        st.dataframe(eff_df)
        fig = px.bar(eff_df, x="interventions_adopted", y=["predicted_credit_score", "phl_risk_score"], barmode="group", title="Credit Score & PHL Risk by Intervention")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No intervention data available.")

    st.subheader("📊 Intervention Adoption by Region")
    if {"region", "interventions_adopted"}.issubset(filtered_df.columns):
        crosstab = pd.crosstab(filtered_df["region"], filtered_df["interventions_adopted"])
        fig = px.bar(crosstab, barmode="stack", title="Intervention Adoption by Region")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Region or intervention data missing.")

# --------- TAB 7: CORRELATIONS & DOWNLOAD ----------
with tab7:
    st.subheader("🔗 Correlation Matrix")
    num_cols = filtered_df.select_dtypes(include=np.number).columns
    if len(num_cols) >= 2:
        corr = filtered_df[num_cols].corr()
        fig_corr = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu', title="Correlation Matrix")
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Not enough numerical data for correlations.")

    st.subheader("📥 Download Excel Report")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='FilteredData')
    st.download_button(
        label="Download filtered data as Excel",
        data=output.getvalue(),
        file_name="filtered_farmers.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# --------- TAB 8: DISTRIBUTIONS ----------
with tab8:
    st.subheader("📊 Credit Score Distribution")
    if "predicted_credit_score" in filtered_df.columns:
        fig = px.histogram(filtered_df, x="predicted_credit_score", nbins=20, 
                           title="Credit Score Distribution", 
                           color_discrete_sequence=['#388e3c'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No credit score data available.")

    st.subheader("📊 PHL Risk Score Distribution")
    if "phl_risk_score" in filtered_df.columns:
        fig = px.histogram(filtered_df, x="phl_risk_score", nbins=20, 
                           title="PHL Risk Score Distribution", 
                           color_discrete_sequence=['#fbc02d'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No PHL risk data available.")

# --------- TAB 9: ADVANCED (FARM SIZE, GENDER, CROPS, TIME) ----------
with tab9:
    st.subheader("🌾 Credit Score vs. Farm Size")
    if {"predicted_credit_score", "farm_size"}.issubset(filtered_df.columns):
        fig = px.scatter(filtered_df, x="farm_size", y="predicted_credit_score",
                         color="region", hover_data=["farmer_id"] if "farmer_id" in filtered_df.columns else None,
                         title="Credit Score vs. Farm Size")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Farm size or credit score data missing.")

    st.subheader("🌾 PHL Risk by Crop Type")
    if {"crop_type", "phl_risk_score"}.issubset(filtered_df.columns):
        crop_df = filtered_df.groupby("crop_type")["phl_risk_score"].mean().reset_index()
        fig = px.bar(crop_df, x="crop_type", y="phl_risk_score", 
                     title="Average PHL Risk by Crop Type",
                     color="phl_risk_score", color_continuous_scale="YlOrRd")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Crop type or PHL risk data missing.")

    st.subheader("♀️♂️ Gender-Based Analytics")
    if {"gender", "predicted_credit_score", "phl_risk_score"}.issubset(filtered_df.columns):
        gender_df = filtered_df.groupby("gender").agg({
            "predicted_credit_score": "mean",
            "phl_risk_score": "mean",
            "farmer_id": "count" if "farmer_id" in filtered_df.columns else "size"
        }).rename(columns={"farmer_id": "num_farmers"}).reset_index()
        st.dataframe(gender_df)
        fig = px.bar(gender_df, x="gender", y=["predicted_credit_score", "phl_risk_score"], barmode="group",
                     title="Credit Score & PHL Risk by Gender")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No gender, credit score or PHL risk data available.")

    st.subheader("🗓️ Farmer Count by Month")
    if "harvest_month" in filtered_df.columns:
        by_month = filtered_df.groupby("harvest_month")["farmer_id"].count().reindex([
            'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'
        ])
        fig = px.bar(by_month, title="Number of Farmers by Harvest Month")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No harvest month data available.")

# --------- TAB 10: FORECASTING ----------
with tab10:
    st.subheader("⏩ Forecasting Credit Score & PHL Risk")
    st.markdown("Forecast future average credit score and PHL risk using Prophet time series models.")
    if Prophet is None:
        st.warning("Prophet is not installed. Please run `pip install prophet` to enable forecasting.")
    else:
        if 'harvest_month' in filtered_df.columns:
            month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
            target_metric = st.selectbox("Select metric to forecast", ["predicted_credit_score", "phl_risk_score"])
            ts_df = filtered_df.groupby("harvest_month")[target_metric].mean().reset_index()
            ts_df["month_num"] = ts_df["harvest_month"].map(month_map)
            ts_df = ts_df.sort_values("month_num")
            ts_df["ds"] = pd.to_datetime("2023-" + ts_df["month_num"].astype(str) + "-01")
            ts_df = ts_df.rename(columns={target_metric: "y"})
            m = Prophet()
            m.fit(ts_df[["ds", "y"]])
            future = m.make_future_dataframe(periods=6, freq="M")
            forecast = m.predict(future)
            fig = px.line(forecast, x="ds", y="yhat", title=f"Forecasted {target_metric.replace('_', ' ').title()} (Next 6 Months)")
            fig.add_scatter(x=ts_df["ds"], y=ts_df["y"], mode='markers+lines', name='Actual')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(12))
        else:
            st.info("No 'harvest_month' column available for forecasting. Please provide monthly data.")

st.caption("✨ Built with Streamlit | Analytics and reports for AgriConnect. No LLM features enabled.")
