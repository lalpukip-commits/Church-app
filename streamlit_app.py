import streamlit as st
import random

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Church Treasury Logic")
st.markdown("Maximum Harmony: Everyone gets a fair mix of small notes.")

# --- 1. Collection Inventory (All Presets Removed) ---
with st.sidebar:
    st.header("1. Plate Inventory")
    n200 = st.number_input("200rs count", min_value=0, value=0)
    n100 = st.number_input("100rs count", min_value=0, value=0)
    n50 = st.number_input("50rs count", min_value=0, value=0)
    n20 = st.number_input("20rs count", min_value=0, value=0)
    n10 = st.number_input("10rs count", min_value=0, value=0)
    
    inv = {200: n200, 100: n100, 50: n50, 20: n20, 10: n10}
    total_plate = sum(k * v for k, v in inv.items())
    st.metric("Total in Plate", f"₹{total_plate}")

# --- 2. Exchange Requests ---
st.header("2. Request List")
num_p = st.number_input("How many shopkeepers?", 1, 15, 1)

people_data = []
total_requested = 0
for i in range(num_p):
    c1, c2 = st.columns([2, 1])
    name = c1.text_input(f"Name", f"Shopkeeper {i+1}", key=f"n{i}")
    wants = c2.number_input(f"Number of 500s", 1, 10, 1, key=f"w{i}")
    total_requested += (wants * 500)
    people_data.append({
        "name": name, 
        "current_wants": wants, 
        "returned": 0,
        "notes_received": {200:0, 100:0, 50:0, 20:0, 10:0}
    })

st.metric("Total Requested", f"₹{total_requested}")

# --- 3. The Logic Engine ---
if st.button("Calculate Final Distribution", type="primary"):
    
    # PHASE A: REDUCTION (If plate is short)
    current_val = sum(p["current_wants"] for p in people_data) * 500
    while current_val > total_plate:
        # Take from those with > 1 note first
        candidates = [p for p in people_data if p["current_wants"] > 1]
        if not candidates:
            candidates = [p for p in people_data if p["current_wants"] > 0]
        if not candidates: break

        # Target the one with the MOST 500s
        max_val = max(p["current_wants"] for p in candidates)
        top_tier = [p for p in candidates if p["current_wants"] == max_val]
        chosen = random.choice(top_tier)
        
        chosen["current_wants"] -= 1
        chosen["returned"] += 1
        current_val -= 500

    # PHASE B: ROUND ROBIN DEALING (Harmony)
    temp_inv = inv.copy()
    slots = []
    for p_idx, p in enumerate(people_data):
        for _ in range(p["current_wants"]):
            slots.append({"p_idx": p_idx, "val": 0, "notes": {200:0, 100:0, 50:0, 20:0, 10:0}})

    # Priority: 10s, then 20s, then 50s
    for denom in [10, 20, 50, 100, 200]:
        while temp_inv[denom] > 0:
            added_any = False
            for s in slots:
                if s["val"] + denom <= 500 and temp_inv[denom] > 0:
                    s["notes"][denom] += 1
                    s["val"] += denom
                    temp_inv[denom] -= 1
                    added_any = True
            if not added_any: break

    # PHASE C: FINAL TALLY & CLEANUP
    for s in slots:
        p = people_data[s["p_idx"]]
        if s["val"] == 500:
            for d in [10, 20, 50, 100, 200]:
                p["notes_received"][d] += s["notes"][d]
        else:
            # Revert incomplete 500s
            p["current_wants"] -= 1
            p["returned"] += 1
            for d, count in s["notes"].items():
                temp_inv[d] += count

    # --- 4. DISPLAY RESULTS ---
    st.divider()
    
    st.subheader("⚠️ Status")
    returns_found = False
    for p in people_data:
        if p["returned"] > 0:
            st.error(f"**{p['name']}**: {p['returned']} note(s) given back due to lack of change.")
            returns_found = True
    if not returns_found:
        st.success("All exchanges fulfilled.")

    st.subheader("💰 Individual Breakdown")
    for p in people_data:
        with st.expander(f"👤 {p['name']} (Successfully Exchanged: {p['current_wants']})"):
            if p["current_wants"] > 0:
                for d in [10, 20, 50, 100, 200]:
                    if p["notes_received"][d] > 0:
                        st.write(f"**{d}rs:** {p['notes_received'][d]} notes")
            else:
                st.write("No exchange possible.")

    st.info(f"**Plate Remaining:** ₹{sum(k*v for k,v in temp_inv.items())}")
