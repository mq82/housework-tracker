import sqlite3
from datetime import datetime

DB_FILE = "chores.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL,
        completed INTEGER NOT NULL DEFAULT 0,
        completed_by TEXT,
        completed_at TEXT
                   )
                   """)
    conn.commit()
    conn.close()


def add_chore(title):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chores (title, created_at, completed, completed_by, completed_at)
        VALUES (?, ?, 0, '', '')
                   """, (title, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

def get_all_chores():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, created_at, completed, completed_by, completed_at
        FROM chores
        order by id desc
                   """)
    
    rows = cursor.fetchall()
    conn.close()

    chores = []
    for row in rows:
        chores.append({
            "id": row[0],
            "title": row[1],
            "created_at": row[2],
            "completed": bool(row[3]),
            "completed_by": row[4] or "",
            "completed_at": row[5] or ""
        })

    return chores

def complete_chore(chore_id, completed_by):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE chores
        SET completed = 1, completed_by = ?, completed_at = ?
        WHERE id = ?
                   """, (completed_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), chore_id))

    conn.commit()
    conn.close()

def undo_chore(chore_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE chores
        SET completed = 0, completed_by = '', completed_at = ''
        WHERE id = ?
                   """, (chore_id,))

    conn.commit()
    conn.close()