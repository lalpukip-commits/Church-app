import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Church Treasury Logic")
st.markdown("Fair Distribution: Small notes are shared first, then big notes fill the gap.")

# --- 1. Collection Inventory ---
st.header("1. Collection Inventory")
n10 = st.number_input("10rs count", min_value=0, value=0)
n20 = st.number_input("20rs count", min_value=0, value=0)
n50 = st.number_input("50rs count", min_value=0, value=0)
n100 = st.number_input("100rs count", min_value=0, value=0)
n200 = st.number_input("200rs count", min_value=0, value=0)

inv = {10: n10, 20: n20, 50: n50, 100: n100, 200: n200}
total_plate = sum(k * v for k, v in inv.items())
st.metric("Total in Plate", f"{total_plate}rs")

# --- 2. Exchange Requests ---
st.divider()
st.header("2. Exchange Requests")
num_p = st.number_input("How many people?", 1, 10, 1)

people_data = []
for i in range(num_p):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input(f"Name {i+1}", f"Person {i+1}")
    with c2:
        wants = st.number_input(f"500s for {name}", 1, 20, 1)
    people_data.append({"name": name, "wants": wants, "notes": {10:0, 20:0, 50:0, 100:0, 200:0}, "current_val": 0, "fulfilled": 0})

# --- 3. Fair Distribution Logic ---
if st.button("Calculate Distribution", type="primary"):
    temp_inv = inv.copy()
    total_requested_slots = sum(p["wants"] for p in people_data)
    
    if total_requested_slots == 0:
        st.warning("Please enter the number of 500rs notes requested.")
    else:
        # STEP 1: Distribute small notes (10, 20, 50) FAIRLY across ALL requested 500rs slots
        for bill in [10, 20, 50]:
            per_slot = temp_inv[bill] // total_requested_slots
            if per_slot > 0:
                for person in people_data:
                    allocated = per_slot * person["wants"]
                    person["notes"][bill] += allocated
                    person["current_val"] += (allocated * bill)
                    temp_inv[bill] -= allocated

        # STEP 2: Finish each 500rs slot one by one using GREEDY method (Big notes first to fill gaps)
        for person in people_data:
            for _ in range(person["wants"]):
                # Calculate what is still needed to reach the next 500rs for this specific person
                target = (person["fulfilled"] + 1) * 500
                needed = target - person["current_val"]
                
                if needed <= 0: # Already met by small notes
                    person["fulfilled"] += 1
                    continue

                # Try to fill the 'needed' amount using remaining inventory
                # We check big notes first now to fill the large gaps left after the small note distribution
                for bill in [200, 100, 50, 20, 10]:
                    while needed >= bill and temp_inv[bill] > 0:
                        temp_inv[bill] -= 1
                        person["notes"][bill] += 1
                        person["current_val"] += bill
                        needed -= bill
                
                if needed == 0:
                    person["fulfilled"] += 1
                else:
                    # Cannot complete this 500rs note
                    break

        # --- 4. Display Results ---
        st.divider()
        total_done = sum(p["fulfilled"] for p in people_data)
        st.success(f"Total 500rs Exchanges Completed: {total_done}")

        for p in people_data:
            with st.expander(f"💰 {p['name']} - Received {p['fulfilled'] * 500}rs"):
                if p['fulfilled'] < p['wants']:
                    st.warning(f"Could only fulfill {p['fulfilled']} of {p['wants']} requested.")
                
                for bill in [200, 100, 50, 20, 10]:
                    if p['notes'][bill] > 0:
                        st.write(f"**{bill}rs notes:** {p['notes'][bill]}")

        rem_total = sum(k * v for k, v in temp_inv.items())
        st.info(f"Remaining in Church Plate: {rem_total}rs")
              
