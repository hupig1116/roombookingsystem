import sqlite3
from dataclasses import dataclass
from datetime import datetime, date, time
from typing import List, Optional, Tuple
import threading

db_lock = threading.Lock()
conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

@dataclass
class Teacher:
    short_name: str
    full_name: str
    email: str 

@dataclass
class Room:
    id: int
    name: str
    capacity: int
    description: str 
    img_url: str
    equipment: str

@dataclass
class Booking:
    id: int
    room_id: int
    room_name: str
    booking_date: date
    start_time: time
    end_time: time
    visitor_name: str
    visitor_email: str
    short_name: Optional[str]
    purpose: Optional[str]
    created_at: datetime

def _create_tables():
    c.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            short_name TEXT PRIMARY KEY NOT NULL,
            full_name  TEXT NOT NULL,
            email      TEXT NOT NULL
        )
    """)
    conn.commit()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            capacity    INTEGER,
            description TEXT,
            equipment   TEXT,
            img_url     TEXT
        )
    """)
    conn.commit()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id       INTEGER NOT NULL,
            short_name    TEXT,
            booking_date  TEXT NOT NULL,
            start_time    TEXT NOT NULL,
            end_time      TEXT NOT NULL,
            visitor_name  TEXT NOT NULL,
            visitor_email TEXT NOT NULL,
            purpose       TEXT,
            created_at   TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
            FOREIGN KEY (short_name) REFERENCES teachers(short_name) ON DELETE SET NULL
        )
    """)
    conn.commit()

    c.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            short_name TEXT PRIMARY KEY,
            FOREIGN KEY (short_name) REFERENCES teachers(short_name) ON DELETE CASCADE
        )
    """)
    conn.commit()

    c.execute("""
        CREATE TABLE IF NOT EXISTS logins (
            short_name TEXT NOT NULL UNIQUE,
            password   TEXT NOT NULL,
            FOREIGN KEY (short_name) REFERENCES teachers(short_name) ON DELETE CASCADE
        )
    """)
    conn.commit()

