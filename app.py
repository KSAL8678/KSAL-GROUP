import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="KSAL Master System", layout="wide")

# URLs
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwEljISVjYuTRC4zZ6yUEQwGltTnlbekDH-IdfdED-pzQ1TsobAXXZbPUskzR0KiAHj/exec"
SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
URL = f"https://script.google.com/macros/s/AKfycbxMVhNqDAkHwU9XZgT9VgXapx79myehDCqdDDayTO1AUxHEALbaoxs3jfQO7CQav-vq/exec"

@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_csv(URL)
        return df
    except:
        return pd.DataFrame()

df = load_data()

# 2. Sidebar Navigation
st.sidebar.title("🚛 KSAL Logistics")
menu = st.sidebar.radio("Go To:", ["Daily Trip Entry", "Fleet Dashboard"])

# --- MENU: DAILY TRIP ENTRY ---
if menu == "Daily Trip Entry":
    st.title("📝 Detailed Trip & Finance Form")
    
    with st.form("entry_form", clear_on_submit=True):
        # Basic Info
        c1, c2, c3, c4 = st.columns(4)
        t_date = c1.date_input("Date")
        t_time = c2.time_input("Time")
        v_no = c3.text_input("Vehicle No")
        d_name = c4.text_input("Driver Name")

        # Container Info
        c5, c6, c7, c8 = st.columns(4)
        cont_1 = c5.text_input("Container-1")
        cont_2 = c6.text_input("Container-2")
        size = c7.selectbox("Size", ["20", "40"])
        status = c8.selectbox("Status", ["MTY", "LDD"])

        # Route
        c9, c10, c11 = st.columns(3)
        r_from = c9.text_input("From")
        r_to = c10.text_input("To")
        cycle = c11.text_input("Cycle")

        st.divider()
        # New Column Order as requested
        c12, c13, c14, c15 = st.columns(4)
        party = c12.text_input("Party Name") # ૧. પાર્ટી
        d_used = c13.number_input("Trip Diesel Used (Liters)", min_value=0.0) # ૨. ડીઝલ (લિટર)
        d_sal = c14.number_input("Driver Salary", min_value=0.0) # ૩. ડ્રાઇવર સેલેરી
        t_status = c15.selectbox("Trip Status", ["Full", "Return"]) # ૪. ટ્રીપ સ્ટેટસ

        c16, c17, c18 = st.columns(3)
        d_rate = c16.number_input("Diesel Rate", min_value=0.0) # ૫. ડીઝલ રેટ
        p_rate = c17.number_input("Party Rate (Income)", min_value=0.0) # ૬. પાર્ટી રેટ
        g_pass = c18.number_input("Gate Pass Charge", min_value=0.0) # ૭. ગેટ પાસ ચાર્જ

        # Auto Calculations
        d_amt = d_used * d_rate # ૮. ડીઝલ એમાઉન્ટ
        income = p_rate - g_pass - d_amt - d_sal # ૯. ફાઈનલ ઇન્કમ

        st.divider()
        res_c1, res_c2 = st.columns(2)
        res_c1.metric("Diesel Amount", f"₹{d_amt}")
        res_c2.metric("Net Income", f"₹{income}")

        if st.form_submit_button("Save Movement Report"):
            payload = {
                "date": str(t_date), "time": str(t_time), "vehicle_no": v_no,
                "driver_name": d_name, "container_1": cont_1, "container_2": cont_2,
                "size": size, "status": status, "from": r_from, "to": r_to,
                "cycle": cycle, "party": party, "diesel_used": d_used, 
                "driver_salary": d_sal, "trip_status": t_status, "diesel_rate": d_rate,
                "party_rate": p_rate, "gate_pass": g_pass, "diesel_amount": d_amt, 
                "income": income
            }
            res = requests.post(SCRIPT_URL, json=payload)
            if res.status_code == 200:
                st.success("Trip Saved Successfully!")
                st.balloons()

# --- MENU: FLEET DASHBOARD ---
elif menu == "Fleet Dashboard":
    st.title("📊 Fleet Performance & Diesel Stock")
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No data found.")