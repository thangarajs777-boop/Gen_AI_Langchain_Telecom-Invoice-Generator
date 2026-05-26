import streamlit as st
import pandas as pd
from datetime import datetime
from utils.invoice_generator import (
    calculate_invoice,
    generate_invoice_number,
    get_required_columns_message,
)
from utils.pdf_generator import create_invoice_pdf
from utils.rag_engine import get_ai_recommendation

st.set_page_config(page_title="Telecom Invoice Generator", layout="centered")
st.title("📞 Telecom Invoice GEN AI Application")

st.header("Upload Calls Summary Excel File")

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx", "csv"],
    help="Required Columns: Total billed minutes, Total customer cost",
)

if uploaded_file:
    # Safely handle dataset formats
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Calls Summary Preview")
    st.dataframe(df)

    column_error = get_required_columns_message(df)
    if column_error:
        st.error(column_error)
        st.stop()

    st.header("Customer Information")
    customer_name = st.text_input("Customer Name", placeholder="e.g., Voicetec SYS LTD")
    customer_address = st.text_area("Customer Address", placeholder="Enter official billing address")
    mobile_number = st.text_input("Mobile / Contact Number")

    st.header("Invoice Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        invoice_start_date = st.date_input("Invoice Start Date", value=datetime.today())
    with col2:
        invoice_end_date = st.date_input("Invoice End Date", value=datetime.today())
    with col3:
        due_date = st.date_input("Invoice Due Date", value=datetime.today())

    st.markdown("---")

    if st.button("Generate Invoice", type="primary"):
        if not customer_name.strip():
            st.warning("Please specify customer name reference prior to pdf build execution.")
            st.stop()

        invoice_number = generate_invoice_number(customer_name, due_date)
        
        # Calculates structured data items grouped by destination prefix safely
        invoice_data = calculate_invoice(df)

        ai_recommendation = get_ai_recommendation(invoice_data["total_data_usage"])

        # Generates exact corporate grid PDF format 
        pdf_file = create_invoice_pdf(
            customer_name,
            customer_address,
            mobile_number,
            invoice_number,
            invoice_start_date,
            invoice_end_date,
            due_date,
            invoice_data,
            ai_recommendation,
        )

        st.success("🎉 Invoice Generated Successfully!")

        st.subheader("📋 Invoice Summary View")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Invoice Number", invoice_number)
        m_col2.metric("Total Calls Compiled", f"{invoice_data['total_calls']}")
        m_col3.metric("Total Charges Due", f"${invoice_data['total_amount']:.2f}")

        with open(pdf_file, "rb") as file:
            st.download_button(
                label="📥 Download Structured Invoice PDF",
                data=file,
                file_name=f"Invoice_{invoice_number}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )