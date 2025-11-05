import sqlite3
import pandas as pd
import io
from pathlib import Path

DB_NAME = "bot.db"

def init_db():
    """Initialize database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Table for promoters
    cur.execute("""
    CREATE TABLE IF NOT EXISTS promoters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        name TEXT,
        lang TEXT,
        age TEXT,
        phone TEXT,
        region TEXT
    )
    """)

    # Table for respondents (q1–q7 only)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS respondents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        promoter_id INTEGER,
        name TEXT,
        gender TEXT,
        age TEXT,
        phone TEXT,
        q1 TEXT,
        q2 TEXT,
        q3 TEXT,
        q4 TEXT,
        q5 TEXT,
        q6 TEXT,
        q7 TEXT,
        q8 TEXT,
        q9 TEXT,
        region TEXT,
        FOREIGN KEY(promoter_id) REFERENCES promoters(id)
    )
    """)
    conn.commit()
    conn.close()


def add_promoter(user_id, name, age, phone, lang, region):
    """Add or update promoter info."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO promoters (user_id, name, age, phone, lang, region)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, name, age, phone, lang, region))
    conn.commit()
    conn.close()


def get_promoter_id(user_id):
    """Return promoter_id from Telegram user_id."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id FROM promoters WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def add_respondent(promoter_user_id, data):
    """Add respondent (auto-merging q2_selected/q3_selected into q2/q3)."""
    promoter_id = get_promoter_id(promoter_user_id)
    if promoter_id is None:
        return False

    def join_value(key):
        val = data.get(key)
        if isinstance(val, (list, set)):
            return ", ".join(val)
        return val

    # Merge q2_selected/q3_selected into q2/q3
    q2_value = join_value("q2_selected") or join_value("q2")
    q3_value = join_value("q3_selected") or join_value("q3")
    
    region = data.get("region", "default")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO respondents (
            promoter_id, name, gender, age, phone,
            q1, q2, q3, q4, q5, q6, q7, q8, q9, region
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        promoter_id,
        data.get("name"),
        data.get("gender"),
        data.get("age"),
        data.get("phone"),
        data.get("q1"),
        q2_value,
        q3_value,
        data.get("q2"),
        data.get("q3"),
        data.get("q4"),
        data.get("q5"),
        data.get("q6"),
        data.get("q7"),
        region
    ))
    conn.commit()
    conn.close()
    return True

def export_respondents_to_excel_bytes():
    conn = sqlite3.connect("bot.db")
    df = pd.read_sql("SELECT * FROM respondents", conn)
    conn.close()

    if df.empty:
        return None

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="respondents")
    buf.seek(0)
    return buf

def export_promoters_to_excel_bytes():
    conn = sqlite3.connect("bot.db")
    df = pd.read_sql("SELECT * FROM promoters", conn)
    conn.close()

    if df.empty:
        return None

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="promoters")
    buf.seek(0)
    return buf