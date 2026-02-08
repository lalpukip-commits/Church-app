import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Church Treasury Logic")
st.markdown("Fair & Greedy: Shares small notes first, then fills gaps with large notes.")

# --- 1. Collection Inventory ---
st.header("1. Collection Inventory")
col_inv1, col_inv2 = st.columns(2)
with col_inv1:
    n10 = st.number_input("10rs count", min_value=0, value=0)
    n20 = st.number_input("20rs count", min_value=0, value=0)
    n50 = st.number_input("50rs count", min_value=0, value=0)
with col_inv2:
    n100 = st.number_input("100rs count", min_value=0, value=0)
    n200 = st.number_input("200rs count", min_value=0, value=0)

inv = {10: n10, 20: n20, 50: n50, 100: n100, 200: n200}
total_plate = sum(k * v for k, v in inv.items())

# --- 2. Exchange Requests ---
st.divider()
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
    people_data.append({"name": name, "wants": wants, "notes": {10:0, 20:0, 50:0, 100:0, 200:0}, "current_val": 0, "fulfilled": 0})

# --- 3. Summary Before Calculation ---
st.divider()
req_col1, req_col2 = st.columns(2)
with req_col1:
    st.metric("Total in Plate", f"{total_plate}rs")
with req_col2:
    total_req_val = total_notes_requested * 500
    st.metric("Total Requested", f"{total_req_val}rs", delta=f"{total_plate - total_req_val}rs surplus", delta_color="normal" if total_plate >= total_req_val else "inverse")

if total_plate < total_req_val:
    st.warning(f"⚠️ Warning: You are short by {total_req_val - total_plate}rs to fulfill all requests.")

# --- 4. Fair Distribution Logic ---
if st.button("Calculate Distribution", type="primary"):
    temp_inv = inv.copy()
    
    if total_notes_requested == 0:
        st.warning("No requests to process.")
    else:
        # STEP 1: Distribute small notes (10, 20, 50) FAIRLY
        for bill in [10, 20, 50]:
            per_500_slot = temp_inv[bill] // total_notes_requested
            if per_500_slot > 0:
                for person in people_data:
                    allocated = per_500_slot * person["wants"]
                    person["notes"][bill] += allocated
                    person["current_val"] += (allocated * bill)
                    temp_inv[bill] -= allocated

        # STEP 2: Finish each person's request using the Greedy method (Big notes first)
        for person in people_data:
            for _ in range(person["wants"]):
                target = (person["fulfilled"] + 1) * 500
                needed = target - person["current_val"]
                
                if needed <= 0:
                    person["fulfilled"] += 1
                    continue

                for bill in [200, 100, 50, 20, 10]:
                    while needed >= bill and temp_inv[bill] > 0:
                        temp_inv[bill] -= 1
                        person["notes"][bill] += 1
                        person["current_val"] += bill
                        needed -= bill
                
                if needed == 0:
                    person["fulfilled"] += 1
                else:
                    break

        # --- 5. Display Results ---
        st.success(f"Successfully prepared {sum(p['fulfilled'] for p in people_data)} of {total_notes_requested} total notes.")

        for p in people_data:
            with st.expander(f"💰 {p['name']} - Give {p['fulfilled'] * 500}rs"):
                if p['fulfilled'] < p['wants']:
                    st.error(f"Could only provide {p['fulfilled']} notes. Short by {p['wants'] - p['fulfilled']} note(s).")
                
                for bill in [200, 100, 50, 20, 10]:
                    if p['notes'][bill] > 0:
                        st.write(f"**{bill}rs notes:** {p['notes'][bill]}")

        rem_total = sum(k * v for k, v in temp_inv.items())
        st.info(f"Remaining in Church Plate: {rem_total}rs")
      
