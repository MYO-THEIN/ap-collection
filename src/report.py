import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import text, bindparam
import src.utils as utils

if "postgresql" not in st.session_state:
    st.session_state["postgresql"] = utils.get_postgresql_connection()
postgresql = st.session_state["postgresql"]


def get_orders(dt: date):
    from_date = dt.strftime("%Y-%m-%d") + " 00:00:00"
    to_date = dt.strftime("%Y-%m-%d") + " 23:59:59"

    with postgresql.session as session:
        result = session.execute(
            text(
                """
                SELECT 
                    * 
                FROM 
                    v_orders_overall
                WHERE
                    date BETWEEN :from_date AND :to_date;
                """
            ),
            {
                "from_date": from_date,
                "to_date": to_date
            }
        )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df
