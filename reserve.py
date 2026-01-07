
import streamlit as st
from datetime import date, datetime, timedelta, time
import time as time_mod
import db


def _ensure_time(tval):
    """Normalize a time-like value to a datetime.time or None.
    Accepts datetime.time, datetime.datetime, or strings like 'HH:MM' or 'HH:MM:SS'.
    """
    if tval is None:
        return None
    # already a time
    try:
        from datetime import time as _time
    except Exception:
        _time = time
    if isinstance(tval, datetime):
        return tval.time()
    if hasattr(tval, 'hour') and hasattr(tval, 'minute'):
        # likely a datetime.time
        return tval
    if isinstance(tval, str):
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(tval, fmt).time()
            except Exception:
                pass
    return None

def _is_admin(user):
    if not user:
        return False
    if user.short_name == "admin":
        return True
    db.get_admins()
    return db.is_admin_check(user.short_name)

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
                st.session_state.user = db.Teacher(short_name="admin", full_name="Administrator", email="admin@example.com")
                st.success("Log in successful")
                time_mod.sleep(1.0)
                st.rerun()
            else:
                success = db.verify_login(username.strip(), password.strip())
                if success:
                    st.session_state.user = success
                    st.success("Log in successful")
                    time_mod.sleep(1.0)
                    st.rerun()
                else:
                    st.error("Invalid credentials")

## Admin edit booking Function ##

