import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Church Treasury Logic")
st.markdown("Safe Exchange Mode: Only completes full 500rs increments. No one takes a loss.")

# --- 1. Collection Inventory ---
st.header("1. Collection Inventory")
c_inv1, c_inv2 = st.columns(2)
with c_inv1:
    n10 = st.number_input("10rs count", min_value=0, value=0)
    n20 = st.number_input("20rs count", min_value=0, value=0)
    n50 = st.number_input("50rs count", min_value=0, value=0)
with c_inv2:
    n100 = st.number_input("100rs count", min_value=0, value=0)
    n200 = st.number_input("200rs count", min_value=0, value=0)

inv = {10: n10, 20: n20, 50: n50, 100: n100, 200: n200}
total_plate = sum(k * v for k, v in inv.items())

st.metric("Total amount in Plate", f"{total_plate}rs")
st.divider()

# --- 2. Exchange Requests ---
st.header("2. Exchange Requests")
num_p = st.number_input("How many people?", 1, 10, 1)

people_data = []
total_notes_requested = 0
for i in range(num_p):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input(f"Name {i+1}", f"Person {i+1}")
    with c2:
        wants = st.number_input(f"500s for {name}", 1, 20, 1)
    total_notes_requested += wants
    people_data.append({"name": name, "wants": wants, "notes": {10:0, 20:0, 50:0, 100:0, 200:0}, "fulfilled_count": 0})

req_val = total_notes_requested * 500
diff = total_plate - req_val
st.metric("Total amount Requested", f"{req_val}rs", delta=f"{diff}rs", delta_color="normal")

if diff < 0:
    st.warning(f"⚠️ Shortage of {abs(diff)}rs detected. Only full 500rs exchanges will be processed.")

# --- 3. Safe Distribution Logic ---
st.divider()
if st.button("Calculate Distribution", type="primary"):
    temp_inv = inv.copy()
    
    # We process requests one 500rs note at a time to be fair
    # Step 1: Attempt to give everyone their FIRST 500rs exchange fairly
    # Step 2: Then attempt to give seconds, thirds, etc.
    max_wants = max(p["wants"] for p in people_data) if people_data else 0
    
    for round_num in range(max_wants):
        for p in people_data:
            if p["fulfilled_count"] < p["wants"]:
                # Attempt to create ONE 500rs exchange for this person
                current_attempt_notes = {10:0, 20:0, 50:0, 100:0, 200:0}
                needed = 500
                
                # Try to use smaller notes first (as you requested)
                for bill in [10, 20, 50, 100, 200]:
                    while needed >= bill and temp_inv[bill] > 0:
                        temp_inv[bill] -= 1
                        current_attempt_notes[bill] += 1
                        needed -= bill
                
                if needed == 0:
                    # SUCCESS: Add these notes to the person's total
                    p["fulfilled_count"] += 1
                    for b in current_attempt_notes:
                        p["notes"][b] += current_attempt_notes[b]
                else:
                    # FAILURE: Put the notes back in the plate (no loss for church or person)
                    for b, count in current_attempt_notes.items():
                        temp_inv[b] += count

    # --- 4. Final Result Display ---
    total_successful_val = sum(p["fulfilled_count"] for p in people_data) * 500
    st.success(f"Successfully processed {total_successful_val}rs in full exchanges.")

    for p in people_data:
        given_val = p["fulfilled_count"] * 500
        with st.expander(f"💰 {p['name']} - Received: {given_val}rs"):
            if p["fulfilled_count"] < p["wants"]:
                st.error(f"Could not fulfill {p['wants'] - p['fulfilled_count']} note(s). Return their 500rs note(s).")
            
            if p["fulfilled_count"] > 0:
                for b in [200, 100, 50, 20, 10]:
                    if p['notes'][b] > 0:
                        st.write(f"**{b}rs notes:** {p['notes'][b]}")
            else:
                st.write("No exchange possible. Keep their 500rs note.")

    st.info(f"Remaining in Church Plate: {sum(k*v for k,v in temp_inv.items())}rs")
