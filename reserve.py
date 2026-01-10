
import streamlit as st
from datetime import date, datetime, timedelta, time
import time as time_mod
import db



def _is_admin(user):
    if not user:
        return False
    short = (getattr(user, "short_name", "") or "").strip().upper()
    if short == "ADMIN":
        return True
    return db.is_admin_check(short)

## Login Page ##
@st.dialog("Log in")
def _login_dialog():
    st.info("Please log in to continue.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log in"):
        if not username.strip() or not password.strip():
            st.error("Please enter both username and password")
        else:
            if username.strip() == "Admin" and password.strip() == "Admin":
                st.session_state.user = db.Teacher(short_name="ADMIN", full_name="Administrator", email="admin@example.com")
                st.success("Log in successful")
                time_mod.sleep(1.0)
                st.rerun()
            else:
                success = db.verify_login(username.strip(), password.strip())
                if success:
                    st.session_state.user = db.Teacher(short_name=(success.short_name or "").strip().upper(), full_name=success.full_name, email=success.email)
                    st.success("Log in successful")
                    time_mod.sleep(1.0)
                    st.rerun()
                else:
                    st.error("Invalid credentials")

## Admin edit booking Function ##
@st.dialog("Edit Booking")
def _edit_booking_dialog(booking):
    rooms = db.get_all_rooms()
    room_options = [f"{room.name} (Capacity: {room.capacity})" for room in rooms]

            
    col1, col2 = st.columns(2)
    with col1:
        selected_room = st.selectbox("Select Room", options=room_options)
        new_room_id = rooms[room_options.index(selected_room)].id 
        new_date = st.date_input("Date", value=booking.booking_date)
        new_start = st.time_input("Start Time", value=booking.start_time)
        new_end = st.time_input("End Time", value=booking.end_time)
    with col2:
        new_visitor = st.text_input("End User Full Name", value=booking.visitor_name or "")
        new_email = st.text_input("End User Email", value=booking.visitor_email or "")
        new_owner = st.text_input("Booking Owner", value=(booking.short_name or "")).strip().upper()
        new_purpose = st.text_area("Purpose", value=booking.purpose or "", height=120)

    if st.button("Save changes"):
        teacher_record = db.list_teacher_short_name(new_owner)

        errors = []
        if new_start >= new_end:
            errors.append("End Time must be after start time.")
        if not new_visitor.strip():
            errors.append("End User Name is required.")
        if not new_email.strip():
            errors.append("Email is required.")
        elif "@" not in new_email:
            errors.append("Valid email is Required.")
        if not (new_owner or "").strip():
            errors.append("Booking Owner is Required.")
        if not new_purpose.strip():
            errors.append("Purpose is Required.")


        if errors:
            for e in errors:
                st.error(e)
            return
        
        if teacher_record == False:
            st.error(f"Booking Owner '{new_owner}' does not exist. Please enter a valid teacher username.")
            return

        old_room = booking.room_id
        old_date = booking.booking_date
        old_start = booking.start_time
        old_end = booking.end_time
        old_visitor = (booking.visitor_name).strip()
        old_email = (booking.visitor_email).strip().lower()
        old_purpose = (booking.purpose).strip()
        old_owner = (booking.short_name).strip().upper()

        room_changed = new_room_id != old_room
        date_changed = new_date != old_date
        start_changed = new_start != old_start
        end_changed = new_end != old_end
        visitor_changed = new_visitor.strip() != old_visitor
        email_changed = new_email != old_email
        purpose_changed = (new_purpose or "").strip() != old_purpose
        owner_changed = new_owner != old_owner

        if not any([room_changed, date_changed, start_changed, end_changed, visitor_changed, email_changed, purpose_changed, owner_changed]):
            st.info("No changes to save.", icon="🔍")
            return

        if not db.is_available_excluding(booking.id, new_room_id, new_date, new_start, new_end):
            st.error("The selected time slot conflicts with another booking")
            return

        if any([room_changed, date_changed, start_changed, end_changed, visitor_changed, email_changed, purpose_changed, owner_changed]):
            ok = db.update_booking(
                booking_id=booking.id,
                room_id=new_room_id,
                visitor_name=new_visitor.strip(),
                visitor_email=new_email,
                booking_date=new_date,
                start_time=new_start,
                end_time=new_end,
                purpose=(new_purpose or "").strip(),
                short_name=new_owner,
            )
            if not ok:
                st.error("Failed to update booking")
        st.success("Booking updated")
        time_mod.sleep(0.4)
        st.rerun()



