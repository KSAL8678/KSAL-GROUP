import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configuration
st.set_page_config(page_title="KSAL Master Tracker", layout="wide")

# Paste your Web App URL here from your photo
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwEljISVjYuTRC4zZ6yUEQwGltTnlbekDH-IdfdED-pzQ1TsobAXXZbPUskzR0KiAHj/exec"

# Loading Data Safely to avoid IndexError
@st.cache_data(ttl=1)
def load_data():
    try:
        SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
        URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=1114565751"
        df = pd.read_csv(URL)
        return df
    except:
        return pd.DataFrame() # Return empty if fail

df = load_data()

st.title("🚛 KSAL Master Movement & Income Tracker")

# Fixing the error: Check if columns exist before indexing
v_history = []
if not df.empty and len(df.columns) > 3:
    v_history = sorted(df.iloc[:, 3].dropna().unique().tolist())

# --- Trip Entry Form ---
with st.form("master_trip_form", clear_on_submit=True):
    c1, c2, c3, c4 = st.columns(4)
    t_date = c1.date_input("Date")
    t_time = c2.time_input("Time")
    v_no = c3.text_input("Vehicle No", help="Last entry will be saved for next time")
    d_name = c4.text_input("Driver Name")

    c5, c6, c7, c8 = st.columns(4)
    cont_1 = c5.text_input("Container-1")
    cont_2 = c6.text_input("Container-2")
    size = c7.selectbox("Size", ["20", "40"])
    status = c8.selectbox("Status", ["MTY", "LDD"])

    c9, c10, c11, c12 = st.columns(4)
    r_from = c9.text_input("From")
    r_to = c10.text_input("To")
    cycle = c11.text_input("Cycle")
    party = c12.text_input("Party Name")

    c13, c14, c15, c16 = st.columns(4)
    p_rate = c13.number_input("Party Rate", min_value=0.0)
    d_sal = c14.number_input("Driver Salary", min_value=0.0)
    g_pass = c15.number_input("Gate Pass Charge", min_value=0.0)
    t_status = c16.selectbox("Trip Status", ["Full", "Return"])

    st.divider()
    c17, c18 = st.columns(2)
    d_used = c17.number_input("Trip Diesel Used (Liters)", min_value=0.0)
    d_rate = c18.number_input("Diesel Rate", min_value=0.0)

    # Calculations
    d_amt = d_used * d_rate
    income = p_rate - g_pass - d_amt - d_sal

    if st.form_submit_button("Save Movement Report"):
        payload = {
            "date": str(t_date), "time": str(t_time), "vehicle_no": v_no,
            "driver_name": d_name, "container_1": cont_1, "container_2": cont_2,
            "size": size, "status": status, "from": r_from, "to": r_to,
            "cycle": cycle, "party": party, "driver_salary": d_sal,
            "trip_status": t_status, "diesel_used": d_used, "diesel_rate": d_rate,
            "diesel_amount": d_amt, "gate_pass": g_pass, "income": income
        }
        try:
            response = requests.post(SCRIPT_URL, json=payload)
            if response.status_code == 200:
                st.success(f"Trip Saved! Net Income: ₹{income}")
                st.balloons()
            else:
                st.error("Check Apps Script Deployment.")
        except:
            st.error("Connection Error. Check internet or URL.")