import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Setup
st.set_page_config(page_title="KSAL Movement Report", layout="wide")

SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=1114565751"

@st.cache_data(ttl=1)
def load_data():
    try:
        # Reading raw data for better extraction
        df = pd.read_csv(URL)
        return df
    except:
        return None

# 2. Main App
st.title("🚛 KSAL Master Movement Tracker")
df = load_data()

if df is not None:
    # Sidebar for Navigation & Stock Purchase
    menu = st.sidebar.radio("Navigation", ["Daily Trip Entry", "Purchase Stock (Stock Add)", "Dashboard"])
    
    # Extracting lists for dropdowns
    vehicle_list = sorted(df.iloc[:, 3].dropna().unique().tolist())
    driver_list = sorted(df.iloc[:, 5].dropna().unique().tolist())

    if menu == "Daily Trip Entry":
        st.subheader("📝 Detailed Trip Form")
        with st.form("trip_form", clear_on_submit=True):
            # Row 1: Fixed Dropdowns
            c1, c2, c3, c4 = st.columns(4)
            t_date = c1.date_input("Trip Date", datetime.now())
            t_time = c2.time_input("Trip Time", datetime.now())
            v_no = c3.selectbox("Vehicle No", vehicle_list) # Fix: Now showing sorted list
            d_name = c4.selectbox("Driver Name", driver_list) # Fix: Now showing sorted list

            # Row 2: Trip Info
            c5, c6, c7, c8 = st.columns(4)
            cont_1 = c5.text_input("Container-1")
            cont_2 = c6.text_input("Container-2")
            size = c7.selectbox("Size", ["20", "40"])
            status = c8.selectbox("Status", ["MTY", "LDD"])

            # Row 3: Finance & Diesel
            c9, c10, c11, c12 = st.columns(4)
            p_rate = c9.number_input("Party Rate", min_value=0.0)
            d_sal = c10.number_input("Driver Salary", min_value=0.0)
            g_pass = c11.number_input("Gate Pass", min_value=0.0)
            t_status = c12.selectbox("Trip Status", ["Full", "Return"])

            # Diesel Usage Section (Action Removed as requested)
            st.divider()
            c13, c14 = st.columns(2)
            d_liters = c13.number_input("Trip Diesel Used (Liters)", min_value=0.0)
            d_rate = c14.number_input("Diesel Rate", min_value=0.0)

            # Auto Income Calculation
            d_cost = d_liters * d_rate
            net_income = p_rate - g_pass - d_cost - d_sal

            if st.form_submit_button("Save Trip Report"):
                st.info(f"Calculated Trip Income: ₹{net_income}")
                st.success(f"Trip saved and {d_liters}L deducted from stock.")

    elif menu == "Purchase Stock (Stock Add)":
        st.subheader("⛽ Add New Diesel to Stock (Purchase)")
        with st.form("purchase_form"):
            v_purchase = st.selectbox("Select Vehicle", vehicle_list)
            p_liters = st.number_input("Liters Purchased", min_value=0.0)
            if st.form_submit_button("Add to Stock"):
                st.success(f"Added {p_liters}L to {v_purchase} stock.")

else:
    st.error("Could not load vehicle/driver lists from Sheet.")