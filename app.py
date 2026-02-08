import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Church Treasury Logic")
st.markdown("Fair Card-Dealer Mode: Notes are distributed one-by-one across all people.")

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

# --- 3. The "Card Dealer" Logic ---
st.divider()
if st.button("Calculate Distribution", type="primary"):
    temp_inv = inv.copy()
    
    # Create individual 500rs "slots"
    all_slots = []
    for p_idx, p in enumerate(people_data):
        for _ in range(p["wants"]):
            all_slots.append({"owner_idx": p_idx, "val": 0, "notes": {10:0, 20:0, 50:0, 100:0, 200:0}})

    # STAGE 1: The "Card Dealer" - Smallest notes first, one at a time per person
    for denom in [10, 20, 50, 100, 200]:
        notes_available = temp_inv[denom]
        while notes_available > 0:
            notes_given_this_round = 0
            for slot in all_slots:
                # If slot still needs money and can fit at least one more of this note
                if slot["val"] + denom <= 500 and notes_available > 0:
                    slot["notes"][denom] += 1
                    slot["val"] += denom
                    notes_available -= 1
                    notes_given_this_round += 1
            
            # If we went through every person and couldn't give out a single note, stop
            if notes_given_this_round == 0:
                break
        temp_inv[denom] = notes_available

    # STAGE 2: Global Finish - Use any note left in plate to finish incomplete slots
    for slot in all_slots:
        if slot["val"] < 500:
            for denom in [200, 100, 50, 20, 10]:
                while slot["val"] + denom <= 500 and temp_inv[denom] > 0:
                    slot["notes"][denom] += 1
                    slot["val"] += denom
                    temp_inv[denom] -= 1

    # STAGE 3: Cleanup - Only count full 500rs sets
    for slot in all_slots:
        if slot["val"] == 500:
            p_idx = slot["owner_idx"]
            people_data[p_idx]["fulfilled"] += 1
            for d in [10, 20, 50, 100, 200]:
                people_data[p_idx]["notes"][d] += slot["notes"][d]
        else:
            # If not exactly 500, put notes back in church plate
            for d, count in slot["notes"].items():
                temp_inv[d] += count

    # --- 4. Final Result Display ---
    st.success(f"Total 500rs notes exchanged: {sum(p['fulfilled'] for p in people_data)}")

    for p in people_data:
        with st.expander(f"💰 {p['name']} - Total: {p['fulfilled'] * 500}rs"):
            if p["fulfilled"] < p["wants"]:
                st.error(f"RETURN SECTION: Short by {p['wants'] - p['fulfilled']} notes. Give back their 500rs.")
            
            if p["fulfilled"] > 0:
                for b in [200, 100, 50, 20, 10]:
                    if p["notes"][b] > 0:
                        st.write(f"**{b}rs notes:** {p['notes'][b]}")
            else:
                st.write("No change available. Return all 500rs notes.")

    st.info(f"Remaining in Church Plate: {sum(k*v for k,v in temp_inv.items())}rs")
  
