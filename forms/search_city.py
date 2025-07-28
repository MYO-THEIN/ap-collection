import streamlit as st
import pandas as pd
import json

with open("data/cities_states_regions.json", "r", encoding="utf-8") as f:
    json_data = json.load(f)

# State/Region
states_regions = sorted(list(json_data.keys()))

@st.dialog("### 🔎 Search City")
def search_city_modal(def_state: str="Mandalay Region", sel_state: str=None, sel_city: str=None):
    with st.container():
        state_region = st.selectbox(
            label="State/Region",
            options=states_regions,
            accept_new_options=False,
            index=states_regions.index(def_state) if sel_state is None else states_regions.index(sel_state)
        )

        cities = json_data[state_region]
        if cities:
            for city in cities:
                cols = st.columns([1, 1, 1])

                if city["english"] == sel_city:
                    cols[0].markdown(f"✔️ {city['english']}")
                    cols[1].markdown(f"✔️ {city['burmese']}")
                else:
                    cols[0].markdown(city['english'])
                    cols[1].markdown(city['burmese'])

                if cols[2].button("Select", key=f"select_{city['english']}"):
                    st.session_state["search_city"] = city["english"]
                    st.session_state["search_state_region"] = state_region
                    st.rerun()
        else:
            st.warning(f"No cities data available for {state_region}")

        st.divider()

        if st.button("❌ Close"):
            if sel_city is None:
                st.warning("Please select a city.")
            else:
                st.session_state["search_city"] = sel_city
                st.session_state["search_state_region"] = sel_state
                st.rerun()