@st.dialog("Delete Booking")
def _delete_booking_dialog(booking):
    delete_html = f"""
    <div style="background-color:#ffe5e5;padding:10px;border-radius:12px;margin-bottom:10px">
    <strong>You are about to Delete Booking:</strong><br><br>
    <strong>Room: </strong> {booking.room_name}<br>
    <strong>Booking Date: </strong> {booking.booking_date}<br>
    <strong>Time: </strong>From {booking.start_time.strftime('%H:%M')} To {booking.end_time.strftime('%H:%M')}<br>
    <strong>End User: </strong> {booking.visitor_email}<br>
    <strong>Owner: </strong> {booking.short_name}<br>
    <strong>Purpose: </strong> {booking.purpose}
    </div>
    """
    st.markdown(delete_html, unsafe_allow_html=True)
    
    if st.button("Confirm delete"):
        db.delete_booking_by_id(booking.id)
        st.success("Booking deleted")
        time_mod.sleep(0.8)
        st.rerun()

###Admin Edit Teacher Functions###
@st.dialog("Edit Teacher")
def _edit_teacher_dialog(record, current_user_short):
    current_short = record["short_name"]
    is_admin_now = db.is_admin_check(current_short)

    col1, col2 = st.columns(2)
    with col1:
        new_short = (st.text_input("Username", value=current_short) or "").upper().strip()
        new_full = (st.text_input("Full name", value=record["full_name"] or "") or "").strip()
        new_email = (st.text_input("Email", value=record["email"] or "") or "").strip()

    with col2:
        new_password = (st.text_input("New password (optional)", type="password") or "").strip()
        role_admin = st.checkbox("Grant admin role", value=is_admin_now)

    if st.button("Save changes"):
        errors = []
        if not new_short:
            errors.append("Username is required.")
        if not new_full:
            errors.append("Full name is required.")
        if not new_email or "@" not in new_email:
            errors.append("Valid email is required.")
        if new_password and len(new_password) < 8:
            errors.append("Password must have at least 8 characters.")

        if errors:
            for e in errors:
                st.error(e)
            return

        old_short = (record["short_name"] or "").strip().upper()
        old_full = (record["full_name"] or "").strip()
        old_email = (record["email"] or "").strip().lower()
        new_email_norm = new_email.strip().lower()

        short_changed = new_short != old_short
        full_changed = new_full != old_full
        email_changed = new_email_norm != old_email
        password_changed = bool(new_password)
        admin_changed = role_admin != is_admin_now

        if not any([short_changed, full_changed, email_changed, password_changed, admin_changed]):
            st.info("No changes to save.", icon="🔍")
            return

        if email_changed:
            for t in db.list_teachers():
                existing_email = getattr(t, "email", "").strip().lower()
                existing_short = getattr(t, "short_name", "")
                if existing_email == new_email.strip().lower() and existing_short != old_short:
                    st.error("Email is already used by another teacher.")
                    return

        if short_changed:
            ok_rename = db.rename_teacher(old_short, new_short)
            if not ok_rename:
                st.error("Username already exists.")
                return
            
        payload_password = new_password if password_changed else None 

        if any([full_changed, email_changed, password_changed]):
            ok_update = db.update_teacher(
                new_short, 
                new_full,
                new_email.strip().lower(),
                payload_password
            )

            if not ok_update:
                st.error("Failed to update teacher.")
                return

        if admin_changed:
            current_is_admin = db.is_admin_check(new_short)
            if role_admin and not current_is_admin:
                db.add_admin(new_short)
            elif not role_admin and current_is_admin:
                if new_short == current_user_short:
                    st.error("You cannot remove your own admin role.")
                    return
                db.remove_admin(new_short)


        st.success("Teacher updated")
        time_mod.sleep(0.4)
        st.rerun()
  
