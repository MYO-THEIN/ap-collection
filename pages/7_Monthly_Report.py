import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import calendar
import src.utils as utils
from src.report import get_orders, get_expenses

st.set_page_config(layout="wide")

if "orders_data" in st.session_state:
    del st.session_state["orders_data"]

# Filters
st.sidebar.header("🔎 Filters")
filtered_year = st.sidebar.number_input(    
    label="Year",
    min_value=2025,
    value=date.today().year
)
filtered_month = st.sidebar.selectbox(
    label="Month",
    options=[f"{i:02d}" for i in range(1, 13)],
    format_func=lambda x: calendar.month_name[int(x)],
    index=date.today().month - 1
)
if filtered_year and filtered_month:
    # current month
    last_day_of_month = calendar.monthrange(int(filtered_year), int(filtered_month))[1]
    from_date = datetime.strptime(f"{filtered_year}-{filtered_month}-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    to_date = datetime.strptime(f"{filtered_year}-{filtered_month}-{last_day_of_month} 23:59:59", "%Y-%m-%d %H:%M:%S")
    orders_data = get_orders(from_date, to_date)
    
    # current expenses
    expenses_data = get_expenses(from_date, to_date)
    expenses_data = expenses_data.groupby(["expense_type_id", "expense_type_name"], as_index=False).sum("amount")

    # previous month
    prev_month = date(int(filtered_year), int(filtered_month), 1) - timedelta(days=1)
    from_date = datetime.strptime(f"{prev_month.year}-{prev_month.month}-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    to_date = datetime.strptime(f"{prev_month.year}-{prev_month.month}-{prev_month.day} 23:59:59", "%Y-%m-%d %H:%M:%S")
    prev_data = get_orders(from_date, to_date)

    prev_month_name = calendar.month_abbr[prev_month.month]
    current_month_name = calendar.month_abbr[int(filtered_month)]


# KPIs
def kpi_metrics():
    # Previous Month
    prev_orders = prev_data["id"].nunique()
    prev_quantity = prev_data["quantity"].sum()
    prev_revenue = prev_data.groupby("id")["paid_amount"].first().sum()

    # Current Month
    total_orders = orders_data["id"].nunique()
    total_quantity = orders_data["quantity"].sum()
    total_revenue = orders_data.groupby("id")["paid_amount"].first().sum()
    total_delivery_charges = orders_data.groupby("id")["delivery_charges"].first().sum()
    total_discount = orders_data.groupby("id")["discount"].first().sum()
    total_expenses = expenses_data["amount"].sum() if expenses_data.shape[0] else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric(
        "🧾 Orders", total_orders, 
        delta=f"{utils.percentage_change(total_orders, prev_orders):.2f}%",
        border=True
    )
    col2.metric(
        "📦 Quantity", total_quantity, 
        delta=f"{utils.percentage_change(total_quantity, prev_quantity):.2f}%",
        border=True
    )
    col3.metric(
        "💰 Revenue", f"{total_revenue / 1e5:.1f} L", 
        delta=f"{utils.percentage_change(total_revenue, prev_revenue):.2f}%",
        border=True
    )
    col4.metric(
        "🚚 Delivery Charges", f"{total_delivery_charges:,}",
        border=True
    )
    col5.metric(
        "➖ Discount", f"{total_discount:,}",
        border=True
    )
    col6.metric(
        "💸 Expenses", f"{total_expenses / 1e5:.1f} L",
        border=True
    )

    st.divider()


# Daily Quantity & Revenue
def daily_quantity_and_revenue():
    col1, col2 = st.columns(2)
    with col1:  
        # Quantity - Bar Chart
        agg_daily_quantity = orders_data.groupby(["date"]).agg({
            "quantity": "sum"
        }).reset_index()
        agg_daily_quantity.columns = ["Date", "Quantity"]

        st.markdown("📦 Daily Quantity")
        mean_value = agg_daily_quantity["Quantity"].mean()
        fig = px.bar(
            data_frame=agg_daily_quantity, 
            x="Date",
            y="Quantity",
            color_discrete_sequence=["#4daf4a"]
        ) \
        .update_traces(
            hovertemplate=(
                "<b>%{x|%m-%d}</b><br>"
                "Quantity: %{value}"
            )
        ) \
        .add_trace(
            go.Scatter(
                x=agg_daily_quantity["Date"],
                y=[mean_value] * len(agg_daily_quantity),
                mode="lines",
                line=dict(color="red", dash="dash"),
                name=f"Mean = {mean_value :.0f}",
                hovertemplate=f"Mean = {mean_value :.0f}"
            )
        ) \
        .update_layout(
            xaxis_tickformat="%m-%d",
            yaxis_tickformat=".0f",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue - Bar Chart
        agg_daily_revenue = orders_data.drop_duplicates(subset=["order_no"]).groupby(["date"]).agg({
            "paid_amount": "sum"
        }).reset_index()
        agg_daily_revenue.columns = ["Date", "Revenue"]

        st.markdown("💰 Daily Revenue")
        mean_value = agg_daily_revenue["Revenue"].mean()
        fig = px.bar(
            data_frame=agg_daily_revenue, 
            x="Date",
            y="Revenue",
            color_discrete_sequence=["#d62728"]
        ) \
        .update_traces(
            hovertemplate=(
                "<b>%{x|%m-%d}</b><br>"
                "Revenue: %{value}"
            )
        ) \
        .add_trace(
            go.Scatter(
                x=agg_daily_revenue["Date"],
                y=[mean_value] * len(agg_daily_revenue),
                mode="lines",
                line=dict(color="green", dash="dash"),
                name=f"Mean = {mean_value :,.0f}",
                hovertemplate=f"Mean = {mean_value :,.0f}"
            )
        ) \
        .update_layout(
            xaxis_tickformat="%m-%d",
            yaxis_tickformat=",.0f",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()


# Stock Category Insights
def quantity_and_amount_by_stock_category():
    agg_stock_category = orders_data.groupby(["stock_category_name"]).agg({
        "quantity": "sum",
        "amount": "sum"
    }).reset_index()
    agg_stock_category.columns = ["Stock Category", "Quantity", "Amount"]

    col1, col2 = st.columns(2)
    with col1:  
        # Quantity - Donut Chart
        st.markdown("📦 Quantity by Stock Category")
        pie_quantity_by_stock_category = px.pie(
            data_frame=agg_stock_category, 
            names="Stock Category", 
            values="Quantity",
            hole=0.4
        ) \
        .update_traces(
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Quantity: %{value}"
            )
        )
        st.plotly_chart(pie_quantity_by_stock_category, use_container_width=True)
    
    with col2:
        # Amount - Bar Chart
        st.markdown("💰 Amount by Stock Category")
        bar_amount_by_stock_category = px.bar(
            data_frame=agg_stock_category.sort_values(by="Amount", ascending=False), 
            x="Stock Category",
            y="Amount",
            color="Stock Category"
        ) \
        .update_layout(yaxis_tickformat=",.0f") \
        .update_traces(
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Amount: %{value}"
            )
        )
        st.plotly_chart(bar_amount_by_stock_category, use_container_width=True)

    st.divider()


# Payment Insights
def payment_insights():
    agg_payment_type = orders_data.drop_duplicates(subset=["order_no"]).groupby(["date", "payment_type_name"]).agg({
        "paid_amount": "sum"
    }).reset_index()

    # percent contribution
    agg_payment_type["total"] = agg_payment_type.groupby("date")["paid_amount"].transform("sum")
    agg_payment_type["percent"] = agg_payment_type["paid_amount"] / agg_payment_type["total"] * 100

    # formatted date
    agg_payment_type["date"] = pd.to_datetime(agg_payment_type["date"])
    agg_payment_type["formatted_date"] = agg_payment_type["date"].dt.strftime("%m-%d")

    agg_payment_type.columns = ["Date", "Payment Type", "Revenue", "Total", "Percent", "Formatted Date"]

    st.markdown("💳 Revenue by Payment Type")
    col1, col2 = st.columns([1, 2])
    with col1:
        # Sunburst Chart
        # aggregate at leaf level (Date + Payment Type)
        leaf_df = agg_payment_type.groupby(["Formatted Date", "Payment Type"], as_index=False)["Revenue"].sum()

        # aggregate parent level (Payment Type)
        parent_df = agg_payment_type.groupby("Payment Type", as_index=False)["Revenue"].sum()

        labels = []
        parents = []
        values = []
        hovertexts = []

        # parent nodes
        for _, row in parent_df.iterrows():
            labels.append(row["Payment Type"])
            parents.append("")  # No parent for top level
            values.append(row["Revenue"])
            hovertexts.append(
                f"<b>{row['Payment Type']}</b><br>Revenue: {row['Revenue']:,.0f}"
            )

        # leaf nodes
        for _, row in leaf_df.iterrows():
            labels.append(row["Formatted Date"])
            parents.append(row["Payment Type"])
            values.append(row["Revenue"])
            hovertexts.append(
                f"<b>{row['Formatted Date']}</b><br>"
                f"Revenue: {row['Revenue']:,.0f}<br>"
                f"Payment Type: {row['Payment Type']}"
            )

        sunburst_payment_type = go.Figure(
            go.Sunburst(
                labels=labels,
                parents=parents,
                values=values,
                hovertext=hovertexts,
                hoverinfo="text",
                branchvalues="total",
                insidetextorientation="radial",
                texttemplate="%{label}<br>%{value}"
            )
        ) \
        .update_layout(margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(sunburst_payment_type, use_container_width=True)

    with col2:
        # Stacked Bar Chart
        stack_order = (
            agg_payment_type.groupby("Payment Type")["Percent"].mean().sort_values(ascending=False).index.tolist()
        )

        stacked_bar_payment_type = px.bar(
            data_frame=agg_payment_type,
            x="Date",
            y="Percent",
            color="Payment Type",
            custom_data=["Formatted Date", "Payment Type", "Revenue", "Percent"],
            category_orders={"Payment Type": stack_order}
        ) \
        .update_layout(
            barmode="stack",
            xaxis={
                "tickformat": "%m-%d"
            }
        ) \
        .update_traces(
            hovertemplate=(
                "Date: %{customdata[0]}<br>"
                "Payment Type: %{customdata[1]}<br>"
                "Revenue: %{customdata[2]:,}<br>"
                "Percent: %{customdata[3]:.2f}%"
            )
        )
        st.plotly_chart(stacked_bar_payment_type, use_container_width=True)

    st.divider()


# Expense Insights
def expense_insights():
    if expenses_data.shape[0] == 0:
        return
    
    st.markdown("💸 Expenses by Type")
    col1, col2 = st.columns(2)
    
    with col1:
        df_treemap = expenses_data.copy()

        if expenses_data.shape[0] == 1:
            dummy_row = pd.DataFrame([{"expense_type_name": "dummy", "amount": 0}])
            df_treemap = pd.concat([expenses_data, dummy_row], ignore_index=True)

        # Treemap
        fig_treemap = px.treemap(
            df_treemap,  # expenses_data, 
            path=["expense_type_name"],
            values="amount"
        ).update_traces(
            hovertemplate=(
                "<b>%{label}</b><br>"
                "%{value:,.0f}"
            )
        )
        st.plotly_chart(fig_treemap, use_container_width=True)

    with col2:
        # Radar chart
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=expenses_data["amount"],
            theta=expenses_data["expense_type_name"],
            fill="toself",
            name="Expenses",
            hovertemplate="<b>%{theta}</b><br>%{r:,.0f}<extra></extra>"
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True))
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()


# This Month vs Last Month
def get_comparison_figure(df: pd.DataFrame, x_name: str, title: str, xaxis_title: str, yaxis_title: str, current_month_marker_color: str):
    fig = go.Figure()

    # bars
    fig.add_trace(
        go.Bar(
            name=prev_month_name, 
            x=df[x_name], 
            y=df[prev_month_name], 
            marker_color="lightslategray",
            hovertemplate=(
                "<b>%{x}</b><br>"
                f"<b>Month:</b> {prev_month_name}<br>"
                f"<b>{yaxis_title}:</b> " + "%{y}<extra></extra>"
            )
        )
    )
    fig.add_trace(
        go.Bar(
            name=current_month_name, 
            x=df[x_name], 
            y=df[current_month_name], 
            marker_color=current_month_marker_color,
            hovertemplate=(
                "<b>%{x}</b><br>"
                f"<b>Month:</b> {current_month_name}<br>"
                f"<b>{yaxis_title}:</b> " + "%{y}<extra></extra>"
            )
        )
    )

    # annotations for percentage change
    for _, row in df.iterrows():
        arrow_color = "green" if row["Pct Change"] >= 0 else "red"
        text_position = max(row[prev_month_name], row[current_month_name]) + 10
        if row["Pct Change"] >= 0:
            ax_offset, ay_offset = -20, 20
        else:
            ax_offset, ay_offset = -20, -20

        fig.add_annotation(
            x=row[x_name], 
            y=text_position, 
            text=f"{row['Pct Change'] :+.2f}%", 
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor=arrow_color,
            ax=ax_offset,
            ay=ay_offset,
            font=dict(color="black", size=12)
        )

    fig.update_layout(
        title=title,
        barmode="group",
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        yaxis_tickformat=",.0f"
    )

    return fig


def this_month_vs_last_month():
    if not prev_data.shape[0]:
        return

    st.markdown("🆚 This Month vs Last Month")

    agg_prev_month, agg_current_month = pd.DataFrame(), pd.DataFrame()
    if prev_data.shape[0]:
        agg_prev_month = prev_data.groupby(["stock_category_name"]).agg({
            "quantity": "sum",
            "amount": "sum"
        }).reset_index()
    if orders_data.shape[0]:
        agg_current_month = orders_data.groupby(["stock_category_name"]).agg({
            "quantity": "sum",
            "amount": "sum"
        }).reset_index()

    comp_data = pd.merge(
        agg_prev_month, agg_current_month, 
        on="stock_category_name", 
        suffixes=("_prev", "_current")
    )
    
    tab1, tab2, tab3 = st.tabs(["📦 Quantity", "💰 Amount", "💰 Revenue"])

    with tab1:
        # Quantity Change
        comp_data_quantity = comp_data[["stock_category_name", "quantity_prev", "quantity_current"]]
        comp_data_quantity.columns = ["Stock Category", prev_month_name, current_month_name]
        comp_data_quantity["Change"] = comp_data_quantity[current_month_name] - comp_data_quantity[prev_month_name]
        comp_data_quantity["Pct Change"] = comp_data_quantity["Change"] / comp_data_quantity[prev_month_name] * 100
        
        fig_quantity = get_comparison_figure(
            df=comp_data_quantity,
            x_name="Stock Category",
            title=f"Quantity Change: {prev_month_name} vs {current_month_name}",
            xaxis_title="Stock Category",
            yaxis_title="Quantity",
            current_month_marker_color="#4daf4a"
        )
        st.plotly_chart(fig_quantity, use_container_width=True)

    with tab2:
        # Amount Change
        comp_data_amount = comp_data[["stock_category_name", "amount_prev", "amount_current"]]
        comp_data_amount.columns = ["Stock Category", prev_month_name, current_month_name]
        comp_data_amount["Change"] = comp_data_amount[current_month_name] - comp_data_amount[prev_month_name]
        comp_data_amount["Pct Change"] = comp_data_amount["Change"] / comp_data_amount[prev_month_name] * 100
        
        fig_amount = get_comparison_figure(
            df=comp_data_amount,
            x_name="Stock Category",
            title=f"Amount Change: {prev_month_name} vs {current_month_name}",
            xaxis_title="Stock Category",
            yaxis_title="Amount",
            current_month_marker_color="#d62728"
        )
        st.plotly_chart(fig_amount, use_container_width=True)

    with tab3:
        # Revenue Change
        agg_prev_month, agg_current_month = pd.DataFrame(), pd.DataFrame()
        if prev_data.shape[0]:
            agg_prev_month = prev_data.drop_duplicates(subset=["order_no"]).groupby(["payment_type_name"]).agg({
                "paid_amount": "sum"
            }).reset_index()
        if orders_data.shape[0]:
            agg_current_month = orders_data.drop_duplicates(subset=["order_no"]).groupby(["payment_type_name"]).agg({
                "paid_amount": "sum"
            }).reset_index()

        comp_data = pd.merge(
            agg_prev_month, agg_current_month, 
            on="payment_type_name", 
            suffixes=("_prev", "_current")
        )

        comp_data.columns = ["Payment Type", prev_month_name, current_month_name]
        comp_data["Change"] = comp_data[current_month_name] - comp_data[prev_month_name]
        comp_data["Pct Change"] = comp_data["Change"] / comp_data[prev_month_name] * 100
        
        fig_revenue = get_comparison_figure(
            df=comp_data,
            x_name="Payment Type",
            title=f"Revenue Change: {prev_month_name} vs {current_month_name}",
            xaxis_title="Payment Type",
            yaxis_title="Revenue",
            current_month_marker_color="#1f77b4"
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    st.divider()


# Monthly Summary
def monthly_summary():
    st.markdown("📋 Monthly Summary")
    
    tab1, tab2, tab3 = st.tabs(["Orders", "Payment Types", "Stock Categories"])
    with tab1:
        summary_df = orders_data \
            .drop_duplicates(subset=["order_no"]) \
            .groupby(["date"]) \
            .agg(
                orders=("order_no", "count"),
                quantity=("ttl_quantity", "sum"),
                discount=("discount", "sum"),
                delivery_charges=("delivery_charges", "sum"),
                paid_amount=("paid_amount", "sum")
            ) \
            .reset_index()

        summary_df.columns = ["Date", "Orders", "Quantity", "Discount", "Delivery Charges", "Paid Amount"]

        # format the numbers
        summary_df = summary_df.style.format({
            "Discount": "{:,.0f}",
            "Delivery Charges": "{:,.0f}",
            "Paid Amount": "{:,.0f}"
        })

        st.dataframe(
            data=summary_df,
            column_config={
                "Date": st.column_config.DateColumn(label="Date", disabled=True, format="MM-DD"),
                "Orders": st.column_config.Column(label="Orders", disabled=True),
                "Quantity": st.column_config.Column(label="Quantity", disabled=True),
                "Discount": st.column_config.NumberColumn(label="Discount", disabled=True),
                "Delivery Charges": st.column_config.NumberColumn(label="Delivery Charges", disabled=True),
                "Paid Amount": st.column_config.NumberColumn(label="Paid Amount", disabled=True)
            },
            hide_index=True, 
            use_container_width=True
        )

    with tab2:
        summary_df = orders_data \
            .drop_duplicates(subset=["order_no"]) \
            .groupby(["date", "payment_type_name"]) \
            .agg(
                paid_amount=("paid_amount", "sum")
            ) \
            .reset_index()

        summary_df.columns = ["Date", "Payment Type", "Paid Amount"]

        # format the numbers
        summary_df = summary_df.style.format({
            "Paid Amount": "{:,.0f}"
        })

        st.dataframe(
            data=summary_df,
            column_config={
                "Date": st.column_config.DateColumn(label="Date", disabled=True, format="MM-DD"),
                "Payment Type": st.column_config.Column(label="Payment Type", disabled=True),
                "Paid Amount": st.column_config.NumberColumn(label="Paid Amount", disabled=True)
            },
            hide_index=True, 
            use_container_width=True
        )

    with tab3:
        summary_df = orders_data \
            .groupby(["date", "stock_category_name"]) \
            .agg(
                quantity=("quantity", "sum"),
                amount=("amount", "sum")
            ) \
            .reset_index()

        summary_df.columns = ["Date", "Stock Category", "Quantity", "Amount"]

        # format the numbers
        summary_df = summary_df.style.format({
            "Amount": "{:,.0f}"
        })

        st.dataframe(
            data=summary_df,
            column_config={
                "Date": st.column_config.DateColumn(label="Date", disabled=True, format="MM-DD"),
                "Stock Category": st.column_config.Column(label="Stock Category", disabled=True),
                "Quantity": st.column_config.Column(label="Quantity", disabled=True),
                "Amount": st.column_config.NumberColumn(label="Amount", disabled=True)
            },
            hide_index=True, 
            use_container_width=True
        )


if orders_data.shape[0]:
    st.title("🗓️ Monthly Report")
    st.markdown(f"### Month: `{filtered_year}-{filtered_month}`")

    kpi_metrics()
    daily_quantity_and_revenue()
    quantity_and_amount_by_stock_category()
    payment_insights()
    expense_insights()
    this_month_vs_last_month()
    monthly_summary()
else:
    st.info("No data available 📭")
