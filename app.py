import streamlit as st
from database import (
    init_db, 
    add_chore, 
    get_all_chores, 
    complete_chore, 
    undo_chore, 
    add_meal, 
    get_meals_by_date,
    add_inventory_item,
    get_all_inventory_items,
    delete_inventory_item
    )

tab1, tab2, tab3 = st.tabs(["Chores", "Meals", "Inventory"])

with tab1:
    st.header("Chores")

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


with tab2:
    st.header("Meals")

    selected_date = st.date_input("Select date", key="meal_date")
    meal_type = st.selectbox("Meal type", ["Breakfast", "Lunch", "Dinner"], key = "meal_type")
    meal_content = st.text_input("What to eat?", key = "meal_content")

    if st.button("Add Meal", key = "add_meal_btn", use_container_width=True):
        if meal_content.strip():
            add_meal(str(selected_date), meal_type, meal_content.strip())
            st.rerun()
        else:
            st.warning("Please enter meal content.")

    st.subheader("Meals for seleccted date")
    meals = get_meals_by_date(str(selected_date))

    if not meals:
        st.caption("No meals recoreded yet.")
    else:
        for meal in meals:
            st.markdown(f"**{meal['meal_type'].title()}** - {meal['content']}")
            st.caption(f"Created at {meal['created_at']}")
            st.divider()



with tab3:
    st.header("Inventory")

    item_name = st.text_input("Item name", key="inventory_item_name")
    item_quantity = st.number_input("Quantity", min_value=0.0, step=1.0, key="inventory_quantity")
    item_unit = st.selectbox(
        "Unit",
        ["pcs", "box", "bag", "bottle","kg", "g", "L", "ml"],
        key="inventory_unit"
    )

    if st.button("Add Item", key="add_inventory_btn", use_container_width=True):
        if item_name.strip():
            add_inventory_item(item_name.strip(), item_quantity, item_unit)
            st.success("Item added to inventory.")
            st.rerun()
        else:
            st.warning("Please enter an item name.")

    st.subheader("Current Inventory")
    items = get_all_inventory_items()

    if not items:
        st.caption("No inventory items yet.")
    else:
        for item in items:
            col1, col2 = st.columns([6, 1.5])

            with col1:
                st.markdown(f"**{item['name']}** - {item['quantity']} {item['unit']}")
                st.caption(f"Updated at {item['updated_at']}")

            with col2:
                if st.button("Delete", key=f"delete_item_{item['id']}", use_container_width=True):
                    delete_inventory_item(item["id"])
                    st.rerun()

            st.divider()
