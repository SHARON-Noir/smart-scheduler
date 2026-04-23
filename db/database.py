import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "events.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            date TEXT,
            time TEXT,
            reminder_1day_sent INTEGER DEFAULT 0,
            reminder_1hour_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_event(chat_id: int, title: str, date: str, time: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (chat_id, title, date, time) VALUES (?, ?, ?, ?)",
        (chat_id, title, date, time)
    )
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return event_id

def get_pending_reminders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, chat_id, title, date, time,
               reminder_1day_sent, reminder_1hour_sent
        FROM events
        WHERE date IS NOT NULL AND time IS NOT NULL
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def mark_reminder_sent(event_id: int, reminder_type: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if reminder_type == "1day":
        cursor.execute(
            "UPDATE events SET reminder_1day_sent = 1 WHERE id = ?",
            (event_id,)
        )
    elif reminder_type == "1hour":
        cursor.execute(
            "UPDATE events SET reminder_1hour_sent = 1 WHERE id = ?",
            (event_id,)
        )
    conn.commit()
    conn.close()

def get_all_events(chat_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, date, time FROM events WHERE chat_id = ? ORDER BY date, time",
        (chat_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_event(event_id: int, chat_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM events WHERE id = ? AND chat_id = ?",
        (event_id, chat_id)
    )
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted