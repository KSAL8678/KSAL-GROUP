import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io

# --- DATABASE SETUP ---
conn = sqlite3.connect('ksal_master.db', check_same_thread=False)
c = conn.cursor()

# 17 Points Database Structure
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

# --- AUTO-SORT & UPDATE SR FUNCTION ---
def sort_and_update_sr():
    df = pd.read_sql("SELECT * FROM movement", conn)
    if not df.empty:
        # Combined Date and Time for perfect sorting
        df['dt_temp'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        df = df.sort_values(by='dt_temp').reset_index(drop=True)
        # Re-assign SR Numbers from 1 onwards
        df['sr'] = df.index + 1
        df.drop(columns=['dt_temp'], inplace=True)
        df.to_sql('movement', conn, if_exists='replace', index=False)
        conn.commit()
    return df

# --- EXCEL DOWNLOAD FUNCTION ---
def to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Movement_Report')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

# --- APP CONFIG ---
st.set_page_config(page_title="KSAL Master System", layout="wide")
st.sidebar.title("KSAL Logistics")
menu = st.sidebar.radio("Navigation", ["DASHBOARD", "MOVEMENT ENTRY", "DIESEL ENTRY", "DIESEL CHART"])

# --- MENU: DASHBOARD ---
if menu == "DASHBOARD":
    st.title("📊 Dashboard & Reports")
    df_sorted = sort_and_update_sr() # Ensure SRs are updated
    
    if not df_sorted.empty:
        # Download Button for Excel
        excel_data = to_excel(df_sorted)
        st.download_button(label="📥 Download Movement Report (Excel)",
                           data=excel_data,
                           file_name=f'Movement_Report_{datetime.now().date()}.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        st.subheader("Live Movement Records (Auto-Sorted by Date/Time)")
        st.dataframe(df_sorted)

# --- MENU: MOVEMENT ENTRY ---
elif menu == "MOVEMENT ENTRY":
    st.title("🚛 Movement Entry")
    
    # Date and Time Inputs (Auto-sort based on these)
    c_date, c_time = st.columns(2)
    t_date = c_date.date_input("2. Date", value=datetime.now())
    t_time = c_time.time_input("3. Time", value=datetime.now().time())

    c_v, c_d = st.columns(2)
    v_no = c_v.text_input("4. VEHICLE NUMBER")
    d_name = c_d.text_input("5. DRIVER NAME")

    # Size Selection (Triggers Container 2)
    size = st.selectbox("8. SIZE", ["40", "20"])
    c_cont1, c_cont2 = st.columns(2)
    cont1 = c_cont1.text_input("6. CONTAINER-1 (11 Characters)", max_chars=11)
    cont2 = ""
    if size == "20":
        cont2 = c_cont2.text_input("7. CONTAINER-2 (11 Characters)", max_chars=11)

    status = st.selectbox("9. STATUS", ["LDD", "MTY"])

    c_loc1, c_loc2, c_cyc, c_pty = st.columns(4)
    f_loc = c_loc1.text_input("10. FROM")
    t_loc = c_loc2.text_input("11. TO")
    cycle = c_cyc.text_input("12. CYCLE")
    party = c_pty.text_input("13. PARTY")

    # Salary logic: Fixed 200 for both
    salary = st.number_input("14. DRIVER SALARY", value=200.0)
    t_status = st.selectbox("15. TRIP STATUS", ["FULL", "RETURN"])

    # Diesel Calculation from Master Chart
    route_key = f"{f_loc} to {t_loc}"
    res = pd.read_sql(f"SELECT * FROM diesel_chart WHERE route='{route_key}'", conn)
    d_work = 0.0
    if not res.empty:
        d_work = res.iloc[0]['full_diesel'] if t_status == "FULL" else res.iloc[0]['return_diesel']
    
    st.info(f"16. DIESEL WORK: {d_work} L")
    remarks = st.text_area("17. REMARKS")

    if st.button("SAVE MOVEMENT DATA"):
        if v_no and cont1:
            # Temporary SR placeholder, updated immediately by sort_and_update_sr
            c.execute("INSERT INTO movement (date, time, v_no, name, cont1, cont2, size, status, src, dest, cycle, party, salary, trip_status, diesel_work, remarks) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                      (str(t_date), str(t_time), v_no, d_name, cont1, cont2, size, status, f_loc, t_loc, cycle, party, salary, t_status, d_work, remarks))
            conn.commit()
            sort_and_update_sr() # Critical: Re-sorts everything and re-assigns SR
            st.success("Entry Saved! Sequence updated automatically.")
        else:
            st.error("Missing Data")

# --- OTHER MENUS (DIESEL ENTRY & CHART) ---
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
        amount = issued * rate 
        out = amount - paid    
        
        if st.form_submit_button("Save Diesel Stock"):
            c.execute("INSERT INTO diesel_entry VALUES (?,?,?,?,?,?,?,?,?)", 
                      (str(date), v_no, issued, name, rate, amount, pump, paid, out))
            conn.commit()
            st.success(f"Diesel Entry Saved!")

elif menu == "DIESEL CHART":
    st.title("📋 Diesel Master Route Chart")
    with st.form("route_form"):
        r_name = st.text_input("Route Name (e.g. Mundra to Kandla)")
        f_d = st.number_input("Full Trip Diesel (L)")
        r_d = st.number_input("Return Trip Diesel (L)")
        if st.form_submit_button("Update Route Chart"):
            c.execute("INSERT OR REPLACE INTO diesel_chart VALUES (?,?,?)", (r_name, f_d, r_d))
            conn.commit()
            st.success("Route Updated")
    st.table(pd.read_sql("SELECT * FROM diesel_chart", conn))