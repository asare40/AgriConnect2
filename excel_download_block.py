import io

excel_buffer = io.BytesIO()
your_df.to_excel(excel_buffer, index=False, engine='openpyxl')
st.download_button(
    label="Download Results (Excel)",
    data=excel_buffer.getvalue(),
    file_name="farmer_credit_scores.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)