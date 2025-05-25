import streamlit as st
import pandas as pd

st.set_page_config(page_title="Debug App", layout="wide")

df = pd.read_csv("integrated_results.csv")
st.write("Data loaded:", df.shape)
st.write("Columns:", df.columns.tolist())
st.write(df.head())

try:
    st.subheader("Testing region column access")
    st.write(df['region'].value_counts())
except Exception as e:
    st.error(f"Problem accessing 'region': {e}")