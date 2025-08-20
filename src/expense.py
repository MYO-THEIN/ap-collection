import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from sqlalchemy import text, bindparam
import src.utils as utils

if "postgresql" not in st.session_state:
    st.session_state["postgresql"] = utils.get_postgresql_connection()
postgresql = st.session_state["postgresql"]


def get_expenses(from_date: date, to_date: date, search_term: str=""):
    if from_date is not None and to_date is not None:
        from_date = from_date.strftime("%Y-%m-%d") + " 00:00:00"
        to_date = to_date.strftime("%Y-%m-%d") + " 23:59:59"

    with postgresql.session as session:
        if search_term:
            result = session.execute(
                text(
                    """
                    SELECT 
                        *
                    FROM 
                        v_expenses
                    WHERE
                        expense_type_name ILIKE :search_term
                        OR description ILIKE :search_term
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
                        v_expenses
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


def add_expense(expense: dict):
    with postgresql.session as session:
        try:
            result = session.execute(
                text(
                    """
                    INSERT INTO expenses (
                        date, 
                        expense_type_id,
                        description,
                        amount
                    )
                    VALUES (
                        :date, 
                        :expense_type_id,
                        :description,
                        :amount
                    )
                    RETURNING id;
                    """
                ), 
                {
                    "date": expense["date"], 
                    "expense_type_id": expense["expense_type_id"],
                    "description": expense["description"],
                    "amount": expense["amount"]
                }
            )

            new_id = result.scalar()
            if new_id is None:
                raise Exception("Cannot insert an expense.")

            session.commit()
            return True
        except Exception as e:
            print("Error occurred while inserting an expense: ", e)
            session.rollback()
            return False


def update_expense(expense: dict):
    with postgresql.session as session:
        try:
            session.execute(
                text(
                    """
                    UPDATE 
                        expenses
                    SET
                        date = :date,
                        expense_type_id = :expense_type_id,
                        description = :description,
                        amount = :amount
                    WHERE
                        id = :id;
                    """
                ), 
                {
                    "id": expense["id"], 
                    "date": expense["date"], 
                    "expense_type_id": expense["expense_type_id"],
                    "description": expense["description"],
                    "amount": expense["amount"]
                }
            )
  
            session.commit()
            return True
        except Exception as e:
            print("Error occurred while updating an expense: ", e)
            session.rollback()
            return False


def delete_expense(id: int):
    with postgresql.session as session:
        try:
            session.execute(
                text("DELETE FROM expenses WHERE id = :id;"), 
                {"id": id}
            )

            session.commit()
            return True
        except Exception as e:
            print("Error occurred while deleting an expense: ", e)
            session.rollback()
            return False
