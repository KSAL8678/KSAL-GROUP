import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. Database Setup
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

# Sidebar
st.sidebar.title("KSAL Logistics")
menu = st.sidebar.radio("Navigation", ["DASHBOARD", "MOVEMENT ENTRY", "DIESEL ENTRY", "DIESEL CHART"])

# --- MOVEMENT ENTRY (Simplified Version) ---
if menu == "MOVEMENT ENTRY":
    st.title("🚛 Movement Entry")
    
    # Get history for auto-complete suggestions
    history = pd.read_sql("SELECT v_no, name, src, dest, cycle, party FROM movement", conn)
    
    with st.form("simple_move_form", clear_on_submit=True):
        # Row 1: SR, Date, Time
        c1, c2, c3 = st.columns(3)
        sr = c1.number_input("1. SR Number", min_value=1)
        date = c2.date_input("2. Date", value=datetime.now())
        time = c3.time_input("3. Time", value=datetime.now().time())

        # Row 2: Vehicle & Driver (Single text input with suggestions)
        c4, c5 = st.columns(2)
        v_no = c4.text_input("4. VEHICLE NUMBER", help="Type vehicle number here")
        if not history.empty and v_no == "":
            st.caption(f"Suggested: {', '.join(history['v_no'].unique()[:5])}")
            
        name = c5.text_input("5. DRIVER NAME")

        # Row 3: Size & Containers
        c6, c7, c8, c9 = st.columns(4)
        size = c6.selectbox("8. SIZE", ["40", "20"])
        cont1 = c7.text_input("6. CONTAINER-1", max_chars=11)
        
        cont2 = ""
        if size == "20":
            cont2 = c8.text_input("7. CONTAINER-2")
        
        status = c9.selectbox("9. STATUS", ["LDD", "MTY"])

        # Row 4: Route & Party
        c10, c11, c12, c13 = st.columns(4)
        f_loc = c10.text_input("10. FROM")
        t_loc = c11.text_input("11. TO")
        cycle = c12.text_input("12. CYCLE")
        party = c13.text_input("13. PARTY")

        st.divider()
        # Row 5: Salary & Trip Status
        c14, c15 = st.columns(2)
        salary_val = 200 if size == "40" else 400
        salary = c14.number_input("14. DRIVER SALARY", value=float(salary_val))
        t_status = c15.selectbox("15. TRIP STATUS", ["FULL", "RETURN"])

        # Diesel Work Logic
        route_key = f"{f_loc} to {t_loc}"
        chart_res = pd.read_sql(f"SELECT * FROM diesel_chart WHERE route='{route_key}'", conn)
        d_work = 0.0
        if not chart_res.empty:
            d_work = chart_res.iloc[0]['full_diesel'] if t_status == "FULL" else chart_res.iloc[0]['return_diesel']
        
        st.info(f"16. DIESEL WORK: {d_work} L")
        remarks = st.text_area("17. REMARKS")

        if st.form_submit_button("SAVE MOVEMENT"):
            if v_no and name:
                c.execute("INSERT INTO movement VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                          (sr, str(date), str(time), v_no, name, cont1, cont2, size, status, f_loc, t_loc, cycle, party, salary, t_status, d_work, remarks))
                conn.commit()
                st.success("Data Saved!")
            else:
                st.error("Please enter Vehicle Number and Driver Name")

# --- OTHER MENUS REMAIN SAME ---
elif menu == "DIESEL CHART":
    st.title("⛽ Diesel Route Chart")
    with st.form("chart_form"):
        route_n = st.text_input("Route (From to To)")
        f_d = st.number_input("Full Diesel", min_value=0.0)
        r_d = st.number_input("Return Diesel", min_value=0.0)
        if st.form_submit_button("Add to Chart"):
            c.execute("INSERT OR REPLACE INTO diesel_chart VALUES (?,?,?)", (route_n, f_d, r_d))
            conn.commit()
            st.success("Route Updated!")
    st.table(pd.read_sql("SELECT * FROM diesel_chart", conn))

elif menu == "DIESEL ENTRY":
    st.title("⛽ Diesel Entry")
    # ... (Same as previous code)