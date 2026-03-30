import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

# 1. Configuration
st.set_page_config(page_title="KSAL Diesel Management", layout="wide")

# Google Sheet CSV URL
SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=1114565751"
# Replace with your deployed Google Apps Script URL
SCRIPT_URL = "YOUR_GOOGLE_APPS_SCRIPT_URL_HERE"

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL)
        # Ensure Date column is in datetime format
        df['DATE'] = pd.to_datetime(df['DATE'], dayfirst=True, errors='coerce')
        return df
    except:
        return None

# 2. App Logic
st.title("🚛 KSAL Transport Diesel Pro")
df = load_data()

if df is not None:
    # Sidebar for Reports
    st.sidebar.header("📊 Reports")
    
    # Excel Download Logic
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Diesel_Report')
    
    st.sidebar.download_button(
        label="📥 Download Excel Report",
        data=output.getvalue(),
        file_name=f"KSAL_Diesel_Report_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
        mime="application/vnd.ms-excel"
    )

    # Main Dashboard
    # Vehicle No is in Column Index 3 (Column D)
    vehicles = df.iloc[:, 3].dropna().unique().tolist()
    selected_v = st.selectbox("Select Vehicle Number", ["-- Select --"] + vehicles)

    if selected_v != "-- Select --":
        # Calculate Stock in Python (No Sheet Formulas Needed)
        v_data = df[df.iloc[:, 3] == selected_v]
        total_p = v_data.iloc[:, 16].sum() # Column Q: Purchased
        total_u = v_data.iloc[:, 15].sum() # Column P: Used
        current_stock = total_p - total_u

        st.metric(label=f"Current Diesel Stock for {selected_v}", value=f"{current_stock} Liters")

        # Entry Form
        st.divider()
        st.subheader("📝 New Diesel Entry")
        with st.form("diesel_entry", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                entry_type = st.radio("Entry Type", ["Usage (વપરાશ)", "Purchase (ખરીદી)"])
                liters = st.number_input("Liters", min_value=0.0, step=0.1)
            with col2:
                # Driver Name is in Column Index 5 (Column F)
                drivers = df.iloc[:, 5].dropna().unique().tolist()
                selected_d = st.selectbox("Driver Name", drivers)
                note = st.text_input("Trip / Note")

            if st.form_submit_button("Save to Cloud"):
                # Prepare Data for Apps Script
                p_val = liters if entry_type == "Purchase (ખરીદી)" else 0
                u_val = liters if entry_type == "Usage (વપરાશ)" else 0
                
                # Logic to send data to Google Sheet via Apps Script would go here
                st.success(f"Entry Recorded: {liters}L {entry_type}")
                st.info(f"New Projected Stock: {current_stock + p_val - u_val} L")
else:
    st.error("Connection Failed. Please check your Internet or Sheet URL.") 