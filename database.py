import sqlite3
from datetime import datetime, timedelta

import streamlit as st
from supabase import create_client

DB_FILE = "chores.db"
@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

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
    supabase = get_supabase_client()

    result = supabase.table("supplement_logs").insert({
        "supplement_name": supplement_name,
        "dosage": dosage,
        "unit": unit,
        "note": note,
    }).execute()

    return result

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
    supabase = get_supabase_client()

    existing = (
        supabase
        .table("supplement_logs")
        .select("id")
        .eq("id", int(log_id))
        .execute()
    )

    if not existing.data:
        return 0
    
    supabase.table("supplement_logs").delete().eq("id", int(log_id)).execute()

    return 1


def get_supplement_logs_by_date(date):
    supabase = get_supabase_client()

    start_time = f"{date}T00:00:00"
    end_time = f"{date}T23:59:59"

    result = (
        supabase
        .table("supplement_logs")
        .select("*")
        .gte("taken_at", start_time)
        .lte("taken_at", end_time)
        .order("taken_at", desc=True)
        .execute()
    )

    logs = []
    for row in result.data:
        logs.append({
            "id": row["id"],
            "supplement_name": row["supplement_name"],
            "dosage": row["dosage"],
            "unit": row["unit"],
            "note": row.get("note") or "",
            "taken_at": row["taken_at"],
            "created_at": row["created_at"]
        })

    return logs

def get_supplement_daily_summary(date):
    logs = get_supplement_logs_by_date(date)

    summary_map = {}

    for log in logs:
        key = (log["supplement_name"], log["unit"])

        if key not in summary_map:
            summary_map[key] = 0

        summary_map[key] += float(log["dosage"] or 0)

    summary = []

    for (supplement_name, unit), total_dosage in summary_map.items():
        summary.append({
            "supplement_name": supplement_name,
            "total_dosage": total_dosage,
            "unit": unit
        })

    summary.sort(key=lambda x: x["supplement_name"])

    return summary