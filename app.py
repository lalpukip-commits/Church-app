import streamlit as st
import pandas as pd

st.set_page_config(page_title="Church Treasury", page_icon="⛪", layout="wide")

st.title("⛪ Church Treasury Optimizer")
st.markdown("> **Fair Distribution Mode:** Small denominations are distributed evenly across all requests to ensure the most people get change.")

# --- 1. Collection Inventory ---
with st.sidebar:
    st.header("1. Plate Inventory")
    inv = {
        200: st.number_input("200rs count", 0, value=10),
        100: st.number_input("100rs count", 0, value=10),
        50: st.number_input("50rs count", 0, value=10),
        20: st.number_input("20rs count", 0, value=20),
        10: st.number_input("10rs count", 0, value=50),
    }
    total_plate = sum(k * v for k, v in inv.items())
    st.metric("Total in Plate", f"₹{total_plate}")

# --- 2. Exchange Requests ---
st.header("2. Exchange Requests")
num_p = st.number_input("Number of people requesting change:", 1, 20, 3)

people_data = []
cols = st.columns(3)
for i in range(num_p):
    with cols[i % 3]:
        st.subheader(f"Person {i+1}")
        name = st.text_input(f"Name", f"Member {i+1}", key=f"n_{i}")
        wants = st.number_input(f"Number of 500s to swap", 1, 10, 1, key=f"w_{i}")
        people_data.append({
            "name": name, 
            "wants": wants, 
            "notes": {200:0, 100:0, 50:0, 20:0, 10:0}, 
            "fulfilled": 0
        })

# --- 3. Optimized Distribution Logic ---
if st.button("Distribute Change", type="primary", use_container_width=True):
    temp_inv = inv.copy()
    
    # Flatten requests into individual 500rs "slots"
    slots = []
    for p_idx, p in enumerate(people_data):
        for _ in range(p["wants"]):
            slots.append({"p_idx": p_idx, "val": 0, "notes": {200:0, 100:0, 50:0, 20:0, 10:0}})

    # PHASE 1: Fair Distribution of small/scarce notes (10, 20, 50)
    # We deal these round-robin style
    for denom in [50, 20, 10]:
        while temp_inv[denom] > 0:
            added_this_round = False
            for s in slots:
                if s["val"] + denom <= 500 and temp_inv[denom] > 0:
                    s["notes"][denom] += 1
                    s["val"] += denom
                    temp_inv[denom] -= 1
                    added_this_round = True
            if not added_this_round: break

    # PHASE 2: Efficient Topping (200, 100)
    # Use larger notes to complete the 500rs requirement for as many slots as possible
    for s in slots:
        for denom in [200, 100, 50, 20, 10]:
            while s["val"] + denom <= 500 and temp_inv[denom] > 0:
                s["notes"][denom] += 1
                s["val"] += denom
                temp_inv[denom] -= 1

    # PHASE 3: Settlement
    # Only finalize slots that reached exactly 500. Return others to plate.
    for s in slots:
        p = people_data[s["p_idx"]]
        if s["val"] == 500:
            p["fulfilled"] += 1
            for d in p["notes"]:
                p["notes"][d] += s["notes"][d]
        else:
            # Partial fills are invalid for a 500rs swap, return to inventory
            for d, count in s["notes"].items():
                temp_inv[d] += count

    # --- 4. Results Display ---
    st.divider()
    
    # Summary Table
    results = []
    for p in people_data:
        results.append({
            "Name": p["name"],
            "Requested": p["wants"],
            "Fulfilled": p["fulfilled"],
            "Status": "✅ Full" if p["fulfilled"] == p["wants"] else "⚠️ Partial" if p["fulfilled"] > 0 else "❌ Failed"
        })
    
    st.dataframe(pd.DataFrame(results), use_container_width=True)

    # Detailed Breakdown
    st.subheader("Detailed Breakdown")
    for p in people_data:
        if p["fulfilled"] > 0:
            with st.expander(f"💰 {p['name']} - Received ₹{p['fulfilled']*500}"):
                c = st.columns(5)
                for idx, (denom, count) in enumerate(p["notes"].items()):
                    if count > 0:
                        c[idx % 5].metric(f"{denom}rs", f"x{count}")
        elif p["wants"] > 0:
            st.warning(f"Could not fulfill any requests for {p['name']}.")

    st.info(f"**Plate Balance Remaining:** ₹{sum(k*v for k,v in temp_inv.items())}")
