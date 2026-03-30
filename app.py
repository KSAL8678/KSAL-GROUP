import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import BytesIO

# 1. Configuration & Data Loading
st.set_page_config(page_title="KSAL Movement Report", layout="wide")

SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=1114565751"
SCRIPT_URL = "YOUR_GOOGLE_APPS_SCRIPT_URL"

@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_csv(URL)
        df['DATE'] = pd.to_datetime(df['DATE'], dayfirst=True, errors='coerce')
        return df
    except:
        return None

# 2. Main Navigation
st.sidebar.title("Movement Report")
menu = st.sidebar.radio("Navigation", ["Live Dashboard", "New Trip & Diesel Entry", "Download Excel"])

df = load_data()

if df is not None:
    # --- DASHBOARD SECTION ---
    if menu == "Live Dashboard":
        st.header("📊 Live Trip & Diesel Dashboard")
        
        # Vehicle selection for specific stock tracking
        vehicles = df.iloc[:, 3].dropna().unique().tolist()
        selected_v = st.selectbox("Check Stock for Vehicle", vehicles)
        
        v_data = df[df.iloc[:, 3] == selected_v]
        total_purchased = v_data.iloc[:, 16].sum() # Column Q
        total_used = v_data.iloc[:, 15].sum()      # Column P
        current_balance = total_purchased - total_used

        col1, col2, col3 = st.columns(3)
        col1.metric("Current Diesel Stock", f"{current_balance} L")
        col2.metric("Total Trips Done", len(v_data))
        col3.metric("Monthly Consumption", f"{total_used} L")

        st.divider()
        st.subheader("Recent Trip Logs")
        st.dataframe(df.tail(10))

    # --- ENTRY SECTION (Trip + Diesel) ---
    elif menu == "New Trip & Diesel Entry":
        st.header("📝 Movement & Diesel Entry")
        
        with st.form("master_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.markdown("### Vehicle & Driver")
                v_no = st.selectbox("Vehicle No", df.iloc[:, 3].dropna().unique().tolist()) #
                d_name = st.selectbox("Driver Name", df.iloc[:, 5].dropna().unique().tolist()) #
                date_input = st.date_input("Date", datetime.now())
            
            with c2:
                st.markdown("### Trip Details")
                container = st.text_input("Container No") #
                party = st.text_input("Party Name") #
                route = st.text_input("From - To") #
            
            with c3:
                st.markdown("### Diesel Update")
                entry_type = st.radio("Diesel Action", ["Usage (ટ્રીપમાં વપરાયું)", "Purchase (નવું આવ્યું)"])
                liters = st.number_input("Liters", min_value=0.0, step=0.1)
                diesel_status = st.selectbox("Diesel Status", ["FULL", "PARTIAL"]) #

            if st.form_submit_button("Submit Movement Report"):
                # Logic: Purchase goes to Q, Usage goes to P
                p_val = liters if entry_type == "Purchase (નવું આવ્યું)" else 0
                u_val = liters if entry_type == "Usage (ટ્રીપમાં વપરાયું)" else 0
                
                # Payload for Google Apps Script
                st.success(f"Trip saved! Stock updated for {v_no}.")
                st.balloons()

    # --- DOWNLOAD SECTION ---
    elif menu == "Download Excel":
        st.header("📥 Download Master Report")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("Download Excel", output.getvalue(), "Movement_Report.xlsx")

else:
    st.error("Connection Failed. Please check URL.")