import streamlit as st
import pandas as pd
from sqlalchemy import text
import src.utils as utils

if "postgresql" not in st.session_state:
    st.session_state["postgresql"] = utils.get_postgresql_connection()
postgresql = st.session_state["postgresql"]


def get_customers(search_term: str=""):
    with postgresql.session as session:
        if search_term:
            result = session.execute(
                text(
                    """
                    SELECT * 
                    FROM customers 
                    WHERE 
                        serial_no ILIKE :search_term 
                        OR name ILIKE :search_term
                        OR phone ILIKE :search_term
                        OR home_address ILIKE :search_term
                        OR delivery_address ILIKE :search_term
                        OR city ILIKE :search_term
                        OR state_region ILIKE :search_term
                        OR country ILIKE :search_term
                    ORDER BY 
                        serial_no,
                        name;
                    """
                ),
                {"search_term": f"%{search_term}%"}
            )
        else:
            result = session.execute(
                text("SELECT * FROM customers ORDER BY serial_no, name;")
            )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df
    

def customer_exists(serial_no: str, name: str, exclude_id: int=None):
    with postgresql.session as session:
        if exclude_id:
            result = session.execute(
                text(
                    """
                    SELECT 1 
                    FROM customers 
                    WHERE 
                        LOWER(serial_no) = LOWER(:serial_no)
                        AND id != :id;
                    """
                ), 
                {"id": exclude_id, "serial_no": serial_no, "name": name}
            )
        else:
            result = session.execute(
                text("SELECT 1 FROM customers WHERE LOWER(serial_no) = LOWER(:serial_no);"), 
                {"serial_no": serial_no, "name": name}
            )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df.shape[0] > 0


def add_customer(serial_no: str, name: str, phone: str, home_address: str, delivery_address: str, city: str, state_region: str, country: str):
    if customer_exists(serial_no, name):
        st.warning("Serial No/Name already exists.")
        return False

    with postgresql.session as session:
        session.execute(
            text(
                """
                INSERT INTO customers (serial_no, name, phone, home_address, delivery_address, city, state_region, country) 
                VALUES (:serial_no, :name, :phone, :home_address, :delivery_address, :city, :state_region, :country);
                """
            ), 
            {
                "serial_no": serial_no, "name": name, "phone": phone, "home_address": home_address, "delivery_address": delivery_address,
                "city": city, "state_region": state_region, "country": country
            }
        )
        session.commit()
        return True


def update_customer(id: int, serial_no: str, name: str, phone: str, home_address: str, delivery_address: str, city: str, state_region: str, country: str):
    if customer_exists(serial_no, name, exclude_id=id):
        st.warning("Serial No/Name already exists.")
        return False

    with postgresql.session as session:
        session.execute(
            text(
                """
                UPDATE customers
                SET
                    serial_no = :serial_no,
                    name = :name,
                    phone = :phone,
                    home_address = :home_address,
                    delivery_address = :delivery_address,
                    city = :city,
                    state_region = :state_region,
                    country = :country 
                WHERE id = :id;
                """
            ), 
            {
                "id": id, "serial_no": serial_no, "name": name, "phone": phone, "home_address": home_address, "delivery_address": delivery_address,
                "city": city, "state_region": state_region, "country": country
            }
        )
        session.commit()
        return True


def delete_customer(id: int):
    with postgresql.session as session:
        session.execute(
            text("DELETE FROM customers WHERE id = :id;"), 
            {"id": id}
        )
        session.commit()
        return True
