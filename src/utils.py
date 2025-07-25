import streamlit as st

@st.cache_resource
def get_postgresql_connection():
    conn = st.connection(name="postgresql", type="sql")
    return conn
