import streamlit as st

@st.cache_resource
def get_postgresql_connection():
    conn = st.connection(name="postgresql", type="sql")
    return conn


@st.dialog("Confirm Action")
def confirmation_dialog(msg: str, yes_button_txt: str, no_button_txt: str):
    st.write(msg)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(yes_button_txt, key="confirm_btn", use_container_width=True):
            st.session_state["confirmed_action"] = True
            st.rerun()
    with col2:
        if st.button(no_button_txt, key="cancel_btn", use_container_width=True):
            st.session_state["confirmed_action"] = False
            st.rerun()
