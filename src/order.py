import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import text
import src.utils as utils

if "postgresql" not in st.session_state:
    st.session_state["postgresql"] = utils.get_postgresql_connection()
postgresql = st.session_state["postgresql"]


def get_orders(dt: date, search_term: str=""):
    from_date = dt.strftime("%Y-%m-%d") + " 00:00:00"
    to_date = dt.strftime("%Y-%m-%d") + " 23:59:59"

    with postgresql.session as session:
        if search_term:
            result = session.execute(
                text(
                    """
                    SELECT * 
                    FROM v_orders
                    WHERE
                        (date BETWEEN :from_date AND :to_date)
                        AND 
                        (order_no ILIKE :search_term
                        OR customer_serial_no ILIKE :search_term
                        OR customer_name ILIKE :search_term
                        OR customer_phone ILIKE :search_term
                        OR customer_city ILIKE :search_term
                        OR customer_state_region ILIKE :search_term
                        OR customer_country ILIKE :search_term
                        OR payment_type_name ILIKE :search_term)
                    ORDER BY 
                        date DESC;
                    """
                ),
                {
                    "from_date": from_date,
                    "to_date": to_date,
                    "search_term": f"%{search_term}%"
                }
            )
        else:
            result = session.execute(
                text("SELECT * FROM v_orders ORDER BY date DESC;")
            )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df


def get_order_items(dt: date, order_ids: list):
    from_date = dt.strftime("%Y-%m-%d") + " 00:00:00"
    to_date = dt.strftime("%Y-%m-%d") + " 23:59:59"

    with postgresql.session as session:
        if order_ids:
            result = session.execute(
                text(
                    """
                    SELECT * 
                    FROM v_order_items
                    WHERE order_id IN (:order_ids);
                    """
                ),
                {"order_ids": ",".join(order_ids)}
            )
        else:
            result = session.execute(
                text(
                    """
                    SELECT * 
                    FROM v_order_items
                    WHERE 
                        order_id IN (
                            SELECT id
                            FROM orders
                            WHERE date BETWEEN :from_date AND :to_date
                        );
                    """
                ),
                {"from_date": from_date, "to_date": to_date}
            )
    
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df


def order_no_exists(order_no: str, exclude_id: int=None):
    with postgresql.session as session:
        if exclude_id:
            result = session.execute(
                text(
                    """
                    SELECT 1 
                    FROM orders
                    WHERE 
                        LOWER(order_no) = LOWER(:order_no)
                        AND id != :id;
                    """
                ), 
                {"id": exclude_id, "order_no": order_no}
            )
        else:
            result = session.execute(
                text("SELECT 1 FROM orders WHERE LOWER(order_no) = LOWER(:order_no);"), 
                {"order_no": order_no}
            )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df.shape[0] > 0


def get_id_by_order_no(order_no: str):
    with postgresql.session as session:
        result = session.execute(
            text(
                """
                SELECT *
                FROM orders 
                WHERE order_no = :order_no;
                """
            ),
            {"order_no": order_no}
        )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df


def add_order(order: dict, order_items: list):
    if order_no_exists(order["order_no"]):
        st.warning("Order No. already exists.")
        return False

    with postgresql.session as session:
        # order
        session.execute(
            text(
                """
                INSERT INTO orders (date, order_no, customer_id, ttl_quantity, ttl_amount, discount, sub_total, delivery_address, delivery_charges, payment_type_id)
                VALUES (:date, :order_no, :customer_id, :ttl_quantity, :ttl_amount, :discount, :sub_total, :delivery_address, :delivery_charges, :payment_type_id);
                """
            ), 
            {
                "date": order["date"], 
                "order_no": order["order_no"], 
                "customer_id": order["customer_id"], 
                "ttl_quantity": order["ttl_quantity"], 
                "ttl_amount": order["ttl_amount"], 
                "discount": order["discount"], 
                "sub_total": order["sub_total"],
                "delivery_address": order["delivery_address"], 
                "delivery_charges": order["delivery_charges"], 
                "payment_type_id": order["payment_type_id"]
            }
        )
        session.commit()

        # get the id by order_no
        new_id = get_id_by_order_no(order["order_no"])

        # order_items
        for item in order_items:
            add_order_item(session, order_id=new_id, item=item)
        session.commit()
        return True


def update_order(order: dict, order_items: list):
    if order_no_exists(order["order_no"], exclude_id=id):
        st.warning("Order No. already exists.")
        return False

    with postgresql.session as session:
        # order
        session.execute(
            text(
                """
                UPDATE orders
                SET
                    date = :date,
                    order_no = :order_no,
                    customer_id = :customer_id,
                    ttl_quantity = :ttl_quantity,
                    ttl_amount = :ttl_amount,
                    discount = :discount,
                    sub_total = :sub_total,
                    delivery_address = :delivery_address,
                    delivery_charges = :delivery_charges,
                    payment_type_id = :payment_type_id
                WHERE id = :id;
                """
            ), 
            {
                "id": order["id"], 
                "date": order["date"], 
                "order_no": order["order_no"], 
                "customer_id": order["customer_id"], 
                "ttl_quantity": order["ttl_quantity"], 
                "ttl_amount": order["ttl_amount"], 
                "discount": order["discount"], 
                "sub_total": order["sub_total"],
                "delivery_address": order["delivery_address"], 
                "delivery_charges": order["delivery_charges"], 
                "payment_type_id": order["payment_type_id"]
            }
        )

        # order_items
        delete_order_items(session, order_id=order["id"])
        for item in order_items:
            add_order_item(session, order_id=order["id"], item=item)
        
        session.commit()
        return True


def delete_order(id: int):
    with postgresql.session as session:
        # order_items
        delete_order_items(session, order_id=id)

        # order
        session.execute(
            text("DELETE FROM orders WHERE id = :id;"), 
            {"id": id}
        )

        session.commit()
        return True


def add_order_item(session, order_id: int, item: dict):
    session.execute(
        text(
            """
            INSERT INTO order_items (order_id, stock_category_id, quantity, amount)
            VALUES (:order_id, :stock_category_id, :quantity, :amount);
            """
        ), 
        {
            "order_id": order_id, "stock_category_id": item["stock_category_id"], "quantity": item["quantity"], "amount": item["amount"]
        }
    )


def delete_order_items(session, order_id: int):
    session.execute(
        text("DELETE FROM order_items WHERE order_id = :order_id;"), 
        {"order_id": order_id}
    )
