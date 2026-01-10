import streamlit as st
from streamlit_option_menu import option_menu
import os,sys   
import rooms
import reserve
import manage


SIDEBAR_STYLES = {
    "nav-link-selected": {"background-color": "rgb(174,28,43)", "font-size": "17px", "font-weight": "bold", "color": "white"},
    "container": {"background-color": "transparent", "font-size": "17px"},
}

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-image: url("https://i.imgur.com/lbbGYKw.png");
            background-repeat: no-repeat;
            background-position: center top;
            padding-top: 80px;
            background-size: 178.6px 100px !important;
            width: 220px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    choice = option_menu(
        "",
        options=["Rooms", "Book", "View"],
        icons=["house", "calendar-plus", "gear"],
        default_index=0,
        styles=SIDEBAR_STYLES,
    )

if choice == "Rooms":
    rooms.app()
elif choice == "Book":
    reserve.app()
elif choice == "View":
    manage.app()
