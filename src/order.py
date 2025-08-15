import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from sqlalchemy import text, bindparam
import src.utils as utils

if "postgresql" not in st.session_state:
    st.session_state["postgresql"] = utils.get_postgresql_connection()
postgresql = st.session_state["postgresql"]


def get_orders(dt: date, search_term: str=""):
    if dt is not None:
        from_date = dt.strftime("%Y-%m-%d") + " 00:00:00"
        to_date = dt.strftime("%Y-%m-%d") + " 23:59:59"

    with postgresql.session as session:
        if search_term:
            result = session.execute(
                text(
                    """
                    SELECT 
                        *
                    FROM 
                        v_orders
                    WHERE
                        order_no ILIKE :search_term
                        OR customer_serial_no ILIKE :search_term
                        OR customer_name ILIKE :search_term
                        OR customer_phone ILIKE :search_term
                        OR customer_city ILIKE :search_term
                        OR customer_state_region ILIKE :search_term
                        OR customer_country ILIKE :search_term
                        OR payment_type_name ILIKE :search_term
                        OR delivery_address ILIKE :search_term
                    ORDER BY 
                        date DESC, id DESC;
                    """
                ),
                {
                    "search_term": f"%{search_term}%"
                }
            )

        else:
            result = session.execute(
                text(
                    """
                    SELECT 
                        * 
                    FROM 
                        v_orders
                    WHERE
                        date BETWEEN :from_date AND :to_date
                    ORDER BY 
                        date DESC, id DESC;
                    """
                ),
                {
                    "from_date": from_date,
                    "to_date": to_date
                }
            )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df


