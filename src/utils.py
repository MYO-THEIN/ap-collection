import streamlit as st
import numpy as np

@st.cache_resource
def get_postgresql_connection():
    conn = st.connection(name="postgresql", type="sql")
    return conn


def percentage_change(current, previous):
    return ((current - previous) / previous * 100) if previous else 100


@st.dialog("Confirm Action")
def confirmation_dialog(msg: str, yes_button_txt: str, no_button_txt: str):
    st.write(msg)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(yes_button_txt, key="confirm_btn", use_container_width=True):
            st.session_state["confirmed_action"] = True
            st.rerun()
    with col2:
        if st.button(no_button_txt, key="cancel_btn", use_container_width=True):
            st.session_state["confirmed_action"] = False
            st.rerun()


def build_receipt_html(order: dict, items: list):
    def fmt(n):
        return f"{n:,.0f}"

    items_rows = """
    <tr>
        <td style="text-align: left;">Description</td>
        <td style="text-align: right;">Quantity</td>
        <td style="text-align: right;">Amount</td>
    </tr>
    """
    
    for item in items:
        items_rows += f"""
        <tr>
            <td>
                {item['stock_category_name']}<br>
                {item['description']}
            </td>
            <td style="text-align: right;">{item['quantity']}</td>
            <td style="text-align: right;">{fmt(item['amount'])}</td>
        </tr>
        """

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Order Receipt</title>
        <style>
        @page {{ 
            size: 80mm auto; 
            margin: 4mm; 
        }}
        body {{
            font-family: Arial, sans-serif;
            width: 80mm;
            margin: 0;
            padding: 4px;
        }}
        h2 {{ 
            text-align: center; 
            margin-bottom: 4px; 
        }}
        p {{
            line-height: 1.5;
        }}
        table {{ 
            width: 100%; 
            font-size: 12px; 
            border-collapse: separate;
            border-spacing: 0 1em;
        }}
        td {{ 
            padding: 2px 0;
        }}
        .totals {{ 
            text-align: right; 
            margin-top: 8px; 
            font-weight: bold; 
        }}
        </style>
    </head>
    <body onload="window.print(); window.close();">
        <h2>AP Collections</h2>
        <div style="text-align: center; font-size: 11px;">Mandalay, Myanmar<br>Tel: +95 9 974568557</div>
      
        <p>
            <b>Date:</b> {order['date'].strftime('%d-%m-%Y')}<br>
            <b>Order No:</b> {order['order_no']}<br>
            <b>Customer:</b> {order['customer_name']}
        </p>
      
        <table>
            {items_rows}
        </table>

        <hr>
        <p>
            Total Quantity: {order['ttl_quantity']}<br>
            Total Amount: {fmt(order['ttl_amount'])}<br>
            Discount: {fmt(order['discount'])}<br>
            Delivery: {fmt(order['delivery_charges'])}<br>
            Paid Amount: {fmt(order['paid_amount'])}
        </p>

        <p style="text-align: center; font-size: 11px;">
            Thank you and have a nice day!
        </p>
    </body>
    </html>
    """
    return html
