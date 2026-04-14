import streamlit as st
import json
import os
from datetime import datetime

DATA_FILE = "chores.json"


def load_chores():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_chores(chores):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(chores, f, ensure_ascii=False, indent=2)


def generate_id(chores):
    if not chores:
        return "00000001"
    max_id = max(int(chore["id"]) for chore in chores)
    return str(max_id + 1).zfill(8)


def add_chore(title):
    chores = load_chores()
    new_chore = {
        "id": generate_id(chores),
        "title": title,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "completed": False,
        "completed_by": "",
        "completed_at": ""
    }
    chores.append(new_chore)
    save_chores(chores)


def complete_chore(chore_id, user_name):
    chores = load_chores()
    for chore in chores:
        if chore["id"] == chore_id:
            chore["completed"] = True
            chore["completed_by"] = user_name
            chore["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    save_chores(chores)


def undo_chore(chore_id):
    chores = load_chores()
    for chore in chores:
        if chore["id"] == chore_id:
            chore["completed"] = False
            chore["completed_by"] = ""
            chore["completed_at"] = ""
            break
    save_chores(chores)


st.set_page_config(page_title="Housework Tracker", page_icon="🧹")
st.title("🧹 Housework Tracker")

current_user = st.selectbox("Current user", ["Vera", "Husband"])

st.subheader("Add a new chore")
new_title = st.text_input("Chore title")

if st.button("Add chore"):
    if new_title.strip():
        add_chore(new_title.strip())
        st.success("Chore added.")
        st.rerun()
    else:
        st.warning("Please enter a chore title.")

st.subheader("Chore list")
chores = load_chores()

if not chores:
    st.info("No chores yet.")
else:
    for chore in chores:
        col1, col2, col3 = st.columns([4, 2, 2])

        with col1:
            if chore["completed"]:
                st.markdown(f"~~{chore['title']}~~")
                st.caption(f"Done by {chore['completed_by']} at {chore['completed_at']}")
            else:
                st.markdown(chore["title"])
                st.caption(f"Created at {chore['created_at']}")

        with col2:
            if not chore["completed"]:
                if st.button("Complete", key=f"complete_{chore['id']}"):
                    complete_chore(chore["id"], current_user)
                    st.rerun()

        with col3:
            if chore["completed"]:
                if st.button("Undo", key=f"undo_{chore['id']}"):
                    undo_chore(chore["id"])
                    st.rerun()