@st.dialog("Edit Booking")
def _edit_booking_dialog(booking):
    rooms = db.get_all_rooms()
    room_options = {room.id: f"{room.name} (Capacity: {room.capacity})" for room in rooms}
    room_ids = list(room_options.keys())
    room_index = room_ids.index(booking.room_id) if booking.room_id in room_ids else 0

    col1, col2 = st.columns(2)
    with col1:
        new_room_id = st.selectbox("Room", options=room_ids, index=room_index, format_func=lambda i: room_options[i])
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
        if teacher_record == False:
            st.error(f"Booking Owner '{new_owner}' does not exist. Please enter a valid teacher username.")
            return
        
        errors = []
        if new_start >= new_end:
            errors.append("End Time must be after start time.")
        if not new_visitor.strip():
            errors.append("End User Name is required.")
        if not new_email.strip():
            errors.append("Valid End User Email is required.")
        if not (new_owner or "").strip():
            errors.append("Booking Owner is Required.")
        if not new_purpose.strip():
            errors.append("Purpose is Required.")
        if "@" not in new_email:
            errors.append("Valid email is Required.")

        if errors:
            for e in errors:
                st.error(e)
            return

        old_room = booking.room_id
        old_date = booking.booking_date
        old_start = booking.start_time
        old_end = booking.end_time
        old_visitor = (booking.visitor_name or "").strip()
        old_email = (booking.visitor_email or "").strip().lower()
        old_purpose = booking.purpose or ""
        old_owner = (booking.short_name or "").strip().upper()

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
    st.subheader("Delete Booking")
    st.error(
        f"Delete booking for {booking.visitor_name} in {booking.room_name} on {booking.booking_date} "
        f"from {booking.start_time.strftime('%H:%M')} to {booking.end_time.strftime('%H:%M')}?"
    )
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
                existing_email = (getattr(t, "email", None) or (t.get("email") if isinstance(t, dict) else None) or "")
                existing_short = (getattr(t, "short_name", None) or (t.get("short_name") if isinstance(t, dict) else None))
                if existing_email and existing_email.strip().lower() == new_email_norm and existing_short != old_short:
                    st.error("Email is already used by another teacher.")
                    return

        effective_short = old_short
        if short_changed:
            ok_rename = db.rename_teacher(old_short, new_short)
            if not ok_rename:
                st.error("Username already exists.")
                return
            effective_short = new_short

        payload_password = new_password if password_changed else None

        if any([full_changed, email_changed, password_changed]):
            ok_update = db.update_teacher(
                effective_short,
                new_full,
                new_email_norm,
                payload_password
            )
            if not ok_update:
                st.error("Failed to update teacher.")
                return

        if admin_changed:
            if role_admin and not db.is_admin_check(effective_short):
                db.add_admin(effective_short)
            elif not role_admin and db.is_admin_check(effective_short):
                if effective_short == current_user_short:
                    st.error("You cannot remove your own admin role.")
                    return
                db.remove_admin(effective_short)

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
    # build years safely (skip bookings with no date)
    years = sorted({b.booking_date.year for b in all_bookings if getattr(b, "booking_date", None) is not None})
    years_options = ["All"] + [str(y) for y in years]

    # build owner list safely (normalize None to empty string and uppercase)
    # exclude empty/blank short_names so the dropdown doesn't show an empty option
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

        col_btn1, col_btn2 = st.columns([3, 2])
        with col_btn1:
            st.caption("Filters apply automatically when changed.")
        with col_btn2:
            st.button("Clear filters", on_click=clear_filters)

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

    sel_room = st.session_state.get("key_selected_room")
    room_id = sel_room if sel_room != 0 else None

    sel_date_scope = st.session_state.get("key_date_mode")
    date_of_booked = None
    month_int = None
    year_int = None
    sel_month = st.session_state.get("key_month")
    sel_year = st.session_state.get("key_year")
    if sel_date_scope == "Specific Date":
        date_of_booked = st.session_state.get("key_date", date.today())
    elif sel_date_scope == "Specific Month/Year":
        if sel_month != "All":
            month_int = months.index(sel_month)
        if sel_year != "All":
            year_int = int(sel_year)

    sel_time_scope = st.session_state.get("key_time_mode")
    if sel_time_scope == "Specific time range":
        time_from = st.session_state.get("key_time_from")
        time_to = st.session_state.get("key_time_to")
    else:
        time_from = None
        time_to = None
    sel_owner = st.session_state.get("key_owner")
    sel_reserver = st.session_state.get("key_reserver") or ""
    sel_purpose = st.session_state.get("key_purpose") or ""

    # Normalize filter params: convert UI sentinel values ("All" / empty) to None
    owner_param = None if (not sel_owner or sel_owner == "All") else sel_owner
    reserver_param = None if not sel_reserver.strip() else sel_reserver.strip()
    purpose_param = None if not sel_purpose.strip() else sel_purpose.strip()

    # If no meaningful filters are set, return all bookings directly to avoid accidental empty results
    no_filters = (
        room_id is None
        and sel_date_scope == "All Dates"
        and month_int is None
        and year_int is None
        and time_from is None
        and time_to is None
        and (reserver_param is None)
        and (purpose_param is None)
        and (owner_param is None)
    )

    if no_filters:
        filtered = db.get_bookings()
    else:
        try:
            filtered = db.query_bookings(
                room_id=room_id,
                date_mode=sel_date_scope,
                booking_date=date_of_booked,
                month=month_int,
                year=year_int,
                time_from=time_from,
                time_to=time_to,
                reserver=reserver_param,
                purpose=purpose_param,
                short_name=owner_param,
            )
        except Exception:
            filtered = db.get_bookings()

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
        nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 8])
        with nav_col1:
            if st.button("Prev", disabled=page_index <= 0):
                st.session_state["key_page_index"] = max(0, page_index - 1)
                st.rerun()
        with nav_col2:
            if st.button("Next", disabled=page_index >= max_index):
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
                    left, right = st.columns([9, 1.5])
                    with left:
                        st.markdown(
                            f"""
                            <div style="padding:12px;border:1px solid #e5e5e5;border-radius:10px;margin-bottom:10px;">
                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <div>
                                        <span style="font-weight:700;">{room}</span>
                                        <span style="color:#666;"> • {booking_date_str} {start_str}-{end_str}</span>
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
                        if st.button("Edit", key=f"edit_b_{b.id}", use_container_width=True):
                            _edit_booking_dialog(b)
                        if st.button("Delete", key=f"del_b_{b.id}", use_container_width=True):
                            _delete_booking_dialog(b)

            @st.dialog("Delete All Bookings")
            def delete_all_bookings_dialog():
                st.error("This will permanently delete all bookings.", icon="⚠️")
                confirm = st.button("Confirm Delete", type="primary", use_container_width=True, on_click=clear_filters)

                if confirm:
                    db.delete_booking()
                    st.success("All bookings deleted")
                    time_mod.sleep(0.8)
                    st.rerun()

            if st.button("Delete All Bookings", type="primary", use_container_width=True):
                delete_all_bookings_dialog()   

#### Admin Teacher Management ###
def admin_panel_teacher(user):
    db.get_admins()
    records = db.list_teachers_with_passwords()
    admin_set = set(db.get_admins())
    st.subheader("Teacher Directory")

    if not records:
        st.info("No teachers found.")
    else:
        st.caption(f"Total teachers: {len(records)}")
        for r in records:
		    is_self = r["short_name"] == user.short_name
			is_admin = r["short_name"] == "Admin"
			role = "Admin" if is_admin else "Teacher"
			
		    header_html = (
			    f"<div style='background-color:#fff9e5;padding:8px;border-radius:6px;margin-bottom:8px'>"
			    f"<strong>{r['full_name']}</strong>&emsp;&emsp;&emsp;"
			    f"<span style='background:#222;color:#fff;border-radius:4px;padding:2px 6px;font-size:12px'>{role}</span>"
			    f"</div>"
		    )

            box = st.container(border=True)
		    with box:
			    st.markdown(header_html, unsafe_allow_html=True)
			    col_top = st.columns([2.5, 2.5, 2.5, 0.6, 1])
				with col_top[0]:
				    st.write(r["email"] if not is_admin else "—")
			    with col_top[1]:
			        st.write(r["short_name"])
                with col_top[2]:
				    st.write("********" if is_admin else r.get("password", ""))
                with col_top[3]:
				    if is_admin:
					    st.button("Edit", key=f"edit_t_{r['short_name']}", disabled=True)
                    else:
                        if st.button("Edit", key=f"edit_t_{r['short_name']}"):
                            _edit_teacher_dialog(r, user.short_name)
				with col_top[4]:
                    if is_admin:
                       st.button("Delete", key=f"del_t_{r['short_name']}", disabled=True)
                    else:
                        if st.button("Delete", key=f"del_t_{r['short_name']}"):
                            _delete_teacher_dialog(r, user.short_name)


def admin_panel_teacher(user):
    records = db.list_teachers_with_passwords()
    admin_set = set(db.get_admins())
    st.subheader("Teacher Directory")

    if not records:
        st.info("No teachers found.")
    else:
        st.caption(f"Total teachers: {len(records)}")
        
         for r in records:
    is_self = r["short_name"] == user.short_name
    is_admin = r["short_name"] in admin_set
    role = "Admin" if is_admin else "Teacher"

    header_html = (
        f"<div style='background-color:#fff9e5;padding:8px;border-radius:6px;margin-bottom:8px'>"
        f"<strong>{r['full_name']}</strong>&emsp;&emsp;&emsp;"
        f"<span style='background:#222;color:#fff;border-radius:4px;padding:2px 6px;font-size:12px'>{role}</span>"
        f"</div>"
    )

    box = st.container(border=True)
    with box:
        st.markdown(header_html, unsafe_allow_html=True)
        col_top = st.columns([2.5, 2.5, 2.5, 0.6, 1])

        with col_top[0]:
            st.write(r["email"] if not is_admin else "—")
        with col_top[1]:
            st.write(r["short_name"])
        with col_top[2]:
            # Never display raw passwords; for admins show masked
            st.write("********" if is_admin else r.get("password", ""))
        with col_top[3]:
            if is_admin:
                st.button("Edit", key=f"edit_t_{r['short_name']}", disabled=True)
            else:
                if st.button("Edit", key=f"edit_t_{r['short_name']}"):
                    _edit_teacher_dialog(r, user.short_name)
        with col_top[4]:
            if is_admin:
                st.button("Delete", key=f"del_t_{r['short_name']}", disabled=True)
            else:
                if st.button("Delete", key=f"del_t_{r['short_name']}"):
                    _delete_teacher_dialog(r, user.short_name)


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
            tempcol1, tempcol2 = st.columns([3, 1])
            with tempcol1:
                st.caption("")
            with tempcol2:
                submit = st.form_submit_button("Add teacher")

        if submit:
            errors = []
            if not new_short:
                errors.append("Username is required.")
            if not new_full:
                errors.append("Full name is required.")
            if not new_email or "@" not in new_email:
                errors.append("Valid email is required.")
            if not new_password:
                errors.append("Password is required.")
            if len(new_password) < 8:
                errors.append("Password must have at least 8 characters.")

            teachers = db.list_teachers() or []
            username_conflict = False
            email_conflict = False
            for t in teachers:
                existing_short = getattr(t, "short_name", t.get("short_name") if isinstance(t, dict) else None)
                existing_email = getattr(t, "email", t.get("email") if isinstance(t, dict) else None)
                if existing_short and existing_short == new_short:
                    username_conflict = True
                if (existing_email or "") and (existing_email or "").strip().lower() == new_email:
                    email_conflict = True
                if username_conflict and email_conflict:
                    break

            if username_conflict:
                errors.append("Username already exists.")
            if email_conflict:
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

def app():
    st.set_page_config(layout="wide")
    st.markdown("<h1 style='text-align: center;'>Reserve</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center;'>Find a room that fits your needs.</h6>", unsafe_allow_html=True)

    if "user" not in st.session_state:
        st.session_state.user = None
    user = st.session_state.user

    if user is None:
        _login_dialog()
        st.stop()
    else:
        top_bar = st.columns([7, 1])
        with top_bar[0]:
            st.write(f"Logged in as: **{user.full_name} ({user.short_name})**")
        with top_bar[1]:
            if st.button("Log out"):
                st.session_state.user = None
                st.rerun()

    rooms = db.get_all_rooms()
    if not rooms:
        st.warning("No rooms are available to reserve.")
        return
    st.subheader("Create a Booking")
    st.caption("Fill in the form to reserve a room")

    room_options = {room.id: f"{room.name} (Capacity: {room.capacity if room.capacity is not None else 'N/A'})" for room in rooms}
    options = list(room_options.keys())
    with st.form("reserve"):
        col1, col2 = st.columns([3, 2])
        with col1:
            selected_room_id = st.selectbox("Select Room", options=options, format_func=lambda i: room_options[i])
            booking_date = st.date_input("Booking Date", min_value=date.today(), value=date.today())
            default_start = (datetime.now() + timedelta(hours=1)).time().replace(minute=0, second=0, microsecond=0)
            default_end = (datetime.now() + timedelta(hours=4)).time().replace(minute=0, second=0, microsecond=0)
            start_time = st.time_input("Start Time", value=default_start)
            end_time = st.time_input("End Time", value=default_end)
        with col2:
            reserver_name = st.text_input("End User Full Name", value=user.full_name or "")
            reserver_email = st.text_input("Email Address", value=user.email or "")
            purpose = st.text_area("Purpose of Meeting", placeholder="Brief description of the meeting purpose", height=120)

            # Admin bookings: owner will be set automatically to the logged-in admin account.
            # No owner selection is shown; the system will store the admin's short_name as the booking owner.
        submitted = st.form_submit_button("Create Booking")

    if submitted:
        errors = []
        if not reserver_name.strip():
            errors.append("Reserver name is required")
        if not reserver_email.strip():
            errors.append("Reserver email is required")
        elif "@" not in reserver_email:
            errors.append("A valid email address is required")

        # Normalize time inputs to avoid type issues (str vs time vs None)
        start_time = _ensure_time(start_time)
        end_time = _ensure_time(end_time)

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
                # Determine admin status and set booking owner automatically for admins
                is_admin = _is_admin(user)
                owner_short = (user.short_name or "").strip().upper() if is_admin else None

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
                    st.success(
                        f"Booking created for {room_options[selected_room_id]} "
                        f"on {booking_date} from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}"
                    )
                else:
                    st.error("Failed to create booking. Please try again.")
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
