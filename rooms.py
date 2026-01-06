
import streamlit as st
from typing import Optional
import db
import pandas as pd

st.set_page_config(page_title="Rooms", layout="wide")
DB_PATH = "data.db"

def room_card(name: str, img_url: Optional[str], description: Optional[str], details: list[dict]):
    details_html = "".join(
        f"<div class='detail-box'><img src='{i['icon']}'/><b>{i['label']}</b><div class='small'>{i['value']}</div></div>"
        for i in details
    )

    st.markdown(
        f"""
        <div class="custom-column">
            <h3>{name}</h3>
            <img class="thumb" src="{img_url}"/>
            <h5>Description</h5>
            <p>{(description)}</p>
            <h5>Details</h5>
            <div class="detail-row">
                {details_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def app():
    st.markdown("<h1 style='text-align: center;'>Rooms</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center;'>Find a room that fits your needs.</h6>", unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .custom-column {
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin: 10px 0;
            border: 2px solid rgba(25, 32, 56, 0.1);
        }

        .custom-column h3 {
            margin-top: -10px;
            font-size: 18px;
        }

        .custom-column h5 {
            margin: 0px 0;
            font-size: 15px;
        }

        .custom-column .thumb {
            width: 100%;
            height: 140px;
            object-fit: cover;
            border-radius: 12px;
            margin-bottom: 12px;
        }

        .detail-row {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 12px;
        }

        .detail-box {
            background: rgb(255, 240, 240);
            border-radius: 12px;
            padding: 10px;
            flex: 140px;
            min-width: 120px;
            text-align: center;
        }

        .detail-box img {
            display: block;
            margin: 0 auto 6px auto;
            width: 32px;
            height: 32px;
        }

        .detail-box b {
            display: block;
            font-size: 13px;
        }

        .detail-box .small {
            font-size: 14px;
            color: grey;
            margin-top: 2px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    rooms = db.get_all_rooms() or []
    if not rooms:
        st.info("No rooms available.")

    cols = st.columns(4)

    capacity_icon = "https://img.icons8.com/?size=100&id=3734&format=png&color=000000"
    equipment_icon = "https://img.icons8.com/?size=100&id=24654&format=png&color=000000"

    for i, r in enumerate(rooms):
        col = cols[i % 4]
        with col:
            details = [
                {"icon": capacity_icon, "label": "Capacity", "value": (r.capacity)},
                {"icon": equipment_icon, "label": "Equipment", "value": (r.equipment)},
            ]
            room_card(r.name, r.img_url, r.description, details)
