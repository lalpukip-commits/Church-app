import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")
st.title("⛪ Church Treasury")
st.markdown("Strategy: **Smallest Notes First (10s → 20s → 50s → 100s → 200s)**")

# --- 1. INVENTORY ---
with st.sidebar:
    st.header("1. Plate Inventory")
    # Using the denominations in reverse order for the UI
    n10 = st.number_input("10rs count", 0)
    n20 = st.number_input("20rs count", 0)
    n50 = st.number_input("50rs count", 0)
    n100 = st.number_input("100rs count", 0)
    n200 = st.number_input("200rs count", 0)
    
    inv = {10: n10, 20: n20, 50: n50, 100: n100, 200: n200}
    total_plate = sum(k * v for k, v in inv.items())
    st.metric("Total in Plate", f"₹{total_plate}")

# --- 2. REQUESTS ---
st.header("2. Shopkeeper Requests")
num_p = st.number_input("Number of Shopkeepers", 1, 15, 3)

shopkeepers = []
for i in range(num_p):
    c1, c2 = st.columns([2, 1])
    name = c1.text_input(f"Name", f"Person {chr(65+i)}", key=f"n{i}")
    notes_in = c2.number_input(f"500s brought", 0, key=f"w{i}")
    shopkeepers.append({
        "name": name, 
        "orig": notes_in, 
        "accepted": 0, 
        "change": {10:0, 20:0, 50:0, 100:0, 200:0},
        "current_val": 0
    })

# --- 3. THE CALCULATION ---
if st.button("Distribute Small-to-Large", type="primary"):
    temp_inv = inv.copy()
    
    # Sort: Big Players (those who brought more 500s) get priority for the exchange slots
    active_list = sorted(shopkeepers, key=lambda x: x['orig'], reverse=True)
    
    # Determine how many 500rs units we can actually fulfill
    total_possible = total_plate // 500
    
    # Create the "Exchanges" list based on Priority
    exchange_slots = []
    temp_total = total_possible
    while temp_total > 0:
        added = False
        for s in active_list:
            if s['accepted'] < s['orig'] and temp_total > 0:
                s['accepted'] += 1
                # Each slot is one 500rs unit
                exchange_slots.append(s)
                temp_total -= 1
                added = True
        if not added: break

    # PHASE 1: THE SMALL-FIRST DISTRIBUTION
    # We loop through denominations from 10 up to 200
    for d in [10, 20, 50, 100, 200]:
        # Keep dealing this specific note as long as we have them
        while temp_inv[d] > 0:
            notes_dealt_this_round = False
            for s in exchange_slots:
                # Only give note if it doesn't push the individual 500rs unit over 500
                # AND if the person's TOTAL change for all their 500s isn't already "full"
                if s['current_val'] + d <= (s['accepted'] * 500) and temp_inv[d] > 0:
                    s['change'][d] += 1
                    s['current_val'] += d
                    temp_inv[d] -= 1
                    notes_dealt_this_round = True
            
            # If we went through everyone and couldn't give out a single note of this type, move to next denomination
            if not notes_dealt_this_round:
                break

    # --- 4. DISPLAY RESULTS ---
    st.divider()
    st.subheader("Final Balanced Distribution")

    for s in shopkeepers:
        returned = s['orig'] - s['accepted']
        
        if s['orig'] > 0:
            with st.expander(f"👤 {s['name']} (Exchanged: {s['accepted']} | Returned: {returned})"):
                if s['accepted'] == 0:
                    st.error("Could not fulfill exchange - Lack of change in plate.")
                else:
                    if returned > 0:
                        st.warning(f"{returned} note(s) of 500rs returned to shopkeeper.")
                    
                    # Display notes from Smallest to Largest
                    for d in [10, 20, 50, 100, 200]:
                        if s['change'][d] > 0:
                            st.write(f"**₹{d}:** {s['change'][d]} notes")
                    st.write(f"---")
                    st.write(f"**Total Received:** ₹{s['current_val']}")

    st.info(f"**Leftover in Plate:** ₹{sum(k*v for k,v in temp_inv.items())}")
