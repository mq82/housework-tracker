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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
             )
        """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def add_meal(date, meal_type, content):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO meals (date, meal_type, content, created_at)
        VALUES (?, ?, ?, ?)
                   """, (
                       date, 
                       meal_type, 
                       content, 
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

def get_meals_by_date(date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, meal_type, content, created_at
        FROM meals
        WHERE date = ?
        order by id desc
                   """, (date,))
    
    rows = cursor.fetchall()
    conn.close()

    meals = []
    for row in rows:
        meals.append({
            "id": row[0],
            "date": row[1],
            "meal_type": row[2],
            "content": row[3],
            "created_at": row[4]
        })

    return meals

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


def add_inventory_item(name, quantity, unit):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO inventory (name, quantity, unit, updated_at)
        VALUES (?, ?, ?, ?)
                   """, (
                       name, 
                       quantity, 
                       unit, 
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

def get_all_inventory_items():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, quantity, unit, updated_at
        FROM inventory
        order by id desc
                   """)
    
    rows = cursor.fetchall()
    conn.close()

    items = []
    for row in rows:
        items.append({
            "id": row[0],
            "name": row[1],
            "quantity": row[2],
            "unit": row[3],
            "updated_at": row[4]
        })

    return items

def delete_inventory_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM inventory
        WHERE id = ?
                   """, (item_id,))

    conn.commit()
    conn.close()