@st.dialog("Delete Teacher")
def _delete_teacher_dialog(record, current_user_short):
    short = record["short_name"]
    
    st.error(f"Delete teacher {short} ({record['full_name']})?")
    
    if st.button("Confirm delete"):
        if short == current_user_short:
            st.error("You cannot delete your own account.")
        else:
            db.delete_teacher(short)
            st.success("Teacher deleted")
            time_mod.sleep(0.4)
            st.rerun()


###admin_bookings_filters###
def _admin_bookings_filters():
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

    filtered = db.query_bookings(**query_params)


    page_size = st.session_state.get("key_page_size", 10)
    page_index = st.session_state.get("key_page_index", 0)
    total = len(filtered)

    max_index = max(0, (total - 1) // page_size)
    page_index = min(page_index, max_index)
    start = page_index * page_size
    end = start + page_size
    current_page = filtered[start:end]

    with col_result:
        st.subheader("Filtered Bookings")
        st.caption(f"Showing {len(current_page)} of {total} bookings")
        nav_col1, nav_col2 = st.columns([1, 1])
        with nav_col1:
            if st.button("Prev", width= "stretch", disabled=page_index <= 0):
                st.session_state["key_page_index"] = max(0, page_index - 1)
                st.rerun()
        with nav_col2:
            if st.button("Next",width= "stretch", disabled=page_index >= max_index):
                st.session_state["key_page_index"] = min(max_index, page_index + 1)
                st.rerun()

    with col_result:
        if db.count_bookings() == 0:
            st.info("No Bookings in the System.", icon="🔍")

        elif total == 0:
            st.info("No Bookings Found based on your Selected Filters.", icon="🔍")

        elif db.count_bookings() != 0:
            for b in current_page:
                room = getattr(b, "room_name", "") or ""
                booking_date_val = getattr(b, "booking_date", None)
                booking_date_str = booking_date_val.strftime("%Y-%m-%d") if booking_date_val else ""
                start_val = getattr(b, "start_time", None)
                start_str = start_val.strftime("%H:%M") if start_val else ""
                end_val = getattr(b, "end_time", None)
                end_str = end_val.strftime("%H:%M") if end_val else ""
                owner = (getattr(b, "short_name", "") or "")
                end_user = getattr(b, "visitor_name", "") or ""
                purpose = getattr(b, "purpose", "") or ""
                email = getattr(b, "visitor_email", "") or ""
                created = getattr(b, "created_at", None)
                created_str = created.strftime("%Y-%m-%d %H:%M") if created else ""

                box = st.container()
                with box:
                    left, right = st.columns([9, 2.1])
                    with left:
                        st.markdown(
                            f"""
                            <div style="padding:12px;border:1px solid #e5e5e5;border-radius:10px;margin-bottom:10px;">
                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <div>
                                        <span style="font-weight:700;">{room}</span>
                                        <span style="color:#666;">  {booking_date_str} {start_str}-{end_str}</span>
                                    </div>
                                    <div style="font-size:12px;color:#666;">Owner: <b>{owner}</b></div>
                                </div>
                                <div style="margin-top:6px;color:#333;">
                                    <div><b>End User:</b> {end_user}</div>
                                    <div><b>Purpose:</b> {purpose}</div>
                                    <div style="font-size:12px;color:#888;margin-top:6px;">
                                        Email: {email} • Created: {created_str}
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with right:
                        if st.button("Edit", key=f"edit_b_{b.id}", width= "stretch"):
                            _edit_booking_dialog(b)
                        if st.button("Delete", key=f"del_b_{b.id}", use_container_width= True):
                            _delete_booking_dialog(b)

            @st.dialog("Delete All Bookings")
            def delete_all_bookings_dialog():
                st.error("This will permanently delete all bookings.", icon="⚠️")
                confirm = st.button("Confirm Delete", type="primary", width= "stretch", on_click=clear_filters)

                if confirm:
                    db.delete_booking()
                    st.success("All bookings deleted")
                    time_mod.sleep(0.8)
                    st.rerun()

            if st.button("Delete All Bookings", type="primary", width= "stretch"):
                delete_all_bookings_dialog()   

#### Admin Teacher Management ###
def admin_panel_teacher(user):
    records = db.list_teachers_with_passwords() or []
    admin_set_raw = db.get_admins() or []
    admin_set = {str(a).strip().lower() for a in admin_set_raw}

    st.subheader("Teacher Directory")
    st.caption(f"Total Teacher: {len(records)-1} ")

    if not records:
        st.info("No teachers found.")
        return

    st.markdown(
        """
        <style>
        .teacher-header {
            margin-bottom: 8px;
            border-radius: 8px;
            padding: 8px;
            color: black;
        }
        .teacher-details {
            color: black;
            font-size: 14px;
        }
        .role-badge {
            background: black;
            color: white;
            border-radius: 8px;
            padding: 2px 6px;
            font-size: 12px;
            margin-left: 8px;
            display: inline-block;
            vertical-align: middle;
        }

        .stButton > button {
            border-radius: 8px;
            padding: 8px 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    norm = []
    for r in records:
        if not (r, dict):
            r = db.list_teachers_with_passwords()
            
        short = (r.get("short_name") or "")
        if short.strip().lower() == "admin":
            continue
        norm.append(r)

    for row_start in range(0, len(records), 2):
        cols = st.columns(2)
        for col_index, col in enumerate(cols):
            idx = row_start + col_index
            if idx >= len(norm):
                break
            r = norm[idx]

            short_name = r.get("short_name")
            full_name  = r.get("full_name")
            email      = r.get("email")
            password   = r.get("password")

            is_admin = short_name.strip().lower() in admin_set
            role = "Admin" if is_admin else "Teacher"
            header_bg = "#f2e5ff" if is_admin else "#fff9e5"

            with col:
                card = st.container(border=True)
                with card:
                    st.markdown(
                        f"""
                        <div class='teacher-header' style='background-color:{header_bg};'>
                            <b>{full_name}</b>
                            <span class='role-badge'>{role}</span>
                        </div>

                        <div class='teacher-details'>
                            <div><b>Username: </b> {short_name}</div>
                            <div><b>Email: </b> {email}</div>
                            <div><b>Password: </b> {password}</div><br>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    a, b = st.columns(2)
                    with a:
                        if st.button("Edit", key=f"edit_t_{short_name}", width= "stretch"):
                            _edit_teacher_dialog(r, getattr(user, "short_name", ""))
                    with b:
                        if st.button("Delete", key=f"del_t_{short_name}", width= "stretch"):
                            _delete_teacher_dialog(r, getattr(user, "short_name", ""))

    st.subheader("Add New Teacher")
    st.caption("Create a new teacher account")
    with st.form("add_teacher"):
        col1, col2 = st.columns(2)
        with col1:
            new_short = (st.text_input("Username") or "").upper().strip()
            new_full = (st.text_input("Full name") or "").strip()
            new_is_admin = st.checkbox("Grant admin role")
        with col2:
            new_password = (st.text_input("Password", type="password") or "").strip()
            new_email = (st.text_input("Email") or "").strip().lower()
        submit = st.form_submit_button("Add teacher")

        if submit:
            errors = []
            if not new_short:
                errors.append("Username is required.")
            if not new_full:
                errors.append("Full name is required.")
            if not new_email.strip():
                errors.append("Email is required")
            elif "@" not in new_email:
                errors.append("Valid email is required.")
            if not new_password:
                errors.append("Password is required.")
            elif len(new_password) < 8:
                errors.append("Password must have at least 8 characters.")
            
            if errors:
                for e in errors:
                    st.error(e)

            teachers = db.list_teachers() or []
            for t in teachers:
                existing_short = getattr(t, "short_name")
                existing_email = getattr(t, "email")
                if existing_short and existing_short == new_short:
                    errors.append("Username already exists.")
                if (existing_email or "").strip() == new_email:
                    errors.append("Email is already used by another teacher.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                short_disp = new_short
                full_disp = new_full
                email_disp = new_email
                role_label = "Admin" if new_is_admin else "Teacher"

                admin_summary_html = f"""
                <div style="background-color:#ffe5e5;padding:10px;border-radius:12px;margin-bottom:10px">
                <strong>You are about to add:</strong> {short_disp} ({full_disp})<br>
                <strong>Role:</strong> {role_label}<br>
                <strong>Email:</strong> {email_disp}
                </div>
                """

                teacher_summary_html = f"""
                <div style="background-color:#e5ffff;padding:10px;border-radius:12px;margin-bottom:10px">
                <strong>You are about to add:</strong> {short_disp} ({full_disp})<br>
                <strong>Role:</strong> {role_label}<br>
                <strong>Email:</strong> {email_disp}
                </div>
                """

                @st.dialog("Add Teacher")
                def add_teacher_dialog():
                    if new_is_admin:
                        st.markdown(admin_summary_html, unsafe_allow_html=True)
                    else:
                        st.markdown(teacher_summary_html, unsafe_allow_html=True)

                    if st.button("Confirm add"):
                        try:
                            ok = db.create_teacher(short_disp, full_disp, email_disp, new_password)
                            if ok:
                                if new_is_admin:
                                    db.add_admin(short_disp)
                                st.success("Teacher added")
                                time_mod.sleep(0.8)
                                st.rerun()
                            else:
                                st.error("Failed to add teacher")
                        except Exception as e:
                            st.error(f"Failed to add teacher. Username or email may already exist. Details: {e}")

                add_teacher_dialog()

###room booking###
def app():
    st.markdown("<h1 style='text-align: center;'>Reserve</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center;'>Find a room that fits your needs.</h6>", unsafe_allow_html=True)

    if "user" not in st.session_state:
        st.session_state.user = None
    user = st.session_state.user

    if user is None:
        _login_dialog()
        st.stop()
    else:
        top_bar = st.columns([7, 2],vertical_alignment="bottom")
        with top_bar[0]:
            st.write(f"Logged in as: **{user.full_name} ({user.short_name})**")
        with top_bar[1]:
            if st.button("Log out", use_container_width="True"):
                st.session_state.user = None
                st.rerun()  

    rooms = db.get_all_rooms()
    if not rooms:
        st.warning("No rooms are available to reserve.")
        return
    st.subheader("Create a Booking")
    st.caption("Fill in the form to reserve a room")

    room_options = [f"{room.name} (Capacity: {room.capacity})" for room in rooms]
    with st.form("reserve"):
        col1, col2 = st.columns([3, 2])
        with col1:
            selected_room = st.selectbox("Select Room", options=room_options)
            selected_room_id = rooms[room_options.index(selected_room)].id 
            booking_date = st.date_input("Booking Date", min_value=date.today(), value=date.today())
            default_start = (datetime.now() + timedelta(hours=1)).time().replace(minute=0, second=0, microsecond=0)
            default_end = (datetime.now() + timedelta(hours=4)).time().replace(minute=0, second=0, microsecond=0)
            start_time = st.time_input("Start Time", value=default_start)
            end_time = st.time_input("End Time", value=default_end)
        with col2:
            reserver_name = st.text_input("End User Full Name", value=user.full_name or "")
            reserver_email = st.text_input("Email Address", value=user.email or "")
            purpose = st.text_area("Purpose of Meeting", placeholder="Brief description of the meeting purpose", height="stretch")
        submitted = st.form_submit_button("Create Booking")

        if submitted:
            errors = []
            if not reserver_name.strip():
                errors.append("Reserver name is required")
            if not reserver_email.strip():
                errors.append("Reserver email is required")
            elif "@" not in reserver_email:
                errors.append("A valid email address is required")

            if start_time is None or end_time is None:
                errors.append("Start time and end time are required and must be valid.")
            elif start_time >= end_time:
                errors.append("End time must be after start time")
            if not purpose.strip():
                errors.append("Purpose of meeting is required")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                if db.is_available(selected_room_id, booking_date, start_time, end_time):
                    admin_info = db.get_admins_info()
                    admins_break =  "<br>".join(admin_info)
                    owner_short = None
                    if user and getattr(user, "short_name", None):
                        candidate = (user.short_name or "").strip().upper()
                        if db.list_teacher_short_name(candidate):
                            owner_short = candidate
                
                    booking_html = f"""
                    <div style="background-color:#ccffff;padding:15px;border-radius:12px;margin-bottom:10px">
                    <strong>You are about to Create Booking:</strong><br><br>
                    <strong>Room: </strong> {selected_room_id}<br>
                    <strong>Booking Date: </strong> {booking_date}<br>
                    <strong>Time: </strong>From {start_time.strftime('%H:%M')} To {end_time.strftime('%H:%M')}<br>
                    <strong>End User: </strong> {reserver_name.strip()}<br>
                    <strong>Purpose: </strong> {purpose.strip()}
                    </div>
                    """

                    booking_content_alert_html = f"""
                    <div style="background-color:#ffe5e5;padding:15px;border-radius:12px;margin-bottom:10px">
                    <b>🚨Once your booking is confirmed, you can't edit or delete it.<br> 
                    If you need any changes, please contact the administrator:</b><br><br>
                    <b>Admin: </b><br>
                    <b>IT Department</b> - admin@example.com<br>
                    {admins_break}  
                    </div>
                    """

                    @st.dialog("Comfirm Booking")
                    def comfirm_booking_dialog():
                            st.markdown(booking_html, unsafe_allow_html=True)
                            st.markdown(booking_content_alert_html, unsafe_allow_html= True)

                            if st.button("Comfirm Booking"):
                                    success = db.create_booking(
                                        room_id=selected_room_id,
                                        visitor_name=reserver_name.strip(),
                                        visitor_email=reserver_email.strip(),
                                        booking_date=booking_date,
                                        start_time=start_time,
                                        end_time=end_time,
                                        purpose=purpose.strip(),
                                        short_name=owner_short,
                                    )
                                    if success:
                                        st.success("Success for Booking")
                                        time_mod.sleep(0.8)
                                        st.rerun()

                                    else:
                                        st.error("Failed to create booking. Please try again.")
                    comfirm_booking_dialog()
                else:
                    st.error(
                        f"The selected room is not available during "
                        f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} on {booking_date}. "
                        "Please choose a different time slot or room."
                    )
            


    if _is_admin(user):
        st.markdown("---")
        st.markdown("<h2 style='text-align: center;'>Admin Panel</h2>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<h3 style='text-align: center;'>Booking</h3>", unsafe_allow_html=True)
        st.markdown("---")
        _admin_bookings_filters()
        st.markdown("---")
        st.markdown("<h3 style='text-align: center;'>Teachers</h3>", unsafe_allow_html=True)
        st.markdown("---")
        admin_panel_teacher(user)



        