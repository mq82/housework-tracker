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
    update_inventory_quantity,
    add_supplement_log,
    delete_supplement_log,
    get_supplement_logs_by_date,
    get_supplement_daily_summary,
    )
from datetime import datetime, timedelta

# ------- 1 database functions -------
def check_password():
    if "APP_PASSWORD" not in st.secrets:
        st.error("APP_PASSWORD is not configured in Streamlit Secrets.")
        st.stop()
    
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True
    
    st.title("🔐 Home App Login")

    password = st.text_input(
        "Enter password",
        type="password",
        key="app_password_input"
    )

    if st.button("Login", use_container_width=True):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state["authenticated"] = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")

    return False


st.set_page_config(page_title="Home App", page_icon="🏠", layout="centered")

if not check_password():
    st.stop()

init_db()

st.title("🏠 Home App")

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



# ------- 3 UI and tab functions -------

tab1, tab2, tab3, tab4 = st.tabs(["Chores", "Meals", "Inventory", "Supplements"])

with tab1:
    st.header("Chores")
    st.title("🧹 Housework Tracker")

    current_user = st.selectbox("Current user", ["Vera", "Ping Ping"])

    st.divider()

    with st.form("add_chore_form", clear_on_submit=True):
        new_title = st.text_input(
            "What needs to be done?",
            key="new_chore"
        )

        submitted = st.form_submit_button(
            "Add Chore",
            use_container_width=True
        )
        
        if submitted:
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

    with st.form("add_meal_form", clear_on_submit=True):
        selected_date = st.date_input(
            "Date",
            key="meal_date"
            )
        
        meal_type = st.selectbox(
            "Meal type",
            ["Breakfast", "Lunch", "Dinner"],
            key = "meal_type"
            )
        
        meal_content = st.text_input(
            "What to eat?",
            key = "meal_content"
        )

        submitted = st.form_submit_button(
            "Add Meal",
            use_container_width=True
        )

        if submitted:
            if meal_content.strip():
                add_meal(str(selected_date), meal_type, meal_content.strip())
                st.success("Meal added.")
                st.rerun()
            else:
                st.warning("Please enter meal content.")

    st.subheader("Meals for selected date")
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

    with st.form("add_inventory_form", clear_on_submit=True):
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
        submitted = st.form_submit_button("Add Item", use_container_width=True)

        if submitted:
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
                st.caption(f"Item ID: {item['id']}")

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



with tab4:
    st.header("Supplements Log")

    st.caption("Record what you take at the current time. No manual date/time input.")

    st.subheader("Add Supplement Log")

    with st.form("add_supplement_form", clear_on_submit=True):
        supplement_name = st.text_input(
            "Supplement name",
            placeholder="e.g. heme iron, magnesium, vitamin D",
            key="supplement_name"
        )

        col1, col2 = st.columns(2)

        with col1:
            dosage = st.number_input(
                "Dosage",
                min_value=0.0,
                step=1.0,
                key="supplement_dosage"
            )

        with col2:
            unit = st.selectbox(
                "Unit",
                [
                    "capsule(s)",
                    "tablet(s)",
                    "drop(s)",
                    "mg",
                    "g",
                    "IU",
                    "mcg"
                ],
                key="supplement_unit"
            )

        note = st.text_area(
            "Note",
            placeholder="Optional: after lunch, felt dizzy, with food, etc.",
            key="supplement_note"
        )

        submitted = st.form_submit_button("Add Log", use_container_width=True)

        if submitted:
            if supplement_name.strip():
                add_supplement_log(
                    supplement_name.strip(),
                    dosage,
                    unit,
                    note.strip()
                )
                st.success("Supplement log added.")
                st.rerun()
            else:
                st.warning("Please enter a supplement name.")

    st.divider()

    st.subheader("View by Date")

    selected_supplement_date = st.date_input(
        "Select date",
        key="supplement_date"
    )

    selected_date_str = str(selected_supplement_date)

    st.markdown(f"### Daily Summary - {selected_date_str}")

    summary = get_supplement_daily_summary(selected_date_str)

    if not summary:
        st.caption("No supplements recorded on this date.")
    else:
        for item in summary:
            st.markdown(f"- **{item['supplement_name']}**: {item['total_dosage']} {item['unit']}")
    
    st.divider()

    st.markdown(f"### Logs - {selected_date_str}")

    logs = get_supplement_logs_by_date(selected_date_str)

    st.caption(f"Debug: {len(logs)} logs found for {selected_date_str}.")

    if not logs:
        st.caption("No supplement logs for this date.")
    else:
        for log in logs:
            col1, col2 = st.columns([6,1.5])

            with col1:
                st.markdown(
                    f"### {log['supplement_name']} - {log['dosage']} {log['unit']}"
                )
                st.caption(f"Taken at: {log['taken_at']}")
                st.caption(f"Log ID: {log['id']}")
                
                if log["note"]:
                    st.caption(f"Note: {log['note']}")

            with col2:
                deleted_clicked = st.button(
                    "Delete",
                    key = f"delete_log_{log['id']}",
                    use_container_width=True
                )
                if deleted_clicked:
                    deleted_count = delete_supplement_log(log["id"])
                    st.success("Deleted one log.")
                    st.rerun()
        
            st.divider()