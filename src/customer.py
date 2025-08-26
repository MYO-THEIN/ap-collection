import streamlit as st
import pandas as pd
from sqlalchemy import text
import src.utils as utils

if "postgresql" not in st.session_state:
    st.session_state["postgresql"] = utils.get_postgresql_connection()
postgresql = st.session_state["postgresql"]


def get_customers(search_term: str="", limit: int=None):
    with postgresql.session as session:
        if search_term:
            result = session.execute(
                text(
                    """
                    SELECT 
                        * 
                    FROM 
                        customers 
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
                        id DESC;
                    """
                ),
                {"search_term": f"%{search_term}%"}
            )
        else:
            result = session.execute(
                text("SELECT * FROM customers ORDER BY id DESC;")
            )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df if limit is None else df.iloc[:limit]


def get_customer_by_id(id: int):
    with postgresql.session as session:
        result = session.execute(
            text("SELECT * FROM customers WHERE id = :id;"),
            {"id": id}
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
        try:
            result = session.execute(
                text(
                    """
                    INSERT INTO customers (
                        serial_no, 
                        name, 
                        phone, 
                        home_address, 
                        delivery_address, 
                        city, 
                        state_region, 
                        country
                    ) 
                    VALUES (
                        :serial_no, 
                        :name, 
                        :phone, 
                        :home_address, 
                        :delivery_address, 
                        :city, 
                        :state_region, 
                        :country
                    )
                    RETURNING id;
                    """
                ), 
                {
                    "serial_no": serial_no, 
                    "name": name, 
                    "phone": phone, 
                    "home_address": home_address, 
                    "delivery_address": delivery_address,
                    "city": city, 
                    "state_region": state_region, 
                    "country": country
                }
            )

            new_id = result.scalar()
            if new_id is None:
                raise Exception("Cannot insert a customer.")
            
            session.commit()
            return {"success": True, "new_id": new_id}
        except Exception as e:
            print("Error occurred while inserting a customer: ", e)
            session.rollback()
            return {"success": False, "error": e}


def update_customer(id: int, serial_no: str, name: str, phone: str, home_address: str, delivery_address: str, city: str, state_region: str, country: str):
    if customer_exists(serial_no, name, exclude_id=id):
        st.warning("Serial No/Name already exists.")
        return False

    with postgresql.session as session:
        try:
            session.execute(
                text(
                    """
                    UPDATE 
                        customers
                    SET
                        serial_no = :serial_no,
                        name = :name,
                        phone = :phone,
                        home_address = :home_address,
                        delivery_address = :delivery_address,
                        city = :city,
                        state_region = :state_region,
                        country = :country 
                    WHERE 
                        id = :id;
                    """
                ), 
                {
                    "id": id, 
                    "serial_no": serial_no, 
                    "name": name, 
                    "phone": phone, 
                    "home_address": home_address, 
                    "delivery_address": delivery_address,
                    "city": city, 
                    "state_region": state_region, 
                    "country": country
                }
            )
            session.commit()
            return {"success": True}
        except Exception as e:
            print("Error occurred while updating a customer: ", e)
            session.rollback()
            return {"success": False, "error": e}


def delete_customer(id: int):
    with postgresql.session as session:
        try:
            session.execute(
                text("DELETE FROM customers WHERE id = :id;"), 
                {"id": id}
            )
            session.commit()
            return {"success": True}
        except Exception as e:
            print("Error occurred while deleting a customer: ", e)
            session.rollback()
            return {"success": False, "error": e}
