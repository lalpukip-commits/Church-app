import streamlit as st
import pandas as pd

# Set Page Config for Mobile
st.set_page_config(page_title="Church Treasury", page_icon="⛪", layout="centered")

def attempt_distribution(n_slots, original_inv):
    if n_slots == 0: return [], original_inv
    inv = original_inv.copy()
    slots = [{"total": 0, "notes": {10:0, 20:0, 50:0, 100:0, 200:0}} for _ in range(n_slots)]
    for d in [10, 20, 50]:
        per_slot = inv[d] // n_slots
        if per_slot > 0:
            for s in slots:
                s["notes"][d] += per_slot
                s["total"] += (per_slot * d)
            inv[d] -= (per_slot * n_slots)
    for i in range(n_slots):
        needed = 500 - slots[i]["total"]
        for d in [200, 100, 50, 20, 10]:
            while needed >= d and inv[d] > 0:
                slots[i]["notes"][d] += 1
                slots[i]["total"] += d
                inv[d] -= 1
                needed -= d
        if needed > 0: return None, original_inv
    return slots, inv

# --- UI Header ---
st.title("⛪ Church Treasury Logic")
st.markdown("Automated distribution for 500rs exchanges.")

# --- Sidebar: Inventory (X) ---
with st.sidebar:
    st.header("Collection Inventory")
    inv = {
        10: st.number_input("10rs Count", 0, value=92),
        20: st.number_input("20rs Count", 0, value=68),
        50: st.number_input("50rs Count", 0, value=50),
        100: st.number_input("100rs Count", 0, value=10),
        200: st.number_input("200rs Count", 0, value=2)
    }
    total_x = sum(k * v for k, v in inv.items())
    st.metric("Total in Plate", f"{total_x}rs")

# --- Main: Requests (P) ---
st.subheader("Exchange Requests")
num_p = st.number_input("Number of People", 1, 10, 3)
people_data = []
cols = st.columns(num_p)

for i in range(num_p):
    with cols[i]:
        name = st.text_input(f"Name {i+1}", f"Person {chr(65+i)}")
        wants = st.number_input(f"500s for {name}", 0, 20, 4)
        people_data.append({"name": name, "wants": wants})

# --- Run Logic ---
if st.button("Calculate Distribution", type="primary"):
    theoretical_max = total_x // 500
    viable_slots, final_rem_inv, final_n = None, None, 0

    for n in range(theoretical_max, -1, -1):
        slots, rem_inv = attempt_distribution(n, inv)
        if slots is not None:
            viable_slots, final_rem_inv, final_n = slots, rem_inv, n
            break

    # Round Robin Allocation
    curr_reqs = {p["name"]: p["wants"] for p in people_data}
    while sum(curr_reqs.values()) > final_n:
        highest = max(curr_reqs, key=curr_reqs.get)
        curr_reqs[highest] -= 1

    # Display Results
    st.divider()
    slot_idx = 0
    for p in people_data:
        appr = curr_reqs[p["name"]]
        p_notes = {10:0, 20:0, 50:0, 100:0, 200:0}
        for _ in range(appr):
            for d, c in viable_slots[slot_idx]["notes"].items(): p_notes[d] += c
            slot_idx += 1
        
        with st.expander(f"💰 {p['name']} - {appr * 500}rs"):
            st.write(f"**Status:** {appr} of {p['wants']} notes fulfilled.")
            st.write(f"**Take back:** {p['wants'] - appr} x 500rs notes.")
            st.table(pd.DataFrame([p_notes], index=["Counts"]))

    st.success(f"Church Remainder: {sum(k*v for k,v in final_rem_inv.items())}rs")
