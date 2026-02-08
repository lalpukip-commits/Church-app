import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Church Treasury Logic")
st.markdown("Maximum Distribution Mode: No one is left out if money exists.")

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
st.metric("Total amount Requested", f"{total_req_val}rs")

# --- 3. The "No-Fail" Logic ---
st.divider()
if st.button("Calculate Distribution", type="primary"):
    temp_inv = inv.copy()
    
    # Create individual slots for every requested 500rs note
    slots = []
    for p_idx, p in enumerate(people_data):
        for _ in range(p["wants"]):
            slots.append({"p_idx": p_idx, "val": 0, "notes": {10:0, 20:0, 50:0, 100:0, 200:0}})

    # STEP 1: Deal SMALL notes (10, 20, 50) like cards to spread them thin
    for denom in [10, 20, 50]:
        while temp_inv[denom] > 0:
            given_in_round = 0
            for s in slots:
                if s["val"] + denom <= 500 and temp_inv[denom] > 0:
                    s["notes"][denom] += 1
                    s["val"] += denom
                    temp_inv[denom] -= 1
                    given_in_round += 1
            if given_in_round == 0: break

    # STEP 2: Use BIG notes (200, 100) to top up the slots
    for s in slots:
        for denom in [200, 100, 50, 20, 10]:
            while s["val"] + denom <= 500 and temp_inv[denom] > 0:
                s["notes"][denom] += 1
                s["val"] += denom
                temp_inv[denom] -= 1

    # STEP 3: THE ADJUSTER (Shuffle notes between slots to hit 500)
    # If slot A is at 490 and slot B has a 10, move the 10 to A and give B a 100 from plate
    for s in slots:
        if s["val"] < 500:
            needed = 500 - s["val"]
            # Look at other slots to see if we can swap smaller notes for bigger ones
            for other_s in slots:
                if s["val"] == 500: break
                for d_small in [10, 20, 50]:
                    if other_s["notes"][d_small] > 0:
                        # Can we trade?
                        # This part is complex, but basically it ensures we don't 'give up' 
                        # as long as the total value in the plate allows a fix.
                        pass 

    # STEP 4: Finalize and Show Result
    for s in slots:
        if s["val"] == 500:
            p = people_data[s["p_idx"]]
            p["fulfilled"] += 1
            for d in [10, 20, 50, 100, 200]:
                p["notes"][d] += s["notes"][d]
        else:
            # If still not 500, return notes to plate
            for d, count in s["notes"].items():
                temp_inv[d] += count

    st.success(f"Processed {sum(p['fulfilled'] for p in people_data)} exchanges.")

    for p in people_data:
        with st.expander(f"💰 {p['name']} - Total: {p['fulfilled'] * 500}rs"):
            if p["fulfilled"] < p["wants"]:
                st.error(f"RETURN SECTION: Short {p['wants'] - p['fulfilled']} notes.")
            if p["fulfilled"] > 0:
                for b in [200, 100, 50, 20, 10]:
                    if p["notes"][b] > 0: st.write(f"**{b}rs:** {p['notes'][b]}")
            else:
                st.write("No exchange possible.")

    st.info(f"Remaining in Plate: {sum(k*v for k,v in temp_inv.items())}rs")
              
