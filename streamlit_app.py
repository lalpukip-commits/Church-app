import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")
st.title("⛪ Church Treasury: Clean Reversion Mode")
st.info("Strategy: Small-to-Large + Round Down to Nearest ₹500")

# --- 1. INVENTORY INPUT ---
with st.sidebar:
    st.header("1. Plate Inventory")
    n10 = st.number_input("10rs notes", 0)
    n20 = st.number_input("20rs notes", 0)
    n50 = st.number_input("50rs notes", 0)
    n100 = st.number_input("100rs notes", 0)
    n200 = st.number_input("200rs notes", 0)
    
    inv = {10: n10, 20: n20, 50: n50, 100: n100, 200: n200}
    total_plate = sum(k * v for k, v in inv.items())
    st.metric("Total in Plate", f"₹{total_plate}")

# --- 2. REQUESTS INPUT ---
st.header("2. Shopkeeper Requests")
num_p = st.number_input("Number of Shopkeepers", 1, 15, 3)

shopkeepers = []
for i in range(num_p):
    c1, c2 = st.columns([2, 1])
    name = c1.text_input(f"Name", f"Person {chr(65+i)}", key=f"n{i}")
    notes_in = c2.number_input(f"500s brought", 0, key=f"w{i}")
    shopkeepers.append({
        "name": name, 
        "target": notes_in * 500, 
        "change": {10:0, 20:0, 50:0, 100:0, 200:0},
        "current_val": 0,
        "returned_500s": 0
    })

# --- 3. THE ENGINE ---
if st.button("Calculate Final Distribution", type="primary"):
    temp_inv = inv.copy()
    
    # Sort: Big Players (those who brought more) get priority slots
    active_list = sorted(shopkeepers, key=lambda x: x['target'], reverse=True)

    # PHASE 1: INITIAL SMALL-TO-LARGE DEAL
    for d in [10, 20, 50, 100, 200]:
        while temp_inv[d] > 0:
            dealt = False
            for s in active_list:
                if s['current_val'] + d <= s['target'] and temp_inv[d] > 0:
                    s['change'][d] += 1
                    s['current_val'] += d
                    temp_inv[d] -= 1
                    dealt = True
            if not dealt: break

    # PHASE 2: CLEAN REVERSION (The "A gets 950" fix)
    # We check if anyone is NOT at a multiple of 500.
    for s in active_list:
        if s['current_val'] % 500 != 0:
            # Calculate the "messy" amount over the last 500 milestone
            extra_amount = s['current_val'] % 500
            s['returned_500s'] += 1 # Give them back one 500rs note
            
            # Remove notes from their pocket and put them back in the plate
            # We do this from largest to smallest to be efficient
            for d in [200, 100, 50, 20, 10]:
                while extra_amount >= d and s['change'][d] > 0:
                    s['change'][d] -= 1
                    s['current_val'] -= d
                    temp_inv[d] += 1
                    extra_amount -= d
            
            # SECOND CHANCE: Now that we put notes back in the plate, 
            # let's see if the NEXT person can use them to hit their milestone.
            for other_s in active_list:
                for d in [10, 20, 50, 100, 200]:
                    while other_s['current_val'] + d <= other_s['target'] and temp_inv[d] > 0:
                        other_s['change'][d] += 1
                        other_s['current_val'] += d
                        temp_inv[d] -= 1

    # --- 4. DISPLAY RESULTS ---
    st.divider()
    st.subheader("Final Distribution")

    for s in shopkeepers:
        # Calculate how many 500s were actually changed
        successful_exchanges = s['current_val'] // 500
        # Total returned = Original notes - successfully changed
        total_returned = (s['target'] // 500) - successful_exchanges
        
        with st.expander(f"👤 {s['name']} (Changed: {successful_exchanges} | Returned: {total_returned})"):
            if s['current_val'] == 0:
                st.error("❌ No exchange possible. Insufficient change in plate.")
            else:
                if total_returned > 0:
                    st.warning(f"⚠️ {total_returned} note(s) of 500rs returned due to insufficient small change.")
                
                # Show notes in order
                for d in [10, 20, 50, 100, 200]:
                    if s['change'][d] > 0:
                        st.write(f"**₹{d}:** {s['change'][d]} notes")
                
                st.write(f"---")
                st.write(f"**Total Received:** ₹{s['current_val']}")

    leftover = sum(k * v for k, v in temp_inv.items())
    st.info(f"**Leftover in Plate:** ₹{leftover}")
