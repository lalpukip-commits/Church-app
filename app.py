import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Church Treasury Logic")
st.markdown("Global Optimization: Smallest notes first, then total adjustment for maximum exchanges.")

# --- 1. Collection Inventory ---
st.header("1. Collection Inventory")
c1, c2 = st.columns(2)
with c1:
    n10 = st.number_input("10rs count", min_value=0, value=0)
    n20 = st.number_input("20rs count", min_value=0, value=0)
    n50 = st.number_input("50rs count", min_value=0, value=0)
with c2:
    n100 = st.number_input("100rs count", min_value=0, value=0)
    n200 = st.number_input("200rs count", min_value=0, value=0)

inv = {10: n10, 20: n20, 50: n50, 100: n100, 200: n200}
total_plate = sum(k * v for k, v in inv.items())
st.metric("Total amount in Plate", f"{total_plate}rs")

st.divider()

# --- 2. Exchange Requests ---
st.header("2. Exchange Requests")
num_p = st.number_input("How many people?", 1, 10, 1)

people_data = []
total_req_notes = 0
for i in range(num_p):
    rc1, rc2 = st.columns(2)
    with rc1:
        name = st.text_input(f"Name {i+1}", f"Person {i+1}")
    with rc2:
        wants = st.number_input(f"500s for {name}", 1, 20, 1)
    total_req_notes += wants
    people_data.append({"name": name, "wants": wants, "notes": {10:0, 20:0, 50:0, 100:0, 200:0}, "fulfilled": 0})

req_val = total_req_notes * 500
st.metric("Total amount Requested", f"{req_val}rs", delta=f"{total_plate - req_val}rs")

# --- 3. The Cascading & Optimization Logic ---
st.divider()
if st.button("Calculate Distribution", type="primary"):
    temp_inv = inv.copy()
    
    # Create individual 500rs "slots" for every single requested note
    all_slots = []
    for p_idx, p in enumerate(people_data):
        for _ in range(p["wants"]):
            all_slots.append({"owner_idx": p_idx, "val": 0, "notes": {10:0, 20:0, 50:0, 100:0, 200:0}})

    # STEP 1: Sequential Filling (10s, then 20s, 50s, 100s, 200s)
    # This spreads the small notes across all slots first
    for denom in [10, 20, 50, 100, 200]:
        for slot in all_slots:
            needed = 500 - slot["val"]
            if needed >= denom and temp_inv[denom] > 0:
                can_take = min(temp_inv[denom], needed // denom)
                slot["notes"][denom] += can_take
                slot["val"] += (can_take * denom)
                temp_inv[denom] -= can_take

    # STEP 2: The Global Adjustment (The "Left and Right" Shuffle)
    # If a slot is incomplete, try to use ANY remaining notes in the plate to finish it
    for slot in all_slots:
        if slot["val"] < 500:
            for denom in [200, 100, 50, 20, 10]:
                while (slot["val"] + denom <= 500) and temp_inv[denom] > 0:
                    slot["notes"][denom] += 1
                    slot["val"] += denom
                    temp_inv[denom] -= 1

    # STEP 3: Final Cleanup & Validation
    # We only count it as fulfilled if it hit exactly 500rs
    for slot in all_slots:
        if slot["val"] == 500:
            p_idx = slot["owner_idx"]
            people_data[p_idx]["fulfilled"] += 1
            for d in [10, 20, 50, 100, 200]:
                people_data[p_idx]["notes"][d] += slot["notes"][d]
        else:
            # Partial slot? Return everything to the plate to be used elsewhere or kept
            for d, count in slot["notes"].items():
                temp_inv[d] += count

    # --- 4. Final Result Display ---
    total_done = sum(p['fulfilled'] for p in people_data)
    st.success(f"Total 500rs notes exchanged: {total_done}")

    for p in people_data:
        with st.expander(f"💰 {p['name']} - Total: {p['fulfilled'] * 500}rs"):
            if p["fulfilled"] < p["wants"]:
                st.error(f"RETURN SECTION: Give back {p['wants'] - p['fulfilled']} of their 500rs notes.")
            
            if p["fulfilled"] > 0:
                # Show breakdown from largest to smallest for the user to count out
                for b in [200, 100, 50, 20, 10]:
                    if p["notes"][b] > 0:
                        st.write(f"**{b}rs notes:** {p['notes'][b]}")
            else:
                st.write("No exchange possible for this person. Please return their notes.")

    st.info(f"Remaining in Church Plate: {sum(k*v for k,v in temp_inv.items())}rs")
    
