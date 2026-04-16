import streamlit as st
from database import init_db, add_chore, get_all_chores, complete_chore, undo_chore

st.set_page_config(page_title="Housework Tracker", page_icon="🧹", layout = "centered")
init_db()
st.title("🧹 Housework Tracker")

current_user = st.selectbox("Current user", ["Vera", "Ping Ping"])

st.divider()

st.subheader("Add a new chore")
new_title = st.text_input("What needs to be done?", label_visibility="collapsed", placeholder="Enter a chore...")

if st.button("Add chore", use_container_width=True):
    if new_title.strip():
        add_chore(new_title.strip())
        st.success("Chore added.")
        st.rerun()
    else:
        st.warning("Please enter a chore title.")

st.divider()

chores = get_all_chores()
todo_chores = [chore for chore in chores if not chore["completed"]]
done_chores = [chore for chore in chores if chore["completed"]]

st.subheader("To Do")

if not todo_chores:
    st.caption("Nothing here. Nice.")
else:
    for chore in todo_chores:
        col1, col2 = st.columns([6,1.5])

        with col1:
            st.markdown(f"### ○ {chore['title']}")
            st.caption(f"Created at {chore['created_at']}")

        with col2:
            if st.button("Done", key = f"complete_{chore['id']}", use_container_width=True):
                complete_chore(chore["id"], current_user)
                st.rerun()
        
        st.divider()

with st.expander(f"Completed ({len(done_chores)})", expanded=False):
    if not done_chores:
        st.caption("No completed chores yet.")
    else:
        for chore in done_chores:
            col1, col2 = st.columns([6,1.5])

            with col1:
                st.markdown(f"### ✓ ~~{chore['title']}~~")
                st.caption(f"Done by {chore['completed_by']} at {chore['completed_at']}")

            with col2:
                if st.button("Undo", key = f"undo_{chore['id']}", use_container_width=True):
                    undo_chore(chore["id"])
                    st.rerun()
            
            st.divider()