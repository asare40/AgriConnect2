import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="AgriConnect: Farmer Credit & PHL Risk Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("integrated_results.csv")
    return df

df = load_data()

st.title("🌾 AgriConnect: Farmer Credit & Post-Harvest Loss (PHL) Risk Dashboard")

# Sidebar filters
st.sidebar.header("Find a Farmer")
farmer_ids = df['farmer_id'].unique()
selected_id = st.sidebar.selectbox("Select Farmer ID", sorted(farmer_ids))
farmer_row = df[df['farmer_id'] == selected_id].iloc[0]

st.sidebar.markdown("---")
st.sidebar.write(f"**Credit Score:** {farmer_row['predicted_credit_score']:.2f}")
st.sidebar.write(f"**PHL Risk Score:** {farmer_row['phl_risk_score']:.2f}")
st.sidebar.write(f"**Interventions Adopted:** {int(farmer_row['interventions_adopted'])}")

# Main metrics
col1, col2, col3 = st.columns(3)
col1.metric("Credit Score", f"{farmer_row['predicted_credit_score']:.2f}", 
            help="Probability farmer will repay loan (1=highly likely)")
col2.metric("PHL Risk Score", f"{farmer_row['phl_risk_score']:.2f}", 
            help="Risk of post-harvest losses (1=very risky)")
col3.metric("Interventions Adopted", int(farmer_row['interventions_adopted']), 
            help="Number of risk-reducing interventions adopted")

# Recommendation logic
def get_recommendation(credit, risk, interventions):
    if credit >= 0.7 and risk <= 0.4:
        return "✅ Eligible for favorable loan. Low PHL risk."
    elif credit >= 0.7 and risk > 0.4:
        return "⚠️ Eligible for loan, but PHL risk is high. Adopt more PHL interventions!"
    elif credit < 0.5:
        return "❌ Improve repayment record or reduce PHL risk to qualify for credit."
    else:
        return "Consider adopting more interventions and improving market timing/storage."

st.subheader("Actionable Recommendation")
st.info(get_recommendation(farmer_row['predicted_credit_score'], 
                           farmer_row['phl_risk_score'], 
                           farmer_row['interventions_adopted']))

# Visualizations: Distribution of scores
st.subheader("Credit Score & PHL Risk Distribution (All Farmers)")
fig, ax = plt.subplots(1,2, figsize=(10,4))
ax[0].hist(df['predicted_credit_score'], bins=20, color='green', alpha=0.7)
ax[0].axvline(farmer_row['predicted_credit_score'], color='red', linestyle='--', label='Selected Farmer')
ax[0].set_title("Credit Score Distribution")
ax[0].set_xlabel("Credit Score")
ax[0].set_ylabel("Count")
ax[0].legend()

ax[1].hist(df['phl_risk_score'], bins=20, color='orange', alpha=0.7)
ax[1].axvline(farmer_row['phl_risk_score'], color='red', linestyle='--', label='Selected Farmer')
ax[1].set_title("PHL Risk Score Distribution")
ax[1].set_xlabel("PHL Risk Score")
ax[1].set_ylabel("Count")
ax[1].legend()
st.pyplot(fig)

# Optional: Show table of all farmers
st.subheader("Browse All Farmers")
st.dataframe(df[['farmer_id', 'predicted_credit_score', 'phl_risk_score', 'interventions_adopted']].sort_values("predicted_credit_score", ascending=False), height=300)

st.caption("Hackathon demo | AgriConnect | Youth farmers, smarter finance & storage decisions 🚜")