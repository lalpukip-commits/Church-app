import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Church Treasury Logic")
st.markdown("Reorganized Layout: Totals appear immediately after their respective sections.")

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

# --- TOTAL IN PLATE (Right after inventory) ---
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
    people_data.append({"name": name, "wants": wants, "notes": {10:0, 20:0, 50:0, 100:0, 200:0}, "current_val": 0, "fulfilled": 0})

# --- TOTAL REQUESTED (Right after requests) ---
req_val = total_notes_requested * 500
diff = total_plate - req_val

st.metric("Total amount Requested", f"{req_val}rs", delta=f"{diff}rs (Surplus/Deficit)", delta_color="normal")

if diff < 0:
    st.warning(f"⚠️ You are short by {abs(diff)}rs. Some people will not get their full amount.")
elif diff == 0 and total_notes_requested > 0:
    st.info("Perfect Match! You have exactly enough.")
elif diff > 0 and total_notes_requested > 0:
    st.success(f"You have a surplus of {diff}rs remaining.")

# --- 3. Calculation Logic ---
st.divider()
if st.button("Calculate Distribution", type="primary"):
    temp_inv = inv.copy()
    
    # Stage 1: Fair Share of small notes
    for bill in [10, 20, 50]:
        if total_notes_requested > 0:
            per_slot = temp_inv[bill] // total_notes_requested
            if per_slot > 0:
                for p in people_data:
                    amt = per_slot * p["wants"]
                    p["notes"][bill] += amt
                    p["current_val"] += (amt * bill)
                    temp_inv[bill] -= amt

    # Stage 2: Fill to 500rs using Greedy method
    for p in people_data:
        for _ in range(p["wants"]):
            target = (p["fulfilled"] + 1) * 500
            needed = target - p["current_val"]
            if needed <= 0:
                p["fulfilled"] += 1
                continue
            for bill in [200, 100, 50, 20, 10]:
                while needed >= bill and temp_inv[bill] > 0:
                    temp_inv[bill] -= 1
                    p["notes"][bill] += 1
                    p["current_val"] += bill
                    needed -= bill
            if needed == 0:
                p["fulfilled"] += 1

    # --- 4. Final Result Display ---
    for p in people_data:
        with st.expander(f"💰 {p['name']} - Total Given: {p['current_val']}rs"):
            if p['fulfilled'] < p['wants']:
                st.error(f"Note: Only {p['fulfilled']} full 500rs notes possible.")
            for b in [200, 100, 50, 20, 10]:
                if p['notes'][b] > 0:
                    st.write(f"**{b}rs notes:** {p['notes'][b]}")

    st.info(f"Remaining in Church Plate: {sum(k*v for k,v in temp_inv.items())}rs")
  