def _seed_table():
    teachers = [
        ("ADMIN", "Administrator", "admin@example.com"),
        ("PSM", "Poon Sin Man", "psm@lkpfc.edu.hk"),
        ("YWY", "Yau Wing Yiu", "ywy@lkpfc.edu.hk"),
        ("YHN", "Yue Hin Nang", "yhn@lkpfc.edu.hk"),
        ("MHC", "Ma Ho Ching", "mhc@lkpfc.edu.hk"),
        ("CYT", "Cheung Yat Tak", "cyt@lkpfc.edu.hk"),
        ("KTL", "Kwok Tsz Ling", "ktl@lkpfc.edu.hk"),
        ("CNY", "Chow Ngo Yin", "cny@lkpfc.edu.hk"),
        ("LHN", "Lee Hiu Nam", "lhn@lkpfc.edu.hk"),
    ]

    c.execute("SELECT COUNT(*) FROM teachers")
    (count,) = c.fetchone()
    if count == 0:
        for short_name, full_name, email in teachers:
            c.execute(
                "INSERT OR IGNORE INTO teachers (short_name, full_name, email) VALUES (?, ?, ?)",
                (short_name, full_name, email),
            )
        conn.commit()

    logins = [
        ("PSM", "Psm8654#"),
        ("YWY", "Ywy8654!"),
        ("YHN", "yhn8654@"),
        ("MHC", "mhc8654#"),
        ("CYT", "cyt8654!"),
        ("KTL", "ktl8654@"),
        ("CNY", "cny8654#"),
        ("LHN", "lhn8654!"),
    ]
    c.execute("SELECT COUNT(*) FROM logins")
    (count,) = c.fetchone()
    if count == 0:
        for short_name, password in logins:
            c.execute(
                "INSERT OR IGNORE INTO logins (short_name, password) VALUES (?, ?)",
                (short_name, password),
            )
        conn.commit()

    rooms = [
        (101, "Room 101", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/Pz9Lloc.jpg"),
        (102, "Room 102", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/Pz9Lloc.jpg"),
        (103, "Room 103", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/Pz9Lloc.jpg"),
        (104, "Room 104", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/Pz9Lloc.jpg"),
        (201, "Room 201", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/UBaU7gj.jpg"),
        (202, "Room 202", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/UBaU7gj.jpg"),
        (203, "Room 203", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/UBaU7gj.jpg"),
        (204, "Room 204", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/UBaU7gj.jpg"),
        (901, "Student Activity Center (SAC)", 200, "A dynamic, versatile space designed for student engagement.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/LUAkUcx.jpg"),
        (902, "Aesthetic Activities Room (AA Room)", 200, "A versatile space for activities and events.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/sO0SIUk.jpg"),
        (903, "School Hall", 700, "A spacious, multi-purpose hall.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/m4fciYI.jpg"),
        (904, "Cover Playground", 500, "A sheltered playground offering weather protection.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/uhbOBpC.jpg"),
        ]
    c.execute("SELECT COUNT(*) FROM rooms")
    (count,) = c.fetchone()
    if count == 0:
        for room_id, name, capacity, description, equipment, img_url in rooms:
            c.execute(
                "INSERT OR IGNORE INTO rooms (id, name, capacity, description, equipment, img_url) VALUES (?, ?, ?, ?, ?, ?)",
                (room_id, name, capacity, description, equipment, img_url),
            )
        conn.commit()

def _init_db():
    _create_tables()
    _seed_table()

_init_db()

def verify_login(short_name: str, password: str) -> Optional[Teacher]:
    short = short_name.strip()
    c.execute("SELECT password FROM logins WHERE LOWER(short_name) = LOWER(?)", (short,))
    login = c.fetchone()
    if not login or password != login[0]:
        return None
    c.execute("SELECT * FROM teachers WHERE LOWER(short_name) = LOWER(?)", (short,))
    t = c.fetchone()
    if not t:
        return None
    return Teacher(*t)

def all_login_info() -> List[dict]:
    c.execute("SELECT * FROM logins")
    rows = c.fetchall()
    return [{"short_name": r[0], "password": r[1]} for r in rows]

def get_all_rooms():
    c.execute("SELECT * FROM rooms ORDER BY id")
    rows = c.fetchall()
    return [Room(row[0], row[1], row[2], row[3], row[5], row[4]) for row in rows]

def get_bookings(room_id: Optional[int] = None, booking_date_filter: Optional[date] = None) -> List[Booking]:
    q = "SELECT b.*, r.name AS room_name FROM bookings b JOIN rooms r ON r.id = b.room_id"
    clauses = []
    params = ()
    if room_id is not None:
        clauses.append("b.room_id = ?")
        params += (room_id,)
    if booking_date_filter is not None:
        clauses.append("b.booking_date = ?")
        params += (booking_date_filter.isoformat(),)
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY b.booking_date, b.start_time"
    c.execute(q, params)
    rows = c.fetchall()
    return [_booking_from_row(r) for r in rows]

def _booking_from_row(r: Tuple) -> Booking:
    def parse_time(t: str):
        if not t: return None
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(t, fmt).time()
            except ValueError:
                pass
        return None

    def parse_date(d: str):
        if not d: return None
        try:
            return datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            return None

    def parse_created_at(s: str):
        if not s: return None
        try:
            return datetime.fromisoformat(s)
        except:
            return datetime.now()

    return Booking(
        id=r[0] if len(r) > 0 else 0,
        room_id=r[1] if len(r) > 1 else 0,
        room_name=r[10] if len(r) > 10 else "Unknown",  # r.name is 11th column (index 10)
        booking_date=parse_date(r[3] if len(r) > 3 else None),
        start_time=parse_time(r[4] if len(r) > 4 else None),
        end_time=parse_time(r[5] if len(r) > 5 else None),
        visitor_name=r[6] if len(r) > 6 else "",
        visitor_email=r[7] if len(r) > 7 else "",
        short_name=r[2] if len(r) > 2 else None,
        purpose=r[8] if len(r) > 8 else None,
        created_at=parse_created_at(r[9] if len(r) > 9 else None),
    )

def create_booking(
    room_id: int,
    visitor_name: str,
    visitor_email: str,
    booking_date: date,
    start_time: time,
    end_time: time,
    purpose: Optional[str] = None,
    short_name: Optional[str] = None,
) -> bool:
    c.execute("""
        INSERT INTO bookings
        (room_id, booking_date, start_time, end_time,
         visitor_name, visitor_email, purpose, short_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        room_id,
        booking_date.isoformat(),
        start_time.strftime("%H:%M"),
        end_time.strftime("%H:%M"),
        visitor_name.strip(),
        visitor_email.strip().lower(),
        purpose,
        short_name,
    ))
    conn.commit()
    return True

def delete_booking_by_id(booking_id: int) -> bool:
    c.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    return True

def count_bookings() -> int:
    c.execute("SELECT COUNT(*) FROM bookings")
    (count,) = c.fetchone()
    return count

def is_available(room_id: int, booking_date: date, start_time: time, end_time: time) -> bool:
    c.execute("""
        SELECT 1 FROM bookings 
        WHERE room_id = ? AND booking_date = ? 
        AND NOT (end_time <= ? OR start_time >= ?)
    """, (
        room_id,
        booking_date.isoformat(),
        start_time.strftime("%H:%M:%S"),
        end_time.strftime("%H:%M:%S"),
    ))
    row = c.fetchone()
    return row is None


def update_booking(
    booking_id: int,
    room_id: int,
    visitor_name: str,
    visitor_email: str,
    booking_date: date,
    start_time: time,
    end_time: time,
    purpose: Optional[str],
    short_name: str) -> bool:
    c.execute(
        """
        UPDATE bookings
        SET room_id = ?, booking_date = ?, start_time = ?, end_time = ?,
            visitor_name = ?, visitor_email = ?, purpose = ?, short_name = ?
        WHERE id = ?
        """,
        (
            room_id,
            booking_date.isoformat(),
            start_time.strftime("%H:%M:%S"),
            end_time.strftime("%H:%M:%S"),
            visitor_name.strip(),
            visitor_email.strip().lower(),
            purpose,
            short_name.strip().upper(),
            booking_id,
        )
    )
    conn.commit()
    return True

def delete_booking() -> bool:
    c.execute("DELETE FROM bookings")
    conn.commit()
    return True

def is_available_excluding(
    booking_id: int,
    room_id: int,
    booking_date: date,
    start_time: time,
    end_time: time,
) -> bool:
    c.execute(
        "SELECT 1 FROM bookings WHERE room_id = ? AND booking_date = ? AND id != ? AND NOT (end_time <= ? OR start_time >= ?)",
        (
            room_id,
            booking_date.isoformat(),
            booking_id,
            start_time.strftime("%H:%M:%S"),
            end_time.strftime("%H:%M:%S"),
        )
    )
    row = c.fetchone()
    return row is None

def query_bookings(
    room_id: Optional[int] = None,
    date_mode: str = "All Dates",
    booking_date: Optional[date] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    time_from: Optional[time] = None,
    time_to: Optional[time] = None,
    reserver: Optional[str] = None,
    purpose: Optional[str] = None,
    short_name: Optional[str] = None
) -> List[Booking]:
    q = "SELECT b.*, r.name AS room_name FROM bookings b JOIN rooms r ON r.id = b.room_id"
    clauses = []
    params = ()

    if room_id is not None:
        clauses.append("b.room_id = ?")
        params += (room_id,)

    if date_mode == "Specific Date" and booking_date is not None:
        clauses.append("b.booking_date = ?")
        params += (booking_date.isoformat(),)
    elif date_mode == "Specific Month/Year":
        if year is not None:
            clauses.append("strftime('%Y', b.booking_date) = ?")
            params += (f"{int(year):04d}",)
        if month is not None:
            clauses.append("strftime('%m', b.booking_date) = ?")
            params += (f"{int(month):02d}",)

    if time_from and time_to:
        clauses.append("NOT (b.end_time <= ? OR b.start_time >= ?)")
        params += (time_from.strftime("%H:%M:%S"), time_to.strftime("%H:%M:%S"))
    elif time_from:
        clauses.append("b.end_time >= ?")
        params += (time_from.strftime("%H:%M:%S"),)
    elif time_to:
        clauses.append("b.start_time <= ?")
        params += (time_to.strftime("%H:%M:%S"),)

    if reserver:
        clauses.append("LOWER(b.visitor_name) LIKE ?")
        params += (f"%{reserver.strip().lower()}%",)
    if purpose:
        clauses.append("LOWER(b.purpose) LIKE ?")
        params += (f"%{purpose.strip().lower()}%",)
    if short_name:
        clauses.append("UPPER(b.short_name) LIKE ?")
        params += (f"%{short_name.strip().upper()}%",)

    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY b.booking_date, b.start_time"

    c.execute(q, params)
    rows = c.fetchall()
    return [_booking_from_row(r) for r in rows]

def get_admins() -> List[str]:
    c.execute("SELECT short_name FROM admins")
    rows = c.fetchall()
    return [row[0] for row in rows]

def add_admin(short_name: str) -> bool:
    c.execute("INSERT OR IGNORE INTO admins (short_name) VALUES (?)", (short_name,))
    conn.commit()
    return True

def remove_admin(short_name: str) -> bool:
    c.execute("DELETE FROM admins WHERE short_name = ?", (short_name,))
    conn.commit()
    return True

def is_admin_check(short_name: str) -> bool:
    c.execute("SELECT 1 FROM admins WHERE short_name = ?", (short_name,))
    r = c.fetchone()
    return r is not None

def get_admins_info() -> List[str]:
    c.execute("SELECT full_name, email FROM teachers t, admins a WHERE t.short_name = a.short_name")
    rows = c.fetchall()
    return [f'<b>{row[0]}</b> - {row[1]}' for row in rows]

def list_teachers() -> List[Teacher]:
    c.execute("""
        SELECT t.short_name, t.full_name, t.email
        FROM teachers t
        LEFT JOIN admins a ON t.short_name = a.short_name
        ORDER BY a.short_name IS NOT NULL DESC, t.short_name ASC
    """)
    rows = c.fetchall()
    return [Teacher(*row) for row in rows]

def list_teachers_with_passwords() -> List[dict]:
    teachers = list_teachers()
    c.execute("SELECT * FROM logins")
    pw_map = {row[0]: row[1] for row in c.fetchall()}
    return [{"short_name": t.short_name, "full_name": t.full_name, "email": t.email, "password": pw_map.get(t.short_name)} for t in teachers]

def list_teacher_short_name(short_name: str) -> bool:
    c.execute("SELECT 1 FROM teachers WHERE short_name = ?", (short_name,))
    r = c.fetchone()
    return r is not None

def create_teacher(short_name: str, full_name: str, email: str, password: str) -> bool:
    c.execute("INSERT INTO teachers (short_name, full_name, email) VALUES (?, ?, ?)", (short_name, full_name, email))
    c.execute(
        "INSERT INTO logins (short_name, password) VALUES (?, ?) ON CONFLICT(short_name) DO UPDATE SET password = excluded.password",
        (short_name, password)
    )
    conn.commit()
    return True

def update_teacher(short_name: str, full_name: str, email: str, password: Optional[str] = None) -> bool:
    c.execute("UPDATE teachers SET full_name = ?, email = ? WHERE short_name = ?", (full_name, email, short_name))
    if password and password.strip():
        c.execute("UPDATE logins SET password = ? WHERE short_name = ?", (password.strip(), short_name))
    conn.commit()
    return True

def rename_teacher(old_short_name: str, new_short_name: str) -> bool:
    c.execute("SELECT 1 FROM teachers WHERE short_name = ?", (new_short_name,))
    r = c.fetchone()
    if r:
        return False
    c.execute("UPDATE teachers SET short_name = ? WHERE short_name = ?", (new_short_name, old_short_name))
    conn.commit()
    return True

def delete_teacher(short_name: str) -> bool:
    c.execute("DELETE FROM teachers WHERE short_name = ?", (short_name,))
    conn.commit()
    return True
