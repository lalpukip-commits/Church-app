import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")
st.title("⛪ Church Treasury")
st.markdown("Strategy: **Round-Robin Harmony** (Dealing notes like cards)")

# --- 1. PLATE INVENTORY ---
with st.sidebar:
    st.header("1. Plate Inventory")
    n200 = st.number_input("200rs count", 0, value=0)
    n100 = st.number_input("100rs count", 0, value=0)
    n50 = st.number_input("50rs count", 0, value=0)
    n20 = st.number_input("20rs count", 0, value=0)
    n10 = st.number_input("10rs count", 0, value=0)
    
    inv = {200: n200, 100: n100, 50: n50, 20: n20, 10: n10}
    total_plate = sum(k * v for k, v in inv.items())
    st.metric("Total Money", f"₹{total_plate}")

# --- 2. REQUESTS ---
st.header("2. Shopkeeper Requests")
num_p = st.number_input("How many people?", 1, 10, 3)

shopkeepers = []
for i in range(num_p):
    c1, c2 = st.columns([2, 1])
    name = c1.text_input(f"Name", f"Person {chr(65+i)}", key=f"n{i}")
    wants = c2.number_input(f"500s", 0, key=f"w{i}")
    shopkeepers.append({"name": name, "wants": wants, "got": 0, "change": {200:0, 100:0, 50:0, 20:0, 10:0}, "current_val": 0})

# --- 3. THE LOGIC ---
if st.button("Distribute Harmoniously", type="primary"):
    temp_inv = inv.copy()
    
    # 1. Determine how many 500rs units we can actually fulfill
    possible = total_plate // 500
    requested = sum(s['wants'] for s in shopkeepers)
    to_fulfill = min(possible, requested)
    
    # 2. Create the "Slots" (Big Players get slots first)
    slots = []
    active_s = sorted(shopkeepers, key=lambda x: x['wants'], reverse=True)
    count = 0
    while count < to_fulfill:
        for s in active_s:
            if s['got'] < s['wants'] and count < to_fulfill:
                slots.append(s)
                s['got'] += 1
                count += 1
    
    # 3. HARMONY DEAL (10s, 20s, 50s) - Give one to each slot in a loop
    for d in [10, 20, 50]:
        while temp_inv[d] > 0:
            added_in_round = False
            for s in slots:
                if s['current_val'] + d <= 500 and temp_inv[d] > 0:
                    s['change'][d] += 1
                    s['current_val'] += d
                    temp_inv[d] -= 1
                    added_in_round = True
            if not added_in_round: break

    # 4. TOP UP (Fill remaining balance with 100s and 200s)
    for s in slots:
        for d in [200, 100, 50, 20, 10]:
            while s['current_val'] + d <= 500 and temp_inv[d] > 0:
                s['change'][d] += 1
                s['current_val'] += d
                temp_inv[d] -= 1

    # --- 4. DISPLAY ---
    st.divider()
    for s in shopkeepers:
        returned = s['wants'] - s['got']
        with st.expander(f"👤 {s['name']} (Exchanged: {s['got']} | Returned: {returned})"):
            if s['got'] > 0:
                for d in [200, 100, 50, 20, 10]:
                    if s['change'][d] > 0:
                        st.write(f"**{d}rs:** {s['change'][d]} notes")
            else:
                st.write("No exchange made.")

    st.info(f"Remaining in Plate: ₹{sum(k*v for k,v in temp_inv.items())}")
