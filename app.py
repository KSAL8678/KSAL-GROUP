import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. Internal Database Setup (No Google Sheets needed)
conn = sqlite3.connect('ksal_logistics.db', check_same_thread=False)
c = conn.cursor()

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

# Page Setup
st.set_page_config(page_title="KSAL Master System", layout="wide")

# Sidebar Menu
st.sidebar.title("KSAL Logistics")
menu = st.sidebar.radio("Navigation", ["DASHBOARD", "MOVEMENT ENTRY", "DIESEL ENTRY", "DIESEL CHART"])

# --- B. MOVEMENT ENTRY (FULL LIST AS PER YOUR REQUEST) ---
if menu == "MOVEMENT ENTRY":
    st.title("🚛 Movement Entry")
    
    # Getting auto-suggest data from previous entries
    history = pd.read_sql("SELECT v_no, name, src, dest, cycle, party FROM movement", conn)
    
    with st.form("full_move_form", clear_on_submit=True):
        # Row 1: SR, Date, Time
        c1, c2, c3 = st.columns(3)
        sr = c1.number_input("1. SR Number (Yearly Start)", min_value=1)
        date = c2.date_input("2. Date", value=datetime.now())
        time = c3.time_input("3. Time", value=datetime.now().time())

        # Row 2: Vehicle & Driver (Auto Suggest)
        c4, c5 = st.columns(2)
        v_no = c4.selectbox("4. VEHICLE NUMBER", ["Type New"] + history['v_no'].unique().tolist())
        if v_no == "Type New": v_no = c4.text_input("Enter New Vehicle No")
        
        name = c5.selectbox("5. DRIVER NAME", ["Type New"] + history['name'].unique().tolist())
        if name == "Type New": name = c5.text_input("Enter New Driver Name")

        # Row 3: Containers & Size
        c6, c7, c8, c9 = st.columns(4)
        size = c6.selectbox("8. SIZE", ["40", "20"])
        cont1 = c7.text_input("6. CONTAINER-1 (11 Chars)", max_chars=11)
        
        cont2 = ""
        if size == "20":
            cont2 = c8.text_input("7. CONTAINER-2 (For 20 Only)")
        
        status = c9.selectbox("9. STATUS", ["LDD", "MTY"])

        # Row 4: Route & Party (Auto Suggest)
        c10, c11, c12, c13 = st.columns(4)
        f_loc = c10.selectbox("10. FROM", ["Type New"] + history['src'].unique().tolist())
        if f_loc == "Type New": f_loc = c10.text_input("Enter New From")
        
        t_loc = c11.selectbox("11. TO", ["Type New"] + history['dest'].unique().tolist())
        if t_loc == "Type New": t_loc = c11.text_input("Enter New To")
        
        cycle = c12.selectbox("12. CYCLE", ["Type New"] + history['cycle'].unique().tolist())
        if cycle == "Type New": cycle = c12.text_input("Enter New Cycle")
        
        party = c13.selectbox("13. PARTY", ["Type New"] + history['party'].unique().tolist())
        if party == "Type New": party = c13.text_input("Enter New Party")

        # Row 5: Salary & Trip Status
        st.divider()
        c14, c15 = st.columns(2)
        # 14. Salary Logic: 40ft = 200, 20ft = 400
        salary_val = 200 if size == "40" else 400
        salary = c14.number_input("14. DRIVER SALARY (Auto)", value=float(salary_val))
        
        t_status = c15.selectbox("15. TRIP STATUS", ["FULL", "RETURN"])

        # 16. Diesel Work Logic from Chart
        route_key = f"{f_loc} to {t_loc}"
        chart_res = pd.read_sql(f"SELECT * FROM diesel_chart WHERE route='{route_key}'", conn)
        d_work = 0.0
        if not chart_res.empty:
            d_work = chart_res.iloc[0]['full_diesel'] if t_status == "FULL" else chart_res.iloc[0]['return_diesel']
        
        st.info(f"16. DIESEL WORK (Auto from Chart): {d_work} Liters")
        
        # 17. Remarks
        remarks = st.text_area("17. REMARKS")

        if st.form_submit_button("SAVE MOVEMENT"):
            c.execute("INSERT INTO movement VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                      (sr, str(date), str(time), v_no, name, cont1, cont2, size, status, f_loc, t_loc, cycle, party, salary, t_status, d_work, remarks))
            conn.commit()
            st.success("Entry Saved Successfully!")

# --- D. DIESEL CHART (CRITICAL FOR AUTO DIESEL) ---
elif menu == "DIESEL CHART":
    st.title("⛽ Diesel Route Chart")
    with st.form("chart_form"):
        route_n = st.text_input("Route Name (e.g., Mundra to Kandla)")
        f_d = st.number_input("Full Diesel Liter", min_value=0.0)
        r_d = st.number_input("Return Diesel Liter", min_value=0.0)
        if st.form_submit_button("Add to Chart"):
            c.execute("INSERT OR REPLACE INTO diesel_chart VALUES (?,?,?)", (route_n, f_d, r_d))
            conn.commit()
            st.success("Route Added!")
    
    st.table(pd.read_sql("SELECT * FROM diesel_chart", conn))

# --- C. DIESEL ENTRY ---
elif menu == "DIESEL ENTRY":
    st.title("⛽ Diesel Entry")
    with st.form("d_entry"):
        c1, c2, c3 = st.columns(3)
        d_date = c1.date_input("1. DATE")
        d_v_no = c2.text_input("2. VEHICLE NUMBER")
        d_issued = c3.number_input("3. ISSUED DIESEL (L)", min_value=0.0)
        
        c4, c5, c6 = st.columns(3)
        d_name = c4.text_input("4. DRIVER NAME")
        d_rate = c5.number_input("5. RATE", min_value=0.0)
        d_pump = c6.text_input("7. PUMP NAME")
        
        d_paid = st.number_input("8. PAID AMOUNT", min_value=0.0)
        
        d_amount = d_issued * d_rate # 6. Amount
        d_out = d_amount - d_paid # 9. Outstanding
        
        st.write(f"Total Amount: {d_amount} | Outstanding: {d_out}")
        
        if st.form_submit_button("SAVE DIESEL"):
            c.execute("INSERT INTO diesel_entry VALUES (?,?,?,?,?,?,?,?,?)", 
                      (str(d_date), d_v_no, d_issued, d_name, d_rate, d_amount, d_pump, d_paid, d_out))
            conn.commit()
            st.success("Diesel Entry Saved!")

# --- A. DASHBOARD ---
elif menu == "DASHBOARD":
    st.title("📊 Analytics Dashboard")
    df_m = pd.read_sql("SELECT * FROM movement", conn)
    df_d = pd.read_sql("SELECT * FROM diesel_entry", conn)
    
    if not df_m.empty:
        # Trips Stats
        t1, t2, t3 = st.columns(3)
        t1.metric("Today Trips", len(df_m[df_m['date'] == str(datetime.now().date())]))
        
        # Diesel Inventory per Vehicle
        st.divider()
        sel_v = st.selectbox("Check Diesel Stock for Vehicle", df_m['v_no'].unique())
        issued = df_d[df_d['v_no'] == sel_v]['issued'].sum()
        used = df_m[df_m['v_no'] == sel_v]['diesel_work'].sum()
        st.metric("Current Diesel Stock", f"{issued - used} Liters")