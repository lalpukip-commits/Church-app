import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")
st.title("⛪ Church Treasury")
st.markdown("Rules: **Small Notes Distributed First** + **Priority for Big Players**")

# --- 1. INVENTORY ---
with st.sidebar:
    st.header("1. Plate Inventory")
    inv = {
        200: st.number_input("200rs count", 0),
        100: st.number_input("100rs count", 0),
        50: st.number_input("50rs count", 0),
        20: st.number_input("20rs count", 0),
        10: st.number_input("10rs count", 0)
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
    shopkeepers.append({"name": name, "orig": notes_in, "got": 0, "change": {200:0, 100:0, 50:0, 20:0, 10:0}, "current_val": 0})

# --- 3. THE CALCULATION ---
if st.button("Distribute Change", type="primary"):
    temp_inv = inv.copy()
    
    # Sort: People with more 500s get served first
    active_list = sorted(shopkeepers, key=lambda x: x['orig'], reverse=True)
    
    # How many 500rs exchanges can we actually do?
    total_possible_exchanges = total_plate // 500
    
    # PHASE 1: ALLOCATE SLOTS
    # Assign who gets an exchange based on your "Big Players First" rule
    exchanges_to_do = []
    temp_count = total_possible_exchanges
    while temp_count > 0:
        found = False
        for s in active_list:
            if s['got'] < s['orig'] and temp_count > 0:
                s['got'] += 1
                exchanges_to_do.append(s)
                temp_count -= 1
                found = True
        if not found: break

    # PHASE 2: HARMONY DISTRIBUTION (Small Notes First)
    # We deal 10s, 20s, and 50s across all "active" 500rs slots
    for d in [10, 20, 50]:
        while temp_inv[d] > 0:
            added = False
            for s in exchanges_to_do:
                # Check if adding this note exceeds 500rs for this specific note exchange
                if s['current_val'] + d <= 500 and temp_inv[d] > 0:
                    s['change'][d] += 1
                    s['current_val'] += d
                    temp_inv[d] -= 1
                    added = True
            if not added: break

    # PHASE 3: FILL THE REST (With 100s and 200s)
    for s in exchanges_to_do:
        for d in [200, 100, 50, 20, 10]:
            while s['current_val'] + d <= 500 and temp_inv[d] > 0:
                s['change'][d] += 1
                s['current_val'] += d
                temp_inv[d] -= 1

    # PHASE 4: THE SWAP (Balancing 10s and 20s between people)
    for _ in range(5): 
        for s1 in shopkeepers:
            for s2 in shopkeepers:
                # Swap Rule: If s1 has 20s and s2 has 10s, trade to balance
                if s1['change'][20] > s2['change'][20] and s2['change'][10] >= 2:
                    s1['change'][20] -= 1
                    s1['change'][10] += 2
                    s2['change'][10] -= 2
                    s2['change'][20] += 1

    # --- 4. DISPLAY RESULTS ---
    st.divider()
    for s in shopkeepers:
        returned = s['orig'] - s['got']
        if s['orig'] > 0 and s['got'] == 0:
            st.error(f"❌ **{s['name']}**: NO MONEY. All {s['orig']} notes returned.")
        elif s['orig'] > 0:
            with st.expander(f"👤 {s['name']} (Exchanged: {s['got']} | Returned: {returned})"):
                if returned > 0:
                    st.warning(f"{returned} note(s) returned to you.")
                for d in [200, 100, 50, 20, 10]:
                    if s['change'][d] > 0:
                        st.write(f"**{d}rs:** {s['change'][d]} notes")

    leftover = sum(k * v for k, v in temp_inv.items())
    st.info(f"Remaining in Plate: ₹{leftover}")
