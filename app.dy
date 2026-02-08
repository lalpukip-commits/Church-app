import streamlit as st

st.set_page_config(page_title="Church Treasury", page_icon="⛪")

st.title("⛪ Church Treasury Logic")
st.markdown("Enter values and click 'Calculate' to see the breakdown.")

# --- 1. Collection Inventory (Main Screen) ---
st.header("1. Collection Inventory")
# Values set to 0 by default
n10 = st.number_input("10rs count", min_value=0, value=0)
n20 = st.number_input("20rs count", min_value=0, value=0)
n50 = st.number_input("50rs count", min_value=0, value=0)
n100 = st.number_input("100rs count", min_value=0, value=0)
n200 = st.number_input("200rs count", min_value=0, value=0)

inv = {10: n10, 20: n20, 50: n50, 100: n100, 200: n200}
total_x = sum(k * v for k, v in inv.items())
st.metric("Total in Plate", f"{total_x}rs")

# --- 2. Exchange Requests ---
st.divider()
st.header("2. Exchange Requests")
num_p = st.number_input("How many people want an exchange?", 1, 10, 1)

people_data = []
for i in range(num_p):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input(f"Name {i+1}", f"Person {i+1}")
    with c2:
        wants = st.number_input(f"500s for {name}", 1, 10, 1)
    people_data.append({"name": name, "wants": wants})

# --- 3. Calculation Engine ---
def attempt_distribution(n_slots, original_inv):
    if n_slots == 0: return [], original_inv
    inv_copy = original_inv.copy()
    slots = [{"total": 0, "notes": {10:0, 20:0, 50:0, 100:0, 200:0}} for _ in range(n_slots)]
    for d in [10, 20, 50]:
        per_slot = inv_copy[d] // n_slots
        if per_slot > 0:
            for s in slots:
                s["notes"][d] += per_slot
                s["total"] += (per_slot * d)
            inv_copy[d] -= (per_slot * n_slots)
    for i in range(n_slots):
        needed = 500 - slots[i]["total"]
        for d in [200, 100, 50, 20, 10]:
            while needed >= d and inv_copy[d] > 0:
                slots[i]["notes"][d] += 1
                slots[i]["total"] += d
                inv_copy[d] -= 1
                needed -= d
        if needed > 0: return None, original_inv
    return slots, inv_copy

# --- 4. Display Results ---
if st.button("Calculate Distribution", type="primary"):
    theoretical_max = total_x // 500
    viable_slots, final_rem_inv, final_n = None, None, 0

    for n in range(theoretical_max, -1, -1):
        slots, rem_inv = attempt_distribution(n, inv)
        if slots is not None:
            viable_slots, final_rem_inv, final_n = slots, rem_inv, n
            break

    if final_n == 0:
        st.error("Not enough change to make a full 500rs exchange!")
    else:
        st.success(f"Distributed {final_n} exchange(s)!")
        
        # Fairly assign the calculated slots to the people
        curr_reqs = {p["name"]: p["wants"] for p in people_data}
        while sum(curr_reqs.values()) > final_n:
            highest = max(curr_reqs, key=curr_reqs.get)
            curr_reqs[highest] -= 1

        slot_idx = 0
        for p in people_data:
            num_assigned = curr_reqs[p["name"]]
            if num_assigned > 0:
                combined_notes = {10:0, 20:0, 50:0, 100:0, 200:0}
                for _ in range(num_assigned):
                    for d, count in viable_slots[slot_idx]["notes"].items():
                        combined_notes[d] += count
                    slot_idx += 1
                
                with st.expander(f"💰 {p['name']} - Give {num_assigned * 500}rs"):
                    for d, count in combined_notes.items():
                        if count > 0:
                            st.write(f"**{d}rs notes:** {count}")
            else:
                st.warning(f"No change available for {p['name']}")

        st.info(f"Remaining in Church Plate: {sum(k*v for k,v in final_rem_inv.items())}rs")
