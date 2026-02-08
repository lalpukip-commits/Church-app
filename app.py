import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Church Treasury Logic")
st.markdown("Guaranteed Minimum Mode: Fulfills at least one 500rs per person before trying for more.")

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
for i in range(num_p):
    rc1, rc2 = st.columns(2)
    with rc1:
        name = st.text_input(f"Name {i+1}", f"Person {i+1}")
    with rc2:
        wants = st.number_input(f"500s for {name}", 1, 20, 1)
    people_data.append({"name": name, "wants": wants, "notes": {10:0, 20:0, 50:0, 100:0, 200:0}, "fulfilled": 0})

total_req_val = sum(p["wants"] for p in people_data) * 500
st.metric("Total amount Requested", f"{total_req_val}rs", delta=f"{total_plate - total_req_val}rs")

# --- 3. Distribution Logic ---
st.divider()
if st.button("Calculate Distribution", type="primary"):
    temp_inv = inv.copy()
    max_wants = max(p["wants"] for p in people_data)
    
    # We go round by round (Round 1: Everyone gets their 1st note, Round 2: Everyone gets their 2nd...)
    for r in range(max_wants):
        for p in people_data:
            if p["fulfilled"] < p["wants"]:
                # Attempt to build EXACTLY one 500rs exchange
                current_note_set = {10:0, 20:0, 50:0, 100:0, 200:0}
                needed = 500
                
                # Fill sequentially 10 -> 20 -> 50 -> 100 -> 200
                for denom in [10, 20, 50, 100, 200]:
                    while needed >= denom and temp_inv[denom] > 0:
                        temp_inv[denom] -= 1
                        current_note_set[denom] += 1
                        needed -= denom
                
                if needed == 0:
                    # Success: Give this note to the person
                    p["fulfilled"] += 1
                    for d in current_note_set:
                        p["notes"][d] += current_note_set[d]
                else:
                    # Fail: Return those specific notes to the plate for the next person
                    for d, count in current_note_set.items():
                        temp_inv[d] += count

    # --- 4. Final Display ---
    total_swapped = sum(p["fulfilled"] for p in people_data)
    st.success(f"Successfully fulfilled {total_swapped} total 500rs notes.")

    for p in people_data:
        with st.expander(f"💰 {p['name']} - Total: {p['fulfilled'] * 500}rs"):
            if p["fulfilled"] < p["wants"]:
                shortfall = p["wants"] - p["fulfilled"]
                st.error(f"RETURN SECTION: Give back {shortfall} of their 500rs notes (Not enough change).")
            
            if p["fulfilled"] > 0:
                for b in [200, 100, 50, 20, 10]:
                    if p["notes"][b] > 0:
                        st.write(f"**{b}rs notes:** {p['notes'][b]}")
            else:
                st.write("No exchange possible. Return all notes.")

    st.info(f"Remaining in Church Plate: {sum(k*v for k,v in temp_inv.items())}rs")
