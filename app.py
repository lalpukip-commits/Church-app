import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Church Treasury Logic")
st.markdown("Automated distribution for 500rs exchanges.")

# --- 1. Collection Inventory (Now on the main screen) ---
st.header("Collection Inventory")
st.info("Enter the number of notes collected from the plate:")

# All values are now set to 0 by default
inv = {
    10: st.number_input("10rs Count", min_value=0, value=0),
    20: st.number_input("20rs Count", min_value=0, value=0),
    50: st.number_input("50rs Count", min_value=0, value=0),
    100: st.number_input("100rs Count", min_value=0, value=0),
    200: st.number_input("200rs Count", min_value=0, value=0)
}

total_x = sum(k * v for k, v in inv.items())
st.metric("Total in Plate", f"{total_x}rs")

# --- 2. Exchange Requests ---
st.divider()
st.subheader("Exchange Requests")
num_p = st.number_input("Number of People requesting 500rs exchange", 1, 10, 1)

people_data = []
for i in range(num_p):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(f"Name {i+1}", f"Person {i+1}")
    with col2:
        wants = st.number_input(f"Notes for {name}", 1, 10, 1)
    people_data.append({"name": name, "wants": wants})

# --- 3. Calculation Logic ---
def attempt_distribution(n_slots, original_inv):
    if n_slots == 0: return [], original_inv
    inv_copy = original_inv.copy()
    slots = [{"total": 0, "notes": {10:0, 20:0, 50:0, 100:0, 200:0}} for _ in range(n_slots)]
    
    # Fill with 10s, 20s, 50s first for fairness
    for d in [10, 20, 50]:
        per_slot = inv_copy[d] // n_slots
        if per_slot > 0:
            for s in slots:
                s["notes"][d] += per_slot
                s["total"] += (per_slot * d)
            inv_copy[d] -= (per_slot * n_slots)
            
    # Top up to 500 using whatever is left
    for i in range(n_slots):
        needed = 500 - slots[i]["total"]
        for d in [200, 100, 50, 20, 10]:
            while needed >= d and inv_copy[d] > 0:
                slots[i]["notes"][d] += 1
                slots[i]["total"] += d
                inv_copy[d] -= 1
                needed -= d
        if needed > 0: return None, original_inv
    return slots, inv_copy

if st.button("Calculate Distribution", type="primary"):
    theoretical_max = total_x // 500
    viable_slots, final_rem_inv, final_n = None, None, 0

    for n in range(theoretical_max, -1, -1):
        slots, rem_inv = attempt_distribution(n, inv)
        if slots is not None:
            viable_slots, final_rem_inv, final_n = slots, rem_inv, n
            break

    # Show Results
    st.divider()
    if final_n == 0:
        st.error("Not enough notes to make a full 500rs exchange!")
    else:
        st.success(f"Successfully distributed {final_n} exchange(s)!")
        # Simple display of result
        st.write("Check the details below:")
        # (Logic to display each person's specific notes follows same pattern as before)
