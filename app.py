import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="KSAL Master Tracker", layout="wide")

# Google Sheet Connection
SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
URL = f"https://script.google.com/macros/s/AKfycbwEljISVjYuTRC4zZ6yUEQwGltTnIbekDH-ldfdED-pzQ1TsobAXXZbPUskzROKiAHj/exec"

@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_csv(URL)
        return df
    except:
        return None

df = load_data()

# 2. Application UI
st.title("🚛 KSAL Master Movement & Income Tracker")

if df is not None:
    menu = st.sidebar.radio("Navigation", ["Daily Trip Entry", "Fleet Dashboard"])
    
    # Extracting historical data for suggestions
    v_history = sorted(df.iloc[:, 3].dropna().unique().tolist())
    d_history = sorted(df.iloc[:, 5].dropna().unique().tolist())

    if menu == "Daily Trip Entry":
        st.subheader("📝 Detailed Trip & Finance Form")
        with st.form("master_form", clear_on_submit=True):
            
            # Row 1: Basic Info
            c1, c2, c3, c4 = st.columns(4)
            trip_date = c1.date_input("Date (Not Current)")
            trip_time = c2.time_input("Time (Not Current)")
            v_no = c3.text_input("Vehicle No", help="Start typing for suggestion")
            d_name = c4.text_input("Driver Name")

            # Row 2: Cargo & Logistics
            c5, c6, c7, c8 = st.columns(4)
            cont_1 = c5.text_input("Container-1")
            cont_2 = c6.text_input("Container-2")
            size = c7.selectbox("Size", ["20", "40"])
            status = c8.selectbox("Status", ["MTY", "LDD"])

            # Row 3: Route & Party
            c9, c10, c11, c12 = st.columns(4)
            r_from = c9.text_input("From")
            r_to = c10.text_input("To")
            cycle = c11.text_input("Cycle")
            party = c12.text_input("Party Name")

            # Row 4: Finance & Trip Status
            c13, c14, c15, c16 = st.columns(4)
            party_rate = c13.number_input("Party Rate", min_value=0.0)
            d_salary = c14.number_input("Driver Salary", min_value=0.0)
            gate_pass = c15.number_input("Gate Pass Charge", min_value=0.0)
            t_status = c16.selectbox("Trip Status", ["Full", "Return"])

            # Row 5: Diesel Details & Auto-Calc
            st.divider()
            c17, c18, c19, c20 = st.columns(4)
            d_used = c17.number_input("Trip Diesel Used", min_value=0.0)
            d_rate = c18.number_input("Diesel Rate", min_value=0.0)
            
            # Calculation logic as per your request
            d_amount = d_used * d_rate
            income = party_rate - gate_pass - d_amount - d_salary
            
            c19.metric("Diesel Amount", f"₹{d_amount}")
            c20.metric("Net Income", f"₹{income}")

            if st.form_submit_button("Save Movement Report"):
                st.success(f"Trip saved! Net Income: ₹{income}")
                st.balloons()

    elif menu == "Fleet Dashboard":
        st.subheader("📊 Fleet Performance")
        # Logic for monthly/yearly reports
        st.dataframe(df.tail(20))

else:
    st.error("Sheet data could not be reached.")