def get_order_items(dt: date, order_ids: list):
    if dt is not None:
        from_date = dt.strftime("%Y-%m-%d") + " 00:00:00"
        to_date = dt.strftime("%Y-%m-%d") + " 23:59:59"

    with postgresql.session as session:
        if order_ids:
            result = session.execute(
                text(
                    """
                    SELECT 
                        * 
                    FROM 
                        v_order_items
                    WHERE 
                        order_id IN :order_ids;
                    """
                ).bindparams(
                    bindparam("order_ids", expanding=True)
                ),
                {"order_ids": order_ids}
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
                {
                    "from_date": from_date, 
                    "to_date": to_date
                }
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


def add_order(order: dict, order_items: list):
    if order_no_exists(order["order_no"]):
        st.warning("Order No. already exists.")
        return False

    with postgresql.session as session:
        try:
            # order
            result = session.execute(
                text(
                    """
                    INSERT INTO orders (
                        date, 
                        order_no, 
                        customer_id, 
                        ttl_quantity, 
                        ttl_amount, 
                        discount, 
                        sub_total, 
                        delivery_address, 
                        delivery_charges, 
                        payment_type_id,
                        paid_amount,
                        measurement,
                        is_delivered,
                        delivery_date
                    )
                    VALUES (
                        :date, 
                        :order_no, 
                        :customer_id, 
                        :ttl_quantity, 
                        :ttl_amount, 
                        :discount, 
                        :sub_total, 
                        :delivery_address, 
                        :delivery_charges, 
                        :payment_type_id,
                        :paid_amount,
                        :measurement,
                        :is_delivered,
                        :delivery_date
                    )
                    RETURNING id;
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
                    "payment_type_id": order["payment_type_id"],
                    "paid_amount": order["paid_amount"],
                    "measurement": order["measurement"],
                    "is_delivered": order["is_delivered"],
                    "delivery_date": order["delivery_date"]
                }
            )

            new_id = result.scalar()
            if new_id is None:
                raise Exception("Cannot insert an order.")

            # order_items
            for item in order_items:
                add_order_item(session, order_id=new_id, item=item)

            session.commit()
            return True
        except Exception as e:
            print("Error occurred while inserting an order: ", e)
            session.rollback()
            return False


def update_order(order: dict, order_items: list):
    if order_no_exists(order["order_no"], exclude_id=order["id"]):
        st.warning("Order No. already exists.")
        return False

    with postgresql.session as session:
        try:
            # order
            session.execute(
                text(
                    """
                    UPDATE 
                        orders
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
                        payment_type_id = :payment_type_id,
                        paid_amount = :paid_amount,
                        measurement = :measurement,
                        is_delivered = :is_delivered,
                        delivery_date = :delivery_date
                    WHERE
                        id = :id;
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
                    "payment_type_id": order["payment_type_id"],
                    "paid_amount": order["paid_amount"],
                    "measurement": order["measurement"],
                    "is_delivered": order["is_delivered"],
                    "delivery_date": order["delivery_date"]
                }
            )

            # order_items
            delete_order_items(session, order_id=order["id"])
            for item in order_items:
                add_order_item(session, order_id=order["id"], item=item)
            
            session.commit()
            return True
        except Exception as e:
            print("Error occurred while updating an order: ", e)
            session.rollback()
            return False


def delete_order(id: int):
    with postgresql.session as session:
        try:
            # order_items
            delete_order_items(session, order_id=id)

            # order
            session.execute(
                text("DELETE FROM orders WHERE id = :id;"), 
                {"id": id}
            )

            session.commit()
            return True
        except Exception as e:
            print("Error occurred while deleting an order: ", e)
            session.rollback()
            return False


def add_order_item(session, order_id: int, item: dict):
    session.execute(
        text(
            """
            INSERT INTO order_items (
                order_id, 
                stock_category_id, 
                quantity, 
                amount,
                description,
                price,
                extra
            )
            VALUES (
                :order_id, 
                :stock_category_id, 
                :quantity, 
                :amount,
                :description,
                :price,
                :extra
            );
            """
        ), 
        {
            "order_id": order_id, 
            "stock_category_id": item["stock_category_id"], 
            "quantity": item["quantity"], 
            "amount": item["amount"],
            "description": item["description"],
            "price": item["price"],
            "extra": item["extra"]
        }
    )


def delete_order_items(session, order_id: int):
    session.execute(
        text("DELETE FROM order_items WHERE order_id = :order_id;"), 
        {"order_id": order_id}
    )


# delivery
def get_undelivered_orders(due_date: date=None, order_date_from: date=None, order_date_to: date=None, search_term: str=None):
    today = datetime.now().strftime("%Y-%m-%d")

    with postgresql.session as session:
        # Due Date
        if due_date:
            result = session.execute(
                text(
                    """
                    SELECT
                        *
                    FROM
                        v_orders
                    WHERE
                        is_delivered = false
                        AND
                        delivery_date <= :due_date
                    ORDER BY
                        delivery_date ASC;
                    """
                ),
                {
                    "due_date": due_date
                }
            )

        # Order Date Range
        elif order_date_from and order_date_to:
            result = session.execute(
                text(
                    """
                    SELECT
                        *
                    FROM
                        v_orders
                    WHERE
                        is_delivered = false
                        AND
                        date BETWEEN :from_date AND :to_date
                    ORDER BY
                        delivery_date ASC;
                    """
                ),
                {
                    "from_date": order_date_from,
                    "to_date": order_date_to
                }
            )

        # Search Term
        elif search_term:
            result = session.execute(
                text(
                    """
                    SELECT 
                        *
                    FROM 
                        v_orders
                    WHERE
                        is_delivered = false
                        AND 
                        (order_no ILIKE :search_term
                        OR customer_serial_no ILIKE :search_term
                        OR customer_name ILIKE :search_term
                        OR customer_phone ILIKE :search_term
                        OR customer_city ILIKE :search_term
                        OR customer_state_region ILIKE :search_term
                        OR customer_country ILIKE :search_term
                        OR payment_type_name ILIKE :search_term
                        OR delivery_address ILIKE :search_term)
                    ORDER BY 
                        delivery_date ASC;
                    """
                ),
                {
                    "search_term": f"%{search_term}%"
                }
            )

        else:
            result = session.execute(
                text(
                    """
                    SELECT 
                        * 
                    FROM 
                        v_orders
                    WHERE
                        is_delivered = false
                        AND delivery_date <= :today
                    ORDER BY 
                        delivery_date ASC;
                    """
                ),
                {
                    "today": today
                }
            )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df


def update_delivery_status(id: int, is_delivered: bool, delivery_date: date):
    with postgresql.session as session:
        try:
            session.execute(
                text(
                    """
                    UPDATE 
                        orders
                    SET
                        is_delivered = :is_delivered,
                        delivery_date = :delivery_date
                    WHERE
                        id = :id;
                    """
                ), 
                {
                    "id": id, 
                    "is_delivered": is_delivered,
                    "delivery_date": delivery_date
                }
            )
            
            session.commit()
            return True
        except Exception as e:
            print("Error occurred while updating an order: ", e)
            session.rollback()
            return False


def get_delivered_orders(from_date: date, to_date: date, search_term: str=None):
    with postgresql.session as session:
        # Search Term
        if search_term:
            result = session.execute(
                text(
                    """
                    SELECT 
                        o.delivery_date,
                        o.date,
                        o.order_no,
                        o.customer_serial_no,
                        o.customer_name,
                        oi.stock_category_name,
                        oi.description,
                        oi.quantity
                    FROM
                        v_orders AS o
                        INNER JOIN v_order_items AS oi 
                        ON o.id = oi.order_id
                    WHERE
                        o.is_delivered = true
                        AND 
                        (o.order_no ILIKE :search_term
                        OR o.customer_serial_no ILIKE :search_term
                        OR o.customer_name ILIKE :search_term
                        OR o.customer_phone ILIKE :search_term
                        OR o.customer_city ILIKE :search_term
                        OR o.customer_state_region ILIKE :search_term
                        OR o.customer_country ILIKE :search_term
                        OR o.payment_type_name ILIKE :search_term
                        OR o.delivery_address ILIKE :search_term)
                    ORDER BY 
                        o.delivery_date ASC, o.id;
                    """
                ),
                {
                    "search_term": f"%{search_term}%"
                }
            )

        # Date Range
        else:
            result = session.execute(
                text(
                    """
                    SELECT 
                        o.delivery_date,
                        o.date,
                        o.order_no,
                        o.customer_serial_no,
                        o.customer_name,
                        oi.stock_category_name,
                        oi.description,
                        oi.quantity
                    FROM
                        v_orders AS o
                        INNER JOIN v_order_items AS oi 
                        ON o.id = oi.order_id
                    WHERE
                        o.is_delivered = true
                        AND
                        (delivery_date BETWEEN :from_date AND :to_date)
                    ORDER BY 
                        o.delivery_date ASC, o.id;
                    """
                ),
                {
                    "from_date": from_date,
                    "to_date": to_date
                }
            )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df
