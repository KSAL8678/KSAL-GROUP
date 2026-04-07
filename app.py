import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- DATABASE SETUP ---
conn = sqlite3.connect('ksal_master.db', check_same_thread=False)
c = conn.cursor()

# Create Tables
c.execute('''CREATE TABLE IF NOT EXISTS movement 
             (sr INTEGER, date TEXT, time TEXT, v_no TEXT, name TEXT, cont1 TEXT, cont2 TEXT, 
              size TEXT, status TEXT, src TEXT, dest TEXT, cycle TEXT, party TEXT, 
              salary REAL, trip_status TEXT, diesel_work REAL, remarks TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS diesel_entry 
             (date TEXT, v_no TEXT, issued REAL, name TEXT, rate REAL, amount REAL, 
              pump TEXT, paid REAL, outstanding REAL)''')

c.execute('''CREATE TABLE IF NOT EXISTS diesel_chart 
             (route TEXT PRIMARY KEY, full_diesel REAL, return_diesel REAL)''')
conn.commit()

# --- APP CONFIG ---
st.set_page_config(page_title="KSAL Master System", layout="wide")
st.sidebar.title("KSAL Logistics")
menu = st.sidebar.radio("Navigation", ["DASHBOARD", "MOVEMENT ENTRY", "DIESEL ENTRY", "DIESEL CHART"])

# --- MENU: DASHBOARD ---
if menu == "DASHBOARD":
    st.title("📊 Dashboard")
    df_m = pd.read_sql("SELECT * FROM movement", conn)
    df_d = pd.read_sql("SELECT * FROM diesel_entry", conn)
    
    if not df_m.empty:
        col1, col2, col3 = st.columns(3)
        today = str(datetime.now().date())
        col1.metric("Today's Trips", len(df_m[df_m['date'] == today]))
        col2.metric("Total Monthly Trips", len(df_m))
        
        st.divider()
        st.subheader("Vehicle Diesel Stock Audit")
        selected_v = st.selectbox("Select Vehicle", df_m['v_no'].unique())
        total_issued = df_d[df_d['v_no'] == selected_v]['issued'].sum()
        total_used = df_m[df_m['v_no'] == selected_v]['diesel_work'].sum()
        st.metric("Balance Diesel in Vehicle", f"{total_issued - total_used} L")

# --- MENU: MOVEMENT ENTRY (17 POINTS LIST) ---
elif menu == "MOVEMENT ENTRY":
    st.title("🚛 Movement Entry")
    
    # 1. SR Number
    sr = st.number_input("1. SR Number (Yearly Start)", min_value=1)
    
    # 2 & 3. Date and Time
    c_date, c_time = st.columns(2)
    t_date = c_date.date_input("2. Date", value=datetime.now())
    t_time = c_time.time_input("3. Time", value=datetime.now().time())

    # 4 & 5. Vehicle & Driver
    c_v, c_d = st.columns(2)
    v_no = c_v.text_input("4. VEHICLE NUMBER")
    d_name = c_d.text_input("5. DRIVER NAME")

    # 8. SIZE (Selection triggers Container 2)
    size = st.selectbox("8. SIZE", ["40", "20"])
    
    # 6 & 7. Containers
    c_cont1, c_cont2 = st.columns(2)
    cont1 = c_cont1.text_input("6. CONTAINER-1 (11 Characters)", max_chars=11)
    cont2 = ""
    if size == "20":
        cont2 = c_cont2.text_input("7. CONTAINER-2 (11 Characters)", max_chars=11)

    # 9. STATUS
    status = st.selectbox("9. STATUS", ["LDD", "MTY"])

    # 10, 11, 12, 13. Route & Party
    c_loc1, c_loc2, c_cyc, c_pty = st.columns(4)
    f_loc = c_loc1.text_input("10. FROM")
    t_loc = c_loc2.text_input("11. TO")
    cycle = c_cyc.text_input("12. CYCLE")
    party = c_pty.text_input("13. PARTY")

    # 14. Salary Logic
    # 40ft = 200, 20ft = 400 (based on your 1*40 and 2*20 logic)
    sal_val = 200.0 if size == "40" else 400.0
    salary = st.number_input("14. DRIVER SALARY", value=sal_val)

    # 15. Trip Status
    t_status = st.selectbox("15. TRIP STATUS", ["FULL", "RETURN"])

    # 16. Diesel Work (Auto Calculation)
    route_key = f"{f_loc} to {t_loc}"
    res = pd.read_sql(f"SELECT * FROM diesel_chart WHERE route='{route_key}'", conn)
    d_work = 0.0
    if not res.empty:
        d_work = res.iloc[0]['full_diesel'] if t_status == "FULL" else res.iloc[0]['return_diesel']
    
    st.info(f"16. DIESEL WORK: {d_work} Liters (Auto-calculated)")

    # 17. Remarks
    remarks = st.text_area("17. REMARKS")

    if st.button("SAVE MOVEMENT DATA"):
        if v_no and cont1:
            c.execute("INSERT INTO movement VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                      (sr, str(t_date), str(t_time), v_no, d_name, cont1, cont2, size, status, f_loc, t_loc, cycle, party, salary, t_status, d_work, remarks))
            conn.commit()
            st.success("Trip Entry Saved Successfully!")
        else:
            st.error("Please fill Vehicle Number and Container-1")

# --- MENU: DIESEL ENTRY ---
elif menu == "DIESEL ENTRY":
    st.title("⛽ Diesel Entry")
    with st.form("d_form"):
        d1, d2, d3 = st.columns(3)
        date = d1.date_input("1. DATE")
        v_no = d2.text_input("2. VEHICLE NUMBER")
        issued = d3.number_input("3. ISSUED DIESEL (L)", min_value=0.0)
        
        d4, d5, d6 = st.columns(3)
        name = d4.text_input("4. DRIVER NAME")
        rate = d5.number_input("5. RATE", min_value=0.0)
        pump = d6.text_input("7. PUMP NAME")
        
        paid = st.number_input("8. PAID AMOUNT", min_value=0.0)
        
        amount = issued * rate # 6. Amount
        out = amount - paid    # 9. Outstanding
        
        if st.form_submit_button("Save Diesel Stock"):
            c.execute("INSERT INTO diesel_entry VALUES (?,?,?,?,?,?,?,?,?)", 
                      (str(date), v_no, issued, name, rate, amount, pump, paid, out))
            conn.commit()
            st.success(f"Saved! Total: {amount}, Outstanding: {out}")

# --- MENU: DIESEL CHART ---
elif menu == "DIESEL CHART":
    st.title("📋 Diesel Master Route Chart")
    with st.form("route_form"):
        r_name = st.text_input("Route Name (e.g. Mundra to Kandla)")
        f_d = st.number_input("Full Trip Diesel (L)")
        r_d = st.number_input("Return Trip Diesel (L)")
        if st.form_submit_button("Update Route Chart"):
            c.execute("INSERT OR REPLACE INTO diesel_chart VALUES (?,?,?)", (r_name, f_d, r_d))
            conn.commit()
            st.success("Route Added to Master Chart")
    
    st.subheader("Current Route Chart")
    st.table(pd.read_sql("SELECT * FROM diesel_chart", conn))