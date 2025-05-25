import streamlit as st
import pandas as pd

st.set_page_config(page_title="Test App", layout="wide")
st.title("Test Streamlit Data Load")

try:
    df = pd.read_csv("integrated_results.csv")
    st.write("Data loaded successfully!")
    st.write(df.head())
except Exception as e:
    st.error(f"Failed to load CSV: {e}")