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
    delete_inventory_item,
    update_inventory_quantity
    )
from datetime import datetime, timedelta

st.set_page_config(page_title="Housework Tracker", page_icon="🧹", layout="centered")
init_db()

 # ------- 2 calculation functions -------

def calculate_expiry(added_date, shelf_life_days):
    if not shelf_life_days:
        return None

    added = datetime.strptime(added_date, "%Y-%m-%d")
    expiry = added + timedelta(days=shelf_life_days)
    days_left = (expiry.date() - datetime.now().date()).days

    return expiry, days_left

def get_inventory_sort_key(item):
    expiry_info = calculate_expiry(item["added_date"], item["shelf_life_days"])
    
    if not expiry_info:
        return 9999  #没有保质期的排最后
    
    _, days_left = expiry_info
    return days_left





tab1, tab2, tab3 = st.tabs(["Chores", "Meals", "Inventory"])

with tab1:
    st.header("Chores")
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


# -------- expiry calculation --------
def calculate_expiry(added_date, shelf_life_days):
    if not shelf_life_days:
        return None
    
    added = datetime.strptime(added_date, "%Y-%m-%d")
    expiry = added + timedelta(days=shelf_life_days)
    days_left = (expiry.date() - datetime.now().date()).days

    return expiry, days_left

def get_sort_key(item):
    expiry_info = calculate_expiry(item["added_date"], item["shelf_life_days"])

    if not expiry_info:
        return 9999
    
    _, days_left = expiry_info
    return days_left


with tab3:
    # ====== Inventory Input ======
    st.header("Inventory")

    # -----------------------------
    # Add new inventory item
    # -----------------------------
    st.subheader("Add Item")

    col1, col2 = st.columns(2)

    with col1:
        item_name = st.text_input("Item name", key="inv_name")
        item_quantity = st.number_input(
            "Quantity",
            min_value=0.0,
            step=1.0,
            key="inv_qty"
        )
        item_unit = st.selectbox(
            "Unit",
            ["pcs", "box", "bag", "bottle","kg", "g", "L", "ml"],
            key="inv_unit"
        )

    with col2:
        item_location = st.selectbox(
            "Location",
            ["fridge", "freezer"],
            key="inv_location"
        )
        item_category = st.selectbox(
            "Category", 
            [
                "vegetable",
                "fruit",
                "meat",
                "seafood",
                "grain",
                "dairy",
                "eggs",
                "condiment",
                "herb/spice",
                "fermented",
                "other"
            ],
            key="inv_category"
        )
        
    added_date = st.date_input("Added date", key="inv_added_date")
    
    shelf_life = st.number_input(
        "Shelf life (days)",
        min_value=0,
        step=1,
        key="inv_shelf_life"
    )

    if st.button("Add Item", key="inv_add_btn", use_container_width=True):
        if item_name.strip():
            add_inventory_item(
                item_name.strip(),
                item_quantity,
                item_unit,
                item_location,
                item_category,
                str(added_date),
                shelf_life if shelf_life > 0 else None,
            )
            st.success("Item added to inventory.")
            st.rerun()
        else:
            st.warning("Please enter an item name.")
    st.divider()

    # -----------------------------
    # Inventory list
    # -----------------------------
    st.subheader("Current Inventory")

    # ===== Inventory Items Filtering and Sorting =====

    items = get_all_inventory_items()
    items = sorted(items, key=get_inventory_sort_key)

    # ===== filters =====
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        filter_location = st.selectbox(
            "Filter by location",
            ["all", "fridge", "freezer"],
            key="filter_location"
        )

    with filter_col2:
        filter_category = st.selectbox(
            "Filter by category",
            [
                "all",
                "vegetable",
                "fruit",
                "meat",
                "seafood",
                "grain",
                "dairy",
                "eggs",
                "condiment",
                "herb/spice",
                "fermented",
                "other"
            ],
            key="filter_category"
        )

    with filter_col3:
        filter_expiry = st.selectbox(
            "Filter by status",
            ["all", "expiring soon", "expired", "no shelf life"],
            key="filter_expiry"
        )

    filtered_items = []

    for item in items:
        expiry_info = calculate_expiry(item["added_date"], item["shelf_life_days"])
        
        if filter_location != "all" and item["location"] != filter_location:
            continue

        if filter_category != "all" and item["category"] != filter_category:
            continue

        if filter_expiry == "expired":
            if not expiry_info or expiry_info[1] >= 0:
                continue
        elif filter_expiry == "expiring soon":
            if not expiry_info or not (0 <= expiry_info[1] <= 2):
                continue
        elif filter_expiry == "no shelf life":
            if expiry_info:
                continue
        
        filtered_items.append(item)


    # -----------------------------
    # Display inventory
    # -----------------------------
    if not filtered_items:
        st.caption("No items in inventory.")
    else:
        for item in filtered_items:
            expiry_info = calculate_expiry(item["added_date"], item["shelf_life_days"])

            col1, col2, col3, col4 = st.columns([5, 1, 1, 1.5])

            with col1:
                st.markdown(f"### {item['name']} - {item['quantity']} {item['unit']}")
                st.caption(f"{item['location']} | {item['category']} | Added at: {item['added_date']}")
                
                if expiry_info:
                    expiry, days_left = expiry_info
                    expiry_date = expiry.strftime("%Y-%m-%d")

                    if days_left < 0:
                        st.error(f"Expired {-days_left} days ago ❕ | Expiry date: {expiry_date}")
                    elif days_left <= 2:
                        st.warning(f"Expiring in {days_left} days ⚠️ | Expiry date: {expiry_date}")
                    else:
                        st.caption(f"Expires in {days_left} days | Expiry date: {expiry_date}")
                else:
                    st.caption("No shelf life set.")
                
                st.caption(f"Last updated at: {item['updated_at']}")

            with col2:
                if st.button("-", key = f"minus_{item['id']}", use_container_width=True):
                    new_quantity = max(0, item["quantity"] - 1)
                    update_inventory_quantity(item["id"], new_quantity)
                    st.rerun()

            with col3:
                if st.button("+", key = f"plus_{item['id']}", use_container_width=True):
                    new_quantity = item["quantity"] + 1
                    update_inventory_quantity(item["id"], new_quantity)
                    st.rerun()
            
            with col4:
                if st.button("Delete", key = f"delete_{item['id']}", use_container_width=True):
                    delete_inventory_item(item["id"])
                    st.rerun()
            
            st.divider()