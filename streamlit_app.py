import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")
st.title("⛪ Church Treasury")
st.markdown("Rules: **Big Players First** + **The Harmony Swap**")

# --- 1. INVENTORY (Starts at 0) ---
with st.sidebar:
    st.header("1. Plate Inventory")
    inv = {
        200: st.number_input("200rs notes", 0),
        100: st.number_input("100rs notes", 0),
        50: st.number_input("50rs notes", 0),
        20: st.number_input("20rs notes", 0),
        10: st.number_input("10rs notes", 0)
    }
    total_plate = sum(k * v for k, v in inv.items())
    st.metric("Total Money", f"₹{total_plate}")

# --- 2. REQUESTS ---
st.header("2. Shopkeeper Requests")
num_p = st.number_input("Number of Shopkeepers", 1, 15, 1)

shopkeepers = []
for i in range(num_p):
    c1, c2 = st.columns([2, 1])
    name = c1.text_input(f"Name", f"Person {i+1}", key=f"n{i}")
    notes_in = c2.number_input(f"500s brought", 0, key=f"w{i}")
    shopkeepers.append({"name": name, "orig": notes_in, "got": 0, "change": {200:0, 100:0, 50:0, 20:0, 10:0}})

# --- 3. THE CALCULATION ---
if st.button("Distribute Change", type="primary"):
    temp_inv = inv.copy()
    current_plate = total_plate
    
    # Sort by who brought the most notes (Big Players First)
    active_list = sorted(shopkeepers, key=lambda x: x['orig'], reverse=True)

    # PHASE 1: DISTRIBUTION (One 500 at a time)
    # We keep looping as long as we have 500rs in change
    while current_plate >= 500:
        found_someone = False
        for s in active_list:
            if s['got'] < s['orig'] and current_plate >= 500:
                # Give 1 unit of 500rs
                s['got'] += 1
                current_plate -= 500
                found_someone = True
                
                # Fill the 500rs using largest notes first for now
                rem = 500
                for d in [200, 100, 50, 20, 10]:
                    while rem >= d and temp_inv[d] > 0:
                        s['change'][d] += 1
                        temp_inv[d] -= 1
                        rem -= d
        if not found_someone: break

    # PHASE 2: THE HARMONY SWAP (Mixing 10s and 20s)
    # We look for people who have 20s and others who have 10s and swap them
    for _ in range(10): # Run a few swap cycles
        for s1 in active_list:
            for s2 in active_list:
                # If s1 has 20s and s2 has 10s... swap 1x20 for 2x10
                if s1['change'][20] >= 1 and s2['change'][10] >= 2:
                    s1['change'][20] -= 1
                    s1['change'][10] += 2
                    s2['change'][10] -= 2
                    s2['change'][20] += 1

    # --- 4. DISPLAY RESULTS ---
    st.divider()
    for s in shopkeepers:
        returned = s['orig'] - s['got']
        
        if s['got'] == 0:
            st.error(f"❌ **{s['name']}**: NO MONEY AVAILABLE. Returned all {s['orig']} notes.")
        else:
            with st.expander(f"👤 {s['name']} (Exchanged: {s['got']} | Returned: {returned})"):
                if returned > 0:
                    st.warning(f"Note: {returned} note(s) given back due to lack of change.")
                for d in [200, 100, 50, 20, 10]:
                    if s['change'][d] > 0:
                        st.write(f"**{d}rs:** {s['change'][d]} notes")

    st.info(f"Remaining in Plate: ₹{current_plate}")
