import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. Database Setup (Internal Storage)
conn = sqlite3.connect('ksal_logistics.db', check_same_thread=False)
c = conn.cursor()

# Create Tables if they don't exist
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

# Page Config
st.set_page_config(page_title="KSAL Master System", layout="wide")

# Sidebar Navigation
st.sidebar.title("KSAL Logistics")
menu = st.sidebar.radio("Main Menu", ["DASHBOARD", "MOVEMENT ENTRY", "DIESEL ENTRY", "DIESEL CHART"])

# --- D. DIESEL CHART (Setting up the Routes first) ---
if menu == "DIESEL CHART":
    st.title("📋 Diesel Master Chart")
    st.info("Define diesel consumption for each route here.")
    
    with st.form("chart_form"):
        route_name = st.text_input("Route Name (e.g., Mundra-Kandla)")
        f_diesel = st.number_input("Full Trip Diesel (Liters)", min_value=0.0)
        r_diesel = st.number_input("Return Trip Diesel (Liters)", min_value=0.0)
        if st.form_submit_button("Add/Update Route"):
            c.execute("INSERT OR REPLACE INTO diesel_chart VALUES (?, ?, ?)", (route_name, f_diesel, r_diesel))
            conn.commit()
            st.success("Route Updated!")

    chart_data = pd.read_sql("SELECT * FROM diesel_chart", conn)
    st.table(chart_data)

# --- B. MOVEMENT ENTRY ---
elif menu == "MOVEMENT ENTRY":
    st.title("🚛 Movement Entry")
    
    # Auto-suggest lists from database
    existing_data = pd.read_sql("SELECT v_no, name, party, src, dest, cycle FROM movement", conn)
    v_list = existing_data['v_no'].unique().tolist()
    d_list = existing_data['name'].unique().tolist()
    p_list = existing_data['party'].unique().tolist()
    route_list = pd.read_sql("SELECT route FROM diesel_chart", conn)['route'].tolist()

    with st.form("move_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        sr = col1.number_input("SR Number", min_value=1)
        date = col2.date_input("Date")
        time = col3.time_input("Time")

        v_no = st.selectbox("Vehicle Number", ["New"] + v_list)
        if v_no == "New": v_no = st.text_input("Enter New Vehicle No")
        
        name = st.selectbox("Driver Name", ["New"] + d_list)
        if name == "New": name = st.text_input("Enter New Driver Name")

        size = st.selectbox("Size", ["40", "20"])
        cont1 = st.text_input("Container-1 (11 Characters)", max_chars=11)
        
        cont2 = ""
        if size == "20":
            cont2 = st.text_input("Container-2 (Only for 20 Size)")

        st.divider()
        col4, col5, col6 = st.columns(3)
        status = col4.selectbox("Status", ["MTY", "LDD"])
        route_sel = col5.selectbox("Select Route", route_list)
        cycle = col6.text_input("Cycle")

        party = st.selectbox("Party", ["New"] + p_list)
        if party == "New": party = st.text_input("Enter New Party Name")

        t_status = st.selectbox("Trip Status", ["Full", "Return"])
        remarks = st.text_area("Remarks")

        # Logic for Salary and Diesel
        salary = 200 if size == "40" else 400
        
        # Auto-fetch Diesel from Chart
        route_info = pd.read_sql(f"SELECT * FROM diesel_chart WHERE route='{route_sel}'", conn)
        diesel_work = 0.0
        if not route_info.empty:
            diesel_work = route_info.iloc[0]['full_diesel'] if t_status == "Full" else route_info.iloc[0]['return_diesel']

        if st.form_submit_button("Save Movement"):
            c.execute("INSERT INTO movement VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                      (sr, str(date), str(time), v_no, name, cont1, cont2, size, status, route_sel, "", cycle, party, salary, t_status, diesel_work, remarks))
            conn.commit()
            st.success(f"Entry Saved! Diesel Work: {diesel_work} L, Salary: {salary}")

# --- C. DIESEL ENTRY ---
elif menu == "DIESEL ENTRY":
    st.title("⛽ Diesel Stock Entry")
    with st.form("diesel_f"):
        d_date = st.date_input("Date")
        v_no = st.text_input("Vehicle Number")
        issued = st.number_input("Issued Diesel (Liters)", min_value=0.0)
        d_name = st.text_input("Driver Name")
        rate = st.number_input("Rate", min_value=0.0)
        pump = st.text_input("Pump Name")
        paid = st.number_input("Paid Amount", min_value=0.0)
        
        amount = issued * rate
        outstanding = amount - paid
        
        if st.form_submit_button("Save Diesel Entry"):
            c.execute("INSERT INTO diesel_entry VALUES (?,?,?,?,?,?,?,?,?)", 
                      (str(d_date), v_no, issued, d_name, rate, amount, pump, paid, outstanding))
            conn.commit()
            st.success("Diesel Stock Updated!")

# --- A. DASHBOARD ---
elif menu == "DASHBOARD":
    st.title("📊 KSAL Analytics Dashboard")
    
    df_m = pd.read_sql("SELECT * FROM movement", conn)
    df_d = pd.read_sql("SELECT * FROM diesel_entry", conn)

    if not df_m.empty:
        # 1. Trip Stats
        st.subheader("Trip Statistics")
        m1, m2, m3 = st.columns(3)
        m1.metric("Today's Trips", len(df_m[df_m['date'] == str(datetime.now().date())]))
        m2.metric("Monthly Trips", len(df_m)) # Add month filter logic
        m3.metric("Yearly Trips", len(df_m))

        # 2. Diesel Inventory Logic
        st.divider()
        st.subheader("Vehicle Diesel Inventory")
        selected_v = st.selectbox("Select Vehicle for Audit", df_m['v_no'].unique())
        
        total_issued = df_d[df_d['v_no'] == selected_v]['issued'].sum()
        total_work = df_m[df_m['v_no'] == selected_v]['diesel_work'].sum()
        balance = total_issued - total_work
        
        i1, i2, i3 = st.columns(3)
        i1.metric("Total Diesel Issued", f"{total_issued} L")
        i2.metric("Total Diesel Work Done", f"{total_work} L")
        i3.metric("Current Stock in Vehicle", f"{balance} L", delta=balance)