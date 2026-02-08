import streamlit as st
import random

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Church Treasury Logic")
st.info("Goal: Fair small notes first, then fill the rest with whatever is available.")

# --- 1. Inventory ---
with st.sidebar:
    st.header("1. Plate Inventory")
    n200 = st.number_input("200rs count", 0, value=0)
    n100 = st.number_input("100rs count", 0, value=0)
    n50 = st.number_input("50rs count", 0, value=0)
    n20 = st.number_input("20rs count", 0, value=0)
    n10 = st.number_input("10rs count", 0, value=0)
    
    inv = {200: n200, 100: n100, 50: n50, 20: n20, 10: n10}
    total_plate = sum(k * v for k, v in inv.items())
    st.metric("Total in Plate", f"₹{total_plate}")

# --- 2. Requests ---
st.header("2. Request List")
num_p = st.number_input("How many shopkeepers?", 1, 15, 1)

people_data = []
for i in range(num_p):
    c1, c2 = st.columns([2, 1])
    name = c1.text_input(f"Name", f"Shopkeeper {i+1}", key=f"n{i}")
    wants = c2.number_input(f"500s", 1, 10, 1, key=f"w{i}")
    people_data.append({"name": name, "wants": wants, "got": 0, "returned": 0, "notes": {200:0, 100:0, 50:0, 20:0, 10:0}})

# --- 3. The Logic ---
if st.button("Distribute Now", type="primary"):
    temp_inv = inv.copy()
    
    # PHASE 1: REJECTION (Take from those with most if short)
    current_req = sum(p["wants"] for p in people_data) * 500
    while current_req > total_plate:
        # Prioritize taking from those with > 1 note
        rich = [p for p in people_data if p["wants"] > 1]
        target = random.choice(rich) if rich else random.choice([p for p in people_data if p["wants"] > 0])
        target["wants"] -= 1
        target["returned"] += 1
        current_req -= 500

    # Create individual 500rs "buckets"
    buckets = []
    for p_idx, p in enumerate(people_data):
        for _ in range(p["wants"]):
            buckets.append({"p_idx": p_idx, "sum": 0, "notes": {200:0, 100:0, 50:0, 20:0, 10:0}})

    # PHASE 2: HARMONY DEAL (10s, 20s, 50s one by one)
    for d in [10, 20, 50]:
        while temp_inv[d] > 0:
            changed = False
            for b in buckets:
                if b["sum"] + d <= 500 and temp_inv[d] > 0:
                    b["notes"][d] += 1
                    b["sum"] += d
                    temp_inv[d] -= 1
                    changed = True
            if not changed: break

    # PHASE 3: AGGRESSIVE FILL (Finish the 500s with anything left)
    for b in buckets:
        for d in [200, 100, 50, 20, 10]:
            while b["sum"] + d <= 500 and temp_inv[d] > 0:
                b["notes"][d] += 1
                b["sum"] += d
                temp_inv[d] -= 1

    # PHASE 4: FINAL SETTLE
    for b in buckets:
        p = people_data[b["p_idx"]]
        if b["sum"] == 500:
            p["got"] += 1
            for d in [10, 20, 50, 100, 200]:
                p["notes"][d] += b["notes"][d]
        else:
            p["returned"] += 1 # Only if plate is truly empty

    # --- 4. DISPLAY ---
    st.divider()
    for p in people_data:
        if p["returned"] > 0:
            st.error(f"⚠️ **{p['name']}**: {p['returned']} note(s) given back (lack of change).")
        
        with st.expander(f"👤 {p['name']} (Exchanged: {p['got']})"):
            if p["got"] > 0:
                for d in [200, 100, 50, 20, 10]:
                    if p["notes"][d] > 0:
                        st.write(f"**{d}rs:** {p['notes'][d]} notes")
            else: st.write("No notes exchanged.")
