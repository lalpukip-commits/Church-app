import streamlit as st
import random

st.set_page_config(page_title="Church Treasury", page_icon="⛪")
st.title("⛪ Treasury: Sacrifice & Rebalance")
st.markdown("Strategy: **Sacrifice Logic** + **Small-to-Large** + **Clean Reversion**")

# --- 1. INVENTORY ---
with st.sidebar:
    st.header("1. Plate Inventory")
    inv = {
        10: st.number_input("10rs count", 0),
        20: st.number_input("20rs count", 0),
        50: st.number_input("50rs count", 0),
        100: st.number_input("100rs count", 0),
        200: st.number_input("200rs count", 0)
    }
    total_plate = sum(k * v for k, v in inv.items())
    st.metric("Total in Plate", f"₹{total_plate}")

# --- 2. REQUESTS ---
st.header("2. Shopkeeper Requests")
num_p = st.number_input("Number of Shopkeepers", 1, 15, 4)

shopkeepers = []
for i in range(num_p):
    c1, c2 = st.columns([2, 1])
    name = c1.text_input(f"Name", f"Person {chr(65+i)}", key=f"n{i}")
    notes_in = c2.number_input(f"500s brought", 0, key=f"w{i}")
    shopkeepers.append({
        "name": name, 
        "orig": notes_in, 
        "target": notes_in * 500,
        "change": {10:0, 20:0, 50:0, 100:0, 200:0},
        "current_val": 0
    })

# --- 3. THE ENGINE ---
if st.button("Calculate Final Distribution", type="primary"):
    temp_inv = inv.copy()
    
    # Sort for initial deal: People who brought more 500s get served first
    active_list = sorted(shopkeepers, key=lambda x: x['orig'], reverse=True)

    # STEP A: SMALL-TO-LARGE ROUND ROBIN DEAL
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

    # STEP B: IDENTIFY THE SACRIFICE
    # Find max 'orig' notes brought
    max_notes = max(s['orig'] for s in shopkeepers)
    # Get all who brought that max amount
    candidates = [s for s in shopkeepers if s['orig'] == max_notes]
    # Pick one randomly if there is a tie
    sacrifice = random.choice(candidates)
    st.toast(f"Sacrifice chosen: {sacrifice['name']}")

    # STEP C: THE SWAP (Give from Sacrifice to others to hit 500/1000/1500)
    for receiver in shopkeepers:
        if receiver == sacrifice: continue
        
        # If receiver is close to a milestone (e.g. 970 or 990)
        if receiver['current_val'] > 0 and receiver['current_val'] % 500 != 0:
            needed = 500 - (receiver['current_val'] % 500)
            
            # Try to take from Sacrifice's loose change
            for d in [50, 20, 10]: 
                while sacrifice['change'][d] > 0 and needed >= d:
                    sacrifice['change'][d] -= 1
                    sacrifice['current_val'] -= d
                    receiver['change'][d] += 1
                    receiver['current_val'] += d
                    needed -= d

    # STEP D: CLEAN REVERSION
    # After swaps, anyone not at a perfect milestone is rounded down.
    # Loose change goes back to plate.
    for s in shopkeepers:
        if s['current_val'] % 500 != 0:
            extra = s['current_val'] % 500
            # Remove notes to reach last 500 milestone
            for d in [200, 100, 50, 20, 10]:
                while extra >= d and s['change'][d] > 0:
                    s['change'][d] -= 1
                    s['current_val'] -= d
                    temp_inv[d] += 1
                    extra -= d

    # --- 4. DISPLAY RESULTS ---
    st.divider()
    st.subheader("Final Balanced Distribution")

    for s in shopkeepers:
        exchanged = s['current_val'] // 500
        returned = s['orig'] - exchanged
        
        with st.expander(f"👤 {s['name']} (Changed: {exchanged} | Returned: {returned})"):
            if s['current_val'] == 0:
                st.error("No exchange possible.")
            else:
                if returned > 0:
                    st.warning(f"{returned} note(s) of 500rs returned.")
                
                for d in [10, 20, 50, 100, 200]:
                    if s['change'][d] > 0:
                        st.write(f"**₹{d}:** {s['change'][d]} notes")
                st.write(f"**Total Received:** ₹{s['current_val']}")

    leftover = sum(k * v for k, v in temp_inv.items())
    st.info(f"Remaining in Plate: ₹{leftover}")
