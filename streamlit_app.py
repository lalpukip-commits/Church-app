import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")
st.title("⛪ Extreme Harmony Treasury")
st.markdown("Strategy: **Milestone Balancing** (Small-First + Person-to-Person Trading)")

# --- 1. INVENTORY INPUT ---
with st.sidebar:
    st.header("1. Plate Inventory")
    n10 = st.number_input("10rs notes", 0, key="inv10")
    n20 = st.number_input("20rs notes", 0, key="inv20")
    n50 = st.number_input("50rs notes", 0, key="inv50")
    n100 = st.number_input("100rs notes", 0, key="inv100")
    n200 = st.number_input("200rs notes", 0, key="inv200")
    
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
        "current_val": 0
    })

# --- 3. THE ENGINE ---
if st.button("Calculate Extreme Harmony", type="primary"):
    temp_inv = inv.copy()
    
    # STEP A: Determine how many total 500rs units we can support
    total_exchange_possible = (total_plate // 500) * 500
    total_requested = sum(s['target'] for s in shopkeepers)
    
    # STEP B: INITIAL SMALL-TO-LARGE DEAL
    # We distribute everything in the plate until the plate is empty or everyone is full
    for d in [10, 20, 50, 100, 200]:
        while temp_inv[d] > 0:
            dealt = False
            # Sort shopkeepers: those who are NOT yet at their target get priority
            for s in sorted(shopkeepers, key=lambda x: x['target'], reverse=True):
                if s['current_val'] + d <= s['target'] and temp_inv[d] > 0:
                    s['change'][d] += 1
                    s['current_val'] += d
                    temp_inv[d] -= 1
                    dealt = True
            if not dealt: break

    # STEP C: THE "HARMONY SWAP" (Person-to-Person Trading)
    # We loop to see if we can move notes from "Over" or "Incomplete" people to help others hit milestones
    for _ in range(10): # Run multiple balancing passes
        # Sort by who is CLOSEST to their next 500 milestone but not quite there
        shopkeepers.sort(key=lambda x: (x['current_val'] % 500) if x['current_val'] < x['target'] else 0, reverse=True)
        
        for receiver in shopkeepers:
            if receiver['current_val'] > 0 and receiver['current_val'] % 500 != 0:
                needed = 500 - (receiver['current_val'] % 500)
                
                # Try to take 'needed' amount from others who have notes to spare
                for giver in shopkeepers:
                    if giver == receiver: continue
                    
                    for d in [50, 20, 10]: # Prefer trading small notes
                        while giver['change'][d] > 0 and needed >= d:
                            giver['change'][d] -= 1
                            giver['current_val'] -= d
                            receiver['change'][d] += 1
                            receiver['current_val'] += d
                            needed -= d

    # STEP D: FINAL PLATE TOP-UP
    # Use any leftover 100s/200s to try and hit milestones
    for s in shopkeepers:
        for d in [200, 100, 50, 20, 10]:
            while s['current_val'] + d <= s['target'] and temp_inv[d] > 0:
                s['change'][d] += 1
                s['current_val'] += d
                temp_inv[d] -= 1

    # --- 4. DISPLAY RESULTS ---
    st.divider()
    st.subheader("Final Balanced Distribution")

    for s in shopkeepers:
        # A person is "satisfied" if they hit a multiple of 500
        satisfied_count = s['current_val'] // 500
        returned_notes = (s['target'] // 500) - satisfied_count
        
        with st.expander(f"👤 {s['name']} (Exchanged: {satisfied_count} | Returned: {returned_notes})"):
            if s['current_val'] == 0:
                st.error("No exchange possible for this person.")
            else:
                if returned_notes > 0:
                    st.warning(f"Note: {returned_notes} of your 500rs notes were returned (lack of change).")
                
                for d in [10, 20, 50, 100, 200]:
                    if s['change'][d] > 0:
                        st.write(f"**₹{d}:** {s['change'][d]} notes")
                
                st.write(f"**Total Received:** ₹{s['current_val']}")
                if s['current_val'] % 500 != 0:
                    st.info(f"⚠️ This person is off-milestone by ₹{s['current_val'] % 500}. Manual adjustment may be needed.")

    st.info(f"**Remaining in Plate:** ₹{sum(k*v for k,v in temp_inv.items())}")
