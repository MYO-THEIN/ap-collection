import streamlit as st
import pandas as pd
from sqlalchemy import text
import src.utils as utils

if "postgresql" not in st.session_state:
    st.session_state["postgresql"] = utils.get_postgresql_connection()
postgresql = st.session_state["postgresql"]


def get_payment_types(search_term: str=""):
    with postgresql.session as session:
        if search_term:
            result = session.execute(
                text("SELECT * FROM payment_types WHERE name ILIKE :search_term ORDER BY name;"),
                {"search_term": f"%{search_term}%"}
            )
        else:
            result = session.execute(
                text("SELECT * FROM payment_types ORDER BY name;")
            )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df
    

def name_exists(name: str, exclude_id: int=None):
    with postgresql.session as session:
        if exclude_id:
            result = session.execute(
                text("SELECT 1 FROM payment_types WHERE LOWER(name) = LOWER(:name) AND id != :id;"), 
                {"id": exclude_id, "name": name}
            )
        else:
            result = session.execute(
                text("SELECT 1 FROM payment_types WHERE LOWER(name) = LOWER(:name);"), 
                {"name": name}
            )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df.shape[0] > 0


def add_payment_type(name: str):
    if name_exists(name):
        st.warning("Name already exists.")
        return False

    with postgresql.session as session:
        session.execute(
            text("INSERT INTO payment_types (name) VALUES (:name);"), 
            {"name": name}
        )
        session.commit()
        return True


def update_payment_type(id: int, name: str):
    if name_exists(name, exclude_id=id):
        st.warning("Name already exists.")
        return False

    with postgresql.session as session:
        session.execute(
            text("UPDATE payment_types SET name = :name WHERE id = :id;"), 
            {"id": id, "name": name}
        )
        session.commit()
        return True


def delete_payment_type(id: int):
    with postgresql.session as session:
        session.execute(
            text("DELETE FROM payment_types WHERE id = :id;"), 
            {"id": id}
        )
        session.commit()
        return True
