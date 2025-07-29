import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

# --- Session State Setup ---
if 'sale_details' not in st.session_state:
    st.session_state.sale_details = []

if 'sales' not in st.session_state:
    st.session_state.sales = []

# --- Sale Form ---
st.header("🧾 Sale Entry")

with st.form("sale_form", clear_on_submit=True):
    customer_name = st.text_input("Customer Name")
    sale_date = st.date_input("Sale Date", datetime.today())
    invoice_no = st.text_input("Invoice No", value=str(uuid.uuid4())[:8])

    submitted = st.form_submit_button("Start Sale")

if submitted:
    st.session_state.current_sale = {
        "invoice_no": invoice_no,
        "customer_name": customer_name,
        "sale_date": sale_date,
    }
    st.success(f"Sale Started for Invoice: {invoice_no}")

# --- Sale Detail Entry ---
if 'current_sale' in st.session_state:
    st.subheader("🧾 Add Sale Detail")

    with st.form("sale_detail_form", clear_on_submit=True):
        item = st.text_input("Item Name")
        qty = st.number_input("Quantity", min_value=1, value=1)
        price = st.number_input("Unit Price", min_value=0.0, format="%.2f")
        add_detail = st.form_submit_button("Add Item")

    if add_detail:
        detail = {
            "item": item,
            "qty": qty,
            "price": price,
            "total": qty * price
        }
        st.session_state.sale_details.append(detail)

# --- Show Sale Detail Table ---
if st.session_state.sale_details:
    st.subheader("📦 Sale Detail")
    detail_df = pd.DataFrame(st.session_state.sale_details)
    st.dataframe(detail_df)

    total = sum([d['total'] for d in st.session_state.sale_details])
    st.markdown(f"### 🧮 Total Amount: ${total:.2f}")

    if st.button("✅ Confirm Sale"):
        # Save Sale
        final_sale = {
            **st.session_state.current_sale,
            "details": st.session_state.sale_details,
            "total": total
        }
        st.session_state.sales.append(final_sale)
        st.success(f"Sale recorded for invoice: {final_sale['invoice_no']}")

        # Clear current session
        del st.session_state['sale_details']
        del st.session_state['current_sale']

# --- View All Sales ---
st.divider()
st.header("📋 All Sales")

if st.session_state.sales:
    for s in st.session_state.sales:
        st.markdown(f"**Invoice**: {s['invoice_no']} | **Customer**: {s['customer_name']} | **Total**: ${s['total']:.2f}")
        st.dataframe(pd.DataFrame(s['details']))
        st.markdown("---")
else:
    st.info("No sales recorded yet.")
