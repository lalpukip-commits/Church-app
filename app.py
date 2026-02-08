import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Shopkeeper's Fair-Share Treasury")
st.markdown("Priority: **Equal Distribution of Small Notes (10s & 20s) first.**")

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
        wants = st.number_input(f"500s to swap", 1, 10, 1, key=f"wants_{i}")
    
    total_requested_amt += (wants * 500)
    people_data.append({
        "name": name, 
        "wants": wants, 
        "fulfilled_count": 0, 
        "received_notes": {200:0, 100:0, 50:0, 20:0, 10:0}
    })

st.metric("Total Amount to be Exchanged", f"₹{total_requested_amt}")

# --- 3. The Equivalent Distribution Logic ---
if st.button("Calculate Fair Distribution", type="primary"):
    temp_inv = inv.copy()
    
    # Create individual 500rs 'slots' to fill
    slots = []
    for p_idx, p in enumerate(people_data):
        for _ in range(p["wants"]):
            slots.append({"p_idx": p_idx, "val": 0, "notes": {200:0, 100:0, 50:0, 20:0, 10:0}})

    # PHASE 1: Distribute 10s and 20s (Priority 1)
    for denom in [10, 20]:
        while temp_inv[denom] > 0:
            added = False
            for s in slots:
                if s["val"] + denom <= 500 and temp_inv[denom] > 0:
                    s["notes"][denom] += 1
                    s["val"] += denom
                    temp_inv[denom] -= 1
                    added = True
            if not added: break

    # PHASE 2: Distribute 50s (Priority 2)
    for denom in [50]:
        while temp_inv[denom] > 0:
            added = False
            for s in slots:
                if s["val"] + denom <= 500 and temp_inv[denom] > 0:
                    s["notes"][denom] += 1
                    s["val"] += denom
                    temp_inv[denom] -= 1
                    added = True
            if not added: break

    # PHASE 3: Top up with 100s and 200s (Last Option)
    for s in slots:
        for denom in [100, 200]:
            while s["val"] + denom <= 500 and temp_inv[denom] > 0:
                s["notes"][denom] += 1
                s["val"] += denom
                temp_inv[denom] -= 1

    # PHASE 4: Settlement
    for s in slots:
        p = people_data[s["p_idx"]]
        if s["val"] == 500:
            p["fulfilled_count"] += 1
            for d in [10, 20, 50, 100, 200]:
                p["received_notes"][d] += s["notes"][d]
        else:
            # If a slot didn't hit 500, return those specific notes to the plate
            for d, count in s["notes"].items():
                temp_inv[d] += count

    # --- 4. Results ---
    st.divider()
    st.subheader("Distribution Results")
    
    for p in people_data:
        with st.expander(f"👤 {p['name']} (Swapped {p['fulfilled_count']} of {p['wants']} notes)"):
            if p["fulfilled_count"] > 0:
                st.write(f"**Total Received:** ₹{p['fulfilled_count'] * 500}")
                # Grouped display of notes
                for d in [10, 20, 50, 100, 200]:
                    count = p["received_notes"][d]
                    if count > 0:
                        st.write(f"✅ **{d}rs:** {count} notes")
            else:
                st.error("No exchange possible for this person (Not enough change left).")

    remaining_val = sum(k*v for k,v in temp_inv.items())
    st.info(f"**Remaining in Plate:** ₹{remaining_val}")
