
import streamlit as st
import pandas as pd
from datetime import date, time
import db

def app():
    st.markdown("<h1 style='text-align: center;'>View</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center;'>View Room Bookings with filter.</h6>", unsafe_allow_html=True)

    rooms = db.get_all_rooms()
    room_filter_options = {0: "All Rooms"}
    for room in rooms:
        room_filter_options[room.id] = room.name
        
    all_bookings = db.get_bookings()
    months = ["All", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    years = sorted({b.booking_date.year for b in all_bookings if getattr(b, "booking_date", None) is not None})
    years_options = ["All"] + [str(y) for y in years]

    owner = sorted({(b.short_name or "").upper() for b in all_bookings if (getattr(b, "short_name", None) or "").strip()})
    owner_options = ["All"] + owner

    col_filters, col_result = st.columns([3, 7])
    with col_filters:
        st.subheader("Filters")

        def clear_filters():
            for k in [
                "key_selected_room",
                "key_date_mode",
                "key_date",
                "key_month",
                "key_year",
                "key_time_mode",
                "key_time_from",
                "key_time_to",
                "key_reserver",
                "key_purpose",
                "key_owner"
            ]:
                st.session_state.pop(k, None)
            st.session_state["key_selected_room"] = 0
            st.session_state["key_date_mode"] = "All Dates"
            st.session_state["key_time_mode"] = "All times"
            st.session_state["key_reserver"] = ""
            st.session_state["key_purpose"] = ""
            st.session_state["key_owner"] = "All"

        col_btn1, col_btn2 = st.columns([6, 5])
        with col_btn1:
            st.caption("Filters apply automatically when changed.")
        with col_btn2:
            st.button("Clear filters",use_container_width = True, on_click=clear_filters)

        st.markdown("---")
        st.selectbox(
            "Room",
            options=list(room_filter_options.keys()),
            format_func=lambda x: room_filter_options[x],
            key="key_selected_room")

        date_scope = st.selectbox(
            "Date scope",
            options=["All Dates", "Specific Date", "Specific Month/Year"],
            index=0,
            key="key_date_mode")

        if date_scope == "Specific Date":
            st.date_input(
                "Date",
                value=st.session_state.get("key_date", date.today()),
                key="key_date")
            st.session_state["key_month"] = "All"
            st.session_state["key_year"] = "All"

        elif date_scope == "Specific Month/Year":
            st.selectbox(
                "Month",
                options=months,
                index=months.index(st.session_state.get("key_month", "All")),
                key="key_month")
            st.selectbox(
                "Year",
                options=years_options,
                index=years_options.index(st.session_state.get("key_year", "All")),
                key="key_year")
            st.session_state["key_date"] = None

        else:
            st.session_state["key_date"] = None
            st.session_state["key_month"] = "All"
            st.session_state["key_year"] = "All"

        time_scope = st.selectbox(
            "Time scope",
            options=["All times", "Specific time range"],
            index=0,
            key="key_time_mode")
        
        if time_scope == "Specific time range":
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.time_input(
                    "From",
                    value=st.session_state.get("key_time_from", time(hour=9, minute=0)),
                    key="key_time_from")
            with col_t2:
                st.time_input(
                    "To",
                    value=st.session_state.get("key_time_to", time(hour=17, minute=0)),
                    key="key_time_to")
        
        st.selectbox(
            "Owner contains (Initial)",
            options=owner_options,
            index =owner_options.index(st.session_state.get("key_owner", "All")),
            key="key_owner"
        )

        st.text_input(
            "End User name contains",
            value=st.session_state.get("key_reserver", ""),
            key="key_reserver",
        )
        st.text_input(
            "Purpose contains",
            value=st.session_state.get("key_purpose", ""),
            key="key_purpose",
        )

    filters = {
        'room_id': st.session_state.get("key_selected_room") if st.session_state.get("key_selected_room") != 0 else None,
        'date_mode': st.session_state.get("key_date_mode", "All Dates"),
        'date': st.session_state.get("key_date"),
        'month': months.index(st.session_state.get("key_month", "All")) if st.session_state.get("key_date_mode") == "Specific Month/Year" and st.session_state.get("key_month") != "All" else None,
        'year': int(st.session_state.get("key_year", "All")) if st.session_state.get("key_date_mode") == "Specific Month/Year" and st.session_state.get("key_year") != "All" else None,
        'time_from': st.session_state.get("key_time_from"),
        'time_to': st.session_state.get("key_time_to"),
        'owner': st.session_state.get("key_owner"),
        'reserver': st.session_state.get("key_reserver"),
        'purpose': st.session_state.get("key_purpose"),
    }

    query_params = {
        'room_id': filters['room_id'] if filters['room_id'] != 0 else None,
        'date_mode': filters['date_mode'],
        'booking_date': filters['date'],
        'month': filters['month'],
        'year': filters['year'],
        'time_from': filters['time_from'],
        'time_to': filters['time_to'],
        'reserver': filters['reserver'] or None,
        'purpose': filters['purpose'] or None,
        'short_name': filters['owner'] if filters['owner'] and filters['owner'] != "All" else None,
    }

    try:
        bookings = db.query_bookings(**query_params)
    except Exception:
        bookings = db.get_bookings()

    all_bookings_raw = db.get_bookings()

    def row(b):
        start_t = getattr(b, "start_time", None)
        end_t = getattr(b, "end_time", None)
        created_at = getattr(b, "created_at", None)
        booking_date_val = getattr(b, "booking_date", None)
        return {
            "Room ID": getattr(b, "room_id", None),
            "Room": getattr(b, "room_name", None),
            "Date": booking_date_val.strftime("%Y-%m-%d") if booking_date_val else None,
            "Start Time": start_t.strftime("%H:%M") if start_t else None,
            "End Time": end_t.strftime("%H:%M") if end_t else None,
            "End User": getattr(b, "visitor_name", None),
            "Email": getattr(b, "visitor_email", None),
            "Purpose": getattr(b, "purpose", None),
            "Created At": created_at.strftime("%Y-%m-%d %H:%M") if created_at else None,
            "Owner": (getattr(b, "short_name", "") or "").upper(),
        }

    filtered_df = pd.DataFrame([row(b) for b in bookings])
    all_df = pd.DataFrame([row(b) for b in all_bookings_raw])

    with col_result:
        DEFAULT_COLS = ["Room ID", "Room", "Date", "Start Time", "End Time", "End User", "Email", "Purpose", "Created At", "Owner"]

        st.subheader("Filtered results")

        if filtered_df.empty:
            if clear_filters():
                if all_df.empty:
                    st.info("No Bookings in the System.", icon="🔍")
                else:
                    filtered_df = all_df.copy()
            else:
                st.info("No Bookings Found based on your Selected Filters.", icon="🔍")

        top_bar_left, top_bar_right = st.columns(2, vertical_alignment="bottom")
        with top_bar_left:
            st.caption("Columns for Filtered results")
        with top_bar_right:
            with st.popover("Columns", use_container_width=True):
                sel_cols = st.session_state.get("selected_columns", DEFAULT_COLS[:])
                
                if st.button("Reset", use_container_width=True):
                    st.session_state["selected_columns"] = DEFAULT_COLS[:]
                    st.rerun()
                
                for col in DEFAULT_COLS:
                    if st.checkbox(col, value=col in sel_cols):
                        if col not in sel_cols: sel_cols.append(col)
                    elif col in sel_cols: sel_cols.remove(col)

        show_cols = [c for c in list(st.session_state["selected_columns"]) if c in filtered_df.columns]
        if not show_cols:
            show_cols = [c for c in DEFAULT_COLS if c in filtered_df.columns]

        st.dataframe(filtered_df[show_cols], use_container_width=True)

        st.markdown(
            f"Showing {len(filtered_df)} booking(s) out of {len(all_df)} total.",
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.subheader("All bookings")
        st.dataframe(all_df[[c for c in DEFAULT_COLS if c in all_df.columns]], use_container_width=True)
