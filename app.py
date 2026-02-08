import streamlit as st
import random

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Shopkeeper's Fair-Share Treasury")
st.markdown("Rules: **Small notes first** → **Min. 1 per person** → **Deduct from highest volume users first.**")

# --- 1. Collection Inventory ---
with st.sidebar:
    st.header("1. Plate Inventory")
    n200 = st.number_input("200rs count", 0, value=5)
    n100 = st.number_input("100rs count", 0, value=10)
    n50 = st.number_input("50rs count", 0, value=20)
    n20 = st.number_input("20rs count", 0, value=50)
    n10 = st.number_input("10rs count", 0, value=100)
    
    inv = {200: n200, 100: n100, 50: n50, 20: n20, 10: n10}
    total_plate = sum(k * v for k, v in inv.items())
    st.metric("Total in Plate", f"₹{total_plate}")

# --- 2. Exchange Requests ---
st.header("2. Request List")
num_p = st.number_input("How many shopkeepers?", 1, 10, 3)

people_data = []
total_requested_amt = 0

for i in range(num_p):
    c1, c2 = st.columns([2, 1])
    with c1:
        name = st.text_input(f"Name", f"Shopkeeper {chr(65+i)}", key=f"name_{i}")
    with c2:
        wants = st.number_input(f"Number of 500s", 1, 10, 2, key=f"wants_{i}")
    
    total_requested_amt += (wants * 500)
    people_data.append({
        "name": name, 
        "wants": wants, 
        "fulfilled": 0, 
        "notes_received": {200:0, 100:0, 50:0, 20:0, 10:0},
        "returned_500s": 0
    })

st.metric("Total Amount to be Exchanged", f"₹{total_requested_amt}")

# --- 3. The Fair Distribution Logic ---
if st.button("Calculate Final Distribution", type="primary"):
    temp_inv = inv.copy()
    
    # Flatten all requests into individual 500rs slots
    slots = []
    for p_idx, p in enumerate(people_data):
        for _ in range(p["wants"]):
            slots.append({
                "p_idx": p_idx, 
                "val": 0, 
                "notes": {200:0, 100:0, 50:0, 20:0, 10:0}, 
                "success": False
            })

    # PHASE 1: Priority Distribution (10, 20 first, then 50)
    for denom in [10, 20, 50]:
        while temp_inv[denom] > 0:
            added = False
            for s in slots:
                if s["val"] + denom <= 500 and temp_inv[denom] > 0:
                    s["notes"][denom] += 1
                    s["val"] += denom
                    temp_inv[denom] -= 1
                    added = True
            if not added: break

    # PHASE 2: Fill remaining with 100/200
    for s in slots:
        for denom in [100, 200]:
            while s["val"] + denom <= 500 and temp_inv[denom] > 0:
                s["notes"][denom] += 1
                s["val"] += denom
                temp_inv[denom] -= 1
        if s["val"] == 500:
            s["success"] = True

    # PHASE 3: THE RE-BALANCER (Safety Clause)
    # Ensure everyone has at least one success
    for p_idx, p in enumerate(people_data):
        p_successes = [s for s in slots if s["p_idx"] == p_idx and s["success"]]
        
        if not p_successes:
            # Person has zero! Find a donor from people with > 1 success
            potential_donors = []
            for d_idx, d_p in enumerate(people_data):
                d_successes = [s for s in slots if s["p_idx"] == d_idx and s["success"]]
                if len(d_successes) > 1:
                    potential_donors.append((d_idx, len(d_successes)))
            
            if potential_donors:
                # Rule: Pick the one with the MOST. If same, random choice.
                max_val = max(d[1] for d in potential_donors)
                top_donors = [d for d in potential_donors if d[1] == max_val]
                chosen_donor_idx = random.choice(top_donors)[0]
                
                # Transfer the change
                donor_slot = next(s for s in slots if s["p_idx"] == chosen_donor_idx and s["success"])
                target_slot = next(s for s in slots if s["p_idx"] == p_idx) # The person with 0
                
                target_slot["notes"] = donor_slot["notes"].copy()
                target_slot["val"] = 500
                target_slot["success"] = True
                
                donor_slot["success"] = False
                donor_slot["val"] = 0
                donor_slot["notes"] = {200:0, 100:0, 50:0, 20:0, 10:0}

    # PHASE 4: Final Tally and Labeling Returns
    for s in slots:
        p = people_data[s["p_idx"]]
        if s["success"]:
            p["fulfilled"] += 1
            for d in [10, 20, 50, 100, 200]:
                p["notes_received"][d] += s["notes"][d]
        else:
            p["returned_500s"] += 1

    # --- 4. Results Display ---
    st.divider()
    st.subheader("Distribution Summary")
    
    for p in people_data:
        with st.expander(f"👤 {p['name']} (Result: {p['fulfilled']} / {p['wants']})"):
            if p["fulfilled"] > 0:
                st.success(f"Exchanged: ₹{p['fulfilled'] * 500}")
                for d in [10, 20, 50, 100, 200]:
                    if p["notes_received"][d] > 0:
                        st.write(f"**{d}rs:** {p['notes_received'][d]} notes")
            
            if p["returned_500s"] > 0:
                st.error(f"⚠️ {p['returned_500s']} x 500rs: **GIVEN BACK DUE TO LACK OF CHANGE**")

    remaining_val = sum(k*v for k,v in temp_inv.items())
    st.info(f"**Remaining in Plate:** ₹{remaining_val}")
