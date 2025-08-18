import streamlit as st
import pandas as pd
from sqlalchemy import text, bindparam
import src.utils as utils

if "postgresql" not in st.session_state:
    st.session_state["postgresql"] = utils.get_postgresql_connection()
postgresql = st.session_state["postgresql"]

def get_users():
    with postgresql.session as session:
        result = session.execute(
            text(
                """
                SELECT 
                    u.id AS user_id,
                    u.user_name,
                    u.password,
                    u.role_id,
                    r.name AS role_name,
                    rp.permissions
                FROM 
                    users AS u
                    INNER JOIN roles AS r ON u.role_id = r.id
                    INNER JOIN role_permissions AS rp ON r.id = rp.role_id;
                """
            )
        )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df
