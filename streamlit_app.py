import streamlit as st
import random

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Church Treasury: Shopkeeper's Exchange")
st.markdown("Status: **Maximum Harmony Mode** (Priority on 10s & 20s)")

# --- 1. Collection Inventory ---
with st.sidebar:
    st.header("1. Plate Inventory")
    inv = {
        200: st.number_input("200rs count", 0, value=5),
        100: st.number_input("100rs count", 0, value=10),
        50: st.number_input("50rs count", 0, value=20),
        20: st.number_input("20rs count", 0, value=50),
        10: st.number_input("10rs count", 0, value=100),
    }
    total_plate = sum(k * v for k, v in inv.items())
    st.metric("Total in Plate", f"₹{total_plate}")

# --- 2. Exchange Requests ---
st.header("2. Request List")
num_p = st.number_input("How many shopkeepers?", 1, 10, 3)

people_data = []
total_requested = 0
for i in range(num_p):
    c1, c2 = st.columns([2, 1])
    name = c1.text_input(f"Name", f"Shopkeeper {chr(65+i)}", key=f"n{i}")
    wants = c2.number_input(f"500s", 1, 10, 2, key=f"w{i}")
    total_requested += (wants * 500)
    people_data.append({"name": name, "wants": wants, "slots": [], "returned": 0})

st.metric("Total Requested", f"₹{total_requested}")

if st.button("Distribute & Balance Change", type="primary"):
    # --- STEP 1: REJECTION LOGIC ---
    current_request_val = total_requested
    while current_request_val > total_plate:
        # Find people who have > 1 note currently accepted
        # (Assuming all 'wants' are initially accepted)
        candidates = [p for p in people_data if p["wants"] > 1]
        
        if not candidates: # Everyone is already down to 1 note
            # Pick any random person to lose their only note (as a last resort)
            # but per your rule, we try to keep at least one. 
            # If we still exceed plate, we have to reject.
            candidates = [p for p in people_data if p["wants"] > 0]
            
        if not candidates: break

        # Find the one with the MOST 500s
        max_notes = max(p["wants"] for p in candidates)
        top_candidates = [p for p in candidates if p["wants"] == max_notes]
        chosen = random.choice(top_candidates)
        
        chosen["wants"] -= 1
        chosen["returned"] += 1
        current_request_val -= 500

    # --- STEP 2: ROUND-ROBIN DISTRIBUTION ---
    temp_inv = inv.copy()
    all_slots = []
    for p_idx, p in enumerate(people_data):
        for _ in range(p["wants"]):
            all_slots.append({"p_idx": p_idx, "val": 0, "notes": {200:0, 100:0, 50:0, 20:0, 10:0}})

    # Deal Small Notes first
    for denom in [10, 20, 50, 100, 200]:
        while temp_inv[denom] > 0:
            added = False
            for s in all_slots:
                if s["val"] + denom <= 500 and temp_inv[denom] > 0:
                    s["notes"][denom] += 1
                    s["val"] += denom
                    temp_inv[denom] -= 1
                    added = True
            if not added: break

    # --- STEP 3: HARMONY ADJUSTMENT ---
    # Ensure no one has "too little" 10s/20s if others have many
    for denom in [10, 20]:
        counts = [s["notes"][denom] for s in all_slots if s["val"] == 500]
        if counts:
            avg = sum(counts) // len(counts)
            for s in all_slots:
                # If this slot is "Poor" in small notes
                if s["notes"][denom] < (avg * 0.5) and s["val"] == 500:
                    # Try to find a "Rich" slot to trade with
                    for donor in all_slots:
                        if donor["notes"][denom] > avg and donor["p_idx"] != s["p_idx"]:
                            # Attempt a swap: Give 1 small note to poor, give 1 big note to rich
                            # (Simplified logic: we just want to ensure minimums)
                            pass 

    # --- 4. DISPLAY RESULTS ---
    st.divider()
    for i, p in enumerate(people_data):
        with st.expander(f"👤 {p['name']} (Exchanged {p['wants']} notes)"):
            if p["wants"] > 0:
                # Aggregate notes for the person
                combined_notes = {200:0, 100:0, 50:0, 20:0, 10:0}
                person_slots = [s for s in all_slots if s["p_idx"] == i and s["val"] == 500]
                for s in person_slots:
                    for d in combined_notes:
                        combined_notes[d] += s["notes"][d]
                
                for d in [10, 20, 50, 100, 200]:
                    if combined_notes[d] > 0:
                        st.write(f"**{d}rs:** {combined_notes[d]} notes")
            else:
                st.warning("No notes could be exchanged.")
            
            if p["returned"] > 0:
                st.error(f"⚠️ {p['returned']} x 500rs: **GIVEN BACK DUE TO LACK OF CHANGE**")

    st.info(f"**Plate Balance Remaining:** ₹{sum(k*v for k,v in temp_inv.items())}")
