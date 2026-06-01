import sqlite3
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import streamlit as st
from supabase import create_client

DB_FILE = "chores.db"

BJ_TZ = ZoneInfo("Asia/Shanghai")

# database connection and initialization

@st.cache_resource

def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def now_bj_iso():
    return datetime.now(BJ_TZ).isoformat()

def format_bj_time(value):
    if not value:
        return ""
    
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(BJ_TZ).strftime("%Y-%m-%d %H:%M:%S")

def beijing_day_utc_range(date_str):
    start_bj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=BJ_TZ)
    end_bj = start_bj + timedelta(days=1)

    start_utc = start_bj.astimezone(timezone.utc).isoformat()
    end_utc = end_bj.astimezone(timezone.utc).isoformat()

    return start_utc, end_utc


def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    pass




# application functions

# tab1 - meals

def add_meal(date, meal_type, content):
    supabase = get_supabase_client()

    result = supabase.table("meals").insert({
        "date": date,
        "meal_type": meal_type,
        "content": content,
        "created_at": now_bj_iso(),
    }).execute()

    return result

def get_meals_by_date(date):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("meals")
        .select("*")
        .eq("date", date)
        .order("id", desc=True)
        .execute()
    )

    meals = []
    
    for row in result.data:
        meals.append({
            "id": row["id"],
            "date": row["date"],
            "meal_type": row["meal_type"],
            "content": row["content"],
            "created_at": format_bj_time(row["created_at"]),
        })

    return meals




# tab2 - chores

def add_chore(title):
    supabase = get_supabase_client()

    result = supabase.table("chores").insert({
        "title": title,
        "created_at": now_bj_iso(),
        "completed": False,
        "completed_by": None,
        "completed_at": None,
    }).execute()

    return result

def get_all_chores():
    supabase = get_supabase_client()

    result = (
        supabase
        .table("chores")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    chores = []
    for row in result.data:
        chores.append({
            "id": row["id"],
            "title": row["title"],
            "created_at": format_bj_time(row["created_at"]),
            "completed": bool(row["completed"]),
            "completed_by": row["completed_by"] or "",
            "completed_at": format_bj_time(row["completed_at"]),
        })

    return chores

def complete_chore(chore_id, user_name):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("chores")
        .update({
            "completed": True,
            "completed_by": user_name,
            "completed_at": now_bj_iso(),
        })
        .eq("id", int(chore_id))
        .execute()
    )

    return result

def undo_chore(chore_id):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("chores")
        .update({
            "completed": False,
            "completed_by": None,
            "completed_at": None,
        })
        .eq("id", int(chore_id))
        .execute()
    )

    return result




# tab3 - refrige inventory

def add_inventory_item(name, quantity, unit, location, category, added_date, shelf_life_days):
    supabase = get_supabase_client()

    result = supabase.table("inventory").insert({
        "name": name,
        "quantity": quantity,
        "unit": unit,
        "location": location,
        "category": category,
        "added_date": added_date,
        "shelf_life_days": shelf_life_days,
        "updated_at": now_bj_iso(),
    }).execute()

    return result

def get_all_inventory_items():
    supabase = get_supabase_client()

    result = (
        supabase
        .table("inventory")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    items = []

    for row in result.data:
        items.append({
            "id": row["id"],
            "name": row["name"],
            "quantity": float(row["quantity"] or 0),
            "unit": row["unit"],
            "location": row.get("location") or "",
            "category": row.get("category") or "",
            "added_date": row.get("added_date") or "",
            "shelf_life_days": row.get("shelf_life_days"),
            "updated_at": format_bj_time(row["updated_at"]),
        })

    return items

def delete_inventory_item(item_id):
    supabase = get_supabase_client()

    existing = (
        supabase
        .table("inventory")
        .select("id")
        .eq("id", int(item_id))
        .execute()
    )

    if not existing.data:
        return 0

    supabase.table("inventory").delete().eq("id", int(item_id)).execute()

    return 1

def update_inventory_quantity(item_id, new_quantity):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("inventory")
        .update({
            "quantity": new_quantity,
            "updated_at": now_bj_iso(),
        })
        .eq("id", int(item_id))
        .execute()
    )

    return result



# tab4 - supplement logs

def add_supplement_log(supplement_name, dosage, unit, note):
    supabase = get_supabase_client()

    now = now_bj_iso()

    result = supabase.table("supplement_logs").insert({
        "supplement_name": supplement_name,
        "dosage": dosage,
        "unit": unit,
        "note": note,
        "taken_at": now,
        "created_at": now,
    }).execute()

    return result

# def get_recent_supplement_logs(limit=50):
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

    start_time, end_time = beijing_day_utc_range(date)

    result = (
        supabase
        .table("supplement_logs")
        .select("*")
        .gte("taken_at", start_time)
        .lt("taken_at", end_time)
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
            "taken_at": format_bj_time(row["taken_at"]),
            "created_at": format_bj_time(row["created_at"]),
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