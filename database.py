import sqlite3
from datetime import datetime, timedelta

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
            location TEXT NOT NULL,
            category TEXT NOT NULL,
            added_date TEXT NOT NULL,
            shelf_life_days INTEGER,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS supplement_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplement_name TEXT NOT NULL,
            dosage REAL,
            unit TEXT,
            note TEXT,
            taken_at TEXT NOT NULL,
            created_at TEXT NOT NULL
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


def add_inventory_item(name, quantity, unit, location, category, added_date, shelf_life_days):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO inventory (name, quantity, unit, location, category, added_date, shelf_life_days, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   """, (
                       name, 
                       quantity, 
                       unit, 
                       location,
                       category,
                       added_date,
                       shelf_life_days,
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

def get_all_inventory_items():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, quantity, unit, location, category, added_date, shelf_life_days, updated_at
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
            "location": row[4],
            "category": row[5],
            "added_date": row[6],
            "shelf_life_days": row[7],
            "updated_at": row[8]
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

def update_inventory_quantity(item_id, new_quantity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE inventory
        SET quantity = ?,
            updated_at = ?
        WHERE id = ?
                   """, (
                       new_quantity,
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       item_id))

    conn.commit()
    conn.close()

def add_supplement_log(supplement_name, dosage, unit, note):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO supplement_logs
        (supplement_name, dosage, unit, note, taken_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
                   """, (
                       supplement_name,
                       dosage,
                       unit,
                       note,
                       now,
                       now
                   ))

    conn.commit()
    conn.close()

def get_recent_supplement_logs(limit=50):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, supplement_name, dosage, unit, note, taken_at, created_at
        FROM supplement_logs
        ORDER BY taken_at DESC
        LIMIT ?
                   """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()

    logs = []
    for row in rows:
        logs.append({
            "id": row[0],
            "supplement_name": row[1],
            "dosage": row[2],
            "unit": row[3],
            "note": row[4] or "",
            "taken_at": row[5],
            "created_at": row[6]
        })

    return logs


def delete_supplement_log(log_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM supplement_logs
        WHERE id = ?
                   """, (int(log_id),))
    
    deleted_count = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted_count

def get_supplement_logs_by_date(date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, supplement_name, dosage, unit, note, taken_at, created_at
        FROM supplement_logs
        WHERE substr(taken_at, 1, 10) = ?
        ORDER BY taken_at DESC
                   """, (date,))
    
    rows = cursor.fetchall()
    conn.close()

    logs = []
    for row in rows:
        logs.append({
            "id": row[0],
            "supplement_name": row[1],
            "dosage": row[2],
            "unit": row[3],
            "note": row[4] or "",
            "taken_at": row[5],
            "created_at": row[6]
        })

    return logs

def get_supplement_daily_summary(date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT supplement_name, unit, SUM(dosage)
        FROM supplement_logs
        WHERE substr(taken_at, 1, 10) = ?
        GROUP BY supplement_name, unit
        ORDER BY supplement_name
                   """, (date,))
    
    rows = cursor.fetchall()
    conn.close()

    summary = []
    for row in rows:
        summary.append({
            "supplement_name": row[0],
            "unit": row[1],
            "total_dosage": row[2]
        })

    return summary