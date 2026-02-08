import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Fair-Share Treasury Logic")
st.markdown("Strategy: **Round-Robin Fulfillment**. Everyone gets their 1st note swapped before anyone gets their 2nd.")

# --- 1. Collection Inventory ---
with st.sidebar:
    st.header("1. Plate Inventory")
    n200 = st.number_input("200rs count", 0, value=10)
    n100 = st.number_input("100rs count", 0, value=10)
    n50 = st.number_input("50rs count", 0, value=10)
    n20 = st.number_input("20rs count", 0, value=20)
    n10 = st.number_input("10rs count", 0, value=50)
    
    inv = {200: n200, 100: n100, 50: n50, 20: n20, 10: n10}
    total_plate = sum(k * v for k, v in inv.items())
    st.metric("Total in Plate", f"₹{total_plate}")

# --- 2. Exchange Requests ---
st.header("2. Request List")
num_p = st.number_input("How many people?", 1, 10, 3)

people_data = []
for i in range(num_p):
    c1, c2 = st.columns([2, 1])
    with c1:
        name = st.text_input(f"Name", f"Person {chr(65+i)}", key=f"name_{i}")
    with c2:
        wants = st.number_input(f"500s to swap", 1, 10, 1, key=f"wants_{i}")
    # Initialize person object
    people_data.append({
        "name": name, 
        "wants": wants, 
        "fulfilled_count": 0, 
        "received_notes": {200:0, 100:0, 50:0, 20:0, 10:0}
    })

# --- 3. The Fair Distribution Logic ---
if st.button("Distribute Equivalently", type="primary"):
    temp_inv = inv.copy()
    
    # We determine the maximum number of notes anyone wants to set the number of rounds
    max_rounds = max(p["wants"] for p in people_data)
    
    # ROUND-ROBIN: We process the "First 500" for everyone, then the "Second 500", etc.
    for round_num in range(max_rounds):
        for p in people_data:
            # Check if this person still needs a note in this round
            if p["fulfilled_count"] < p["wants"]:
                
                # Attempt to build ONE 500rs note from the remaining inventory
                current_fill = 0
                temp_bag = {200:0, 100:0, 50:0, 20:0, 10:0}
                
                # Use Greedy approach for the individual 500rs build
                for denom in [200, 100, 50, 20, 10]:
                    while current_fill + denom <= 500 and temp_inv[denom] > 0:
                        temp_bag[denom] += 1
                        temp_inv[denom] -= 1
                        current_fill += denom
                
                # Success Check: Did we manage to reach exactly 500?
                if current_fill == 500:
                    p["fulfilled_count"] += 1
                    for d in temp_bag:
                        p["received_notes"][d] += temp_bag[d]
                else:
                    # Failure: Not enough change left for a full 500. 
                    # Return notes to the inventory for someone else to potentially use.
                    for d, count in temp_bag.items():
                        temp_inv[d] += count

    # --- 4. Results ---
    st.divider()
    st.subheader("Results")
    
    for p in people_data:
        status_color = "green" if p["fulfilled_count"] == p["wants"] else "orange"
        if p["fulfilled_count"] == 0: status_color = "red"
        
        with st.expander(f"👤 {p['name']} (Got {p['fulfilled_count']} of {p['wants']})"):
            if p["fulfilled_count"] > 0:
                st.write(f"**Total Received:** ₹{p['fulfilled_count'] * 500}")
                # Show note breakdown
                for d, count in p["received_notes"].items():
                    if count > 0:
                        st.write(f"- {d}rs notes: {count}")
            else:
                st.error("No change available for this person.")

    remaining_val = sum(k*v for k,v in temp_inv.items())
    st.info(f"**Remaining in Plate:** ₹{remaining_val}")
