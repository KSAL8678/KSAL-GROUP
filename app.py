import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="KSAL Movement Report", layout="wide")

# Google Sheet Connection
SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=1114565751"

@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_csv(URL)
        return df
    except:
        return None

# 2. Main App Logic
st.title("🚛 KSAL Master Movement & Income Tracker")
df = load_data()

if df is not None:
    menu = st.sidebar.radio("Navigation", ["Dashboard", "New Trip Entry"])
    
    if menu == "Dashboard":
        # Vehicle selection
        vehicles = df.iloc[:, 3].dropna().unique().tolist()
        v_sel = st.selectbox("Select Vehicle to Check Status", vehicles)
        
        # Diesel stock calculation (Purchased - Used)
        v_data = df[df.iloc[:, 3] == v_sel]
        stock = v_data.iloc[:, 16].sum() - v_data.iloc[:, 15].sum()
        
        st.metric(f"Current Diesel Stock for {v_sel}", f"{stock} Liters")
        st.subheader("Recent Trip Logs")
        st.dataframe(df.tail(10))

    elif menu == "New Trip Entry":
        st.subheader("📝 Detailed Trip & Finance Form")
        with st.form("master_trip_form", clear_on_submit=True):
            # Row 1: Basic Info
            c1, c2, c3, c4 = st.columns(4)
            trip_date = c1.date_input("Trip Date", datetime.now())
            trip_time = c2.time_input("Trip Time", datetime.now())
            v_no = c3.selectbox("Vehicle No", df.iloc[:, 3].dropna().unique().tolist())
            d_name = c4.selectbox("Driver Name", df.iloc[:, 5].dropna().unique().tolist())

            # Row 2: Cargo Details
            c5, c6, c7, c8 = st.columns(4)
            cont_1 = c5.text_input("Container-1")
            cont_2 = c6.text_input("Container-2")
            size = c7.selectbox("Size", ["20", "40"])
            status = c8.selectbox("Status", ["MTY", "LDD"])

            # Row 3: Route & Party
            c9, c10, c11, c12 = st.columns(4)
            route_from = c9.text_input("From")
            route_to = c10.text_input("To")
            cycle = c11.text_input("Cycle")
            party = c12.text_input("Party Name")

            # Row 4: Finance & Diesel
            c13, c14, c15, c16 = st.columns(4)
            party_rate = c13.number_input("Party Rate (Income)", min_value=0.0)
            driver_sal = c14.number_input("Driver Salary", min_value=0.0)
            gate_pass = c15.number_input("Gate Pass Charge", min_value=0.0)
            t_status = c16.selectbox("Trip Status", ["Full", "Return"])

            # Row 5: Diesel Details
            c17, c18, c19 = st.columns(3)
            d_type = c17.radio("Diesel Action", ["Usage (Trip)", "Purchase (Stock)"])
            d_liters = c18.number_input("Diesel Liters", min_value=0.0)
            d_rate = c19.number_input("Diesel Rate", min_value=0.0)

            # Auto Calculations
            d_total_amt = d_liters * d_rate
            total_income = party_rate - gate_pass - d_total_amt - driver_sal

            if st.form_submit_button("Save Movement Report"):
                st.write(f"### Final Trip Income: ₹{total_income}")
                st.success("Trip and Diesel entry recorded successfully!")
                st.balloons()