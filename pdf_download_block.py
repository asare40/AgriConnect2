from fpdf import FPDF

def create_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    colwidth = pdf.w / (len(dataframe.columns) + 1)
    row_height = pdf.font_size * 1.5

    # Header
    for col in dataframe.columns:
        pdf.cell(colwidth, row_height, str(col), border=1)
    pdf.ln(row_height)
    # Rows
    for i, row in dataframe.iterrows():
        for item in row:
            pdf.cell(colwidth, row_height, str(item), border=1)
        pdf.ln(row_height)
    return pdf.output(dest='S').encode('latin-1')

pdf_bytes = create_pdf(your_df)
st.download_button(
    label="Download Results (PDF)",
    data=pdf_bytes,
    file_name="farmer_credit_scores.pdf",
    mime="application/pdf"
)