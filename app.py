import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# 1. Setup
st.set_page_config(page_title="Movement Report", layout="wide")

# Google Sheet URL
SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=1114565751"

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL)
        # Date Format Standardization
        df['DATE'] = pd.to_datetime(df['DATE'], dayfirst=True, errors='coerce')
        return df
    except:
        return None

# 2. Sidebar Navigation
st.sidebar.title("Movement Report")
menu = st.sidebar.radio("Menu", ["Dashboard", "Diesel Entry", "Download Report"])

data = load_data()

if data is not None:
    # --- MENU 1: DASHBOARD ---
    if menu == "Dashboard":
        st.header("📈 Diesel Analytics Dashboard")
        
        # Filters for Dashboard
        col1, col2, col3 = st.columns(3)
        
        # Daily Stats
        today = datetime.now().date()
        daily_data = data[data['DATE'].dt.date == today]
        d_used = daily_data.iloc[:, 15].sum() # Col P
        col1.metric("Today's Usage", f"{d_used} L")

        # Monthly Stats
        this_month = datetime.now().month
        monthly_data = data[data['DATE'].dt.month == this_month]
        m_used = monthly_data.iloc[:, 15].sum()
        col2.metric("Monthly Usage", f"{m_used} L")

        # Yearly Stats
        this_year = datetime.now().year
        yearly_data = data[data['DATE'].dt.year == this_year]
        y_used = yearly_data.iloc[:, 15].sum()
        col3.metric("Yearly Usage", f"{y_used} L")
        
        st.divider()
        st.subheader("Recent Movement Logs")
        st.dataframe(data[['DATE', 'VEHICLE NO', 'DRIVER NAME', 'TOTAL DIESEL USED', 'TOTAL DIESEL PURCHASED']].tail(10))

    # --- MENU 2: DIESEL ENTRY (Master Entry Mode) ---
    elif menu == "Diesel Entry":
        st.header("⛽ Bulk Diesel Entry")
        st.info("બધી ગાડીઓની એન્ટ્રી અહિયાંથી એકસાથે કરી શકાશે.")
        
        # Column D (Index 3) માંથી ગાડીઓ લેવી
        vehicles = data.iloc[:, 3].dropna().unique().tolist()
        drivers = data.iloc[:, 5].dropna().unique().tolist() # Col F
        
        entry_list = []
        for v in vehicles:
            with st.expander(f"Entry for {v}"):
                c1, c2, c3 = st.columns(3)
                u = c1.number_input(f"Used (L)", min_value=0.0, key=f"u_{v}")
                p = c2.number_input(f"Purchased (L)", min_value=0.0, key=f"p_{v}")
                dr = c3.selectbox(f"Driver", ["Select"] + drivers, key=f"d_{v}")
                
                if u > 0 or p > 0:
                    entry_list.append({"Vehicle": v, "Used": u, "Purchased": p, "Driver": dr})

        if st.button("Save All Entries"):
            st.success(f"{len(entry_list)} એન્ટ્રી સેવ કરવા માટે તૈયાર છે!")

    # --- MENU 3: DOWNLOAD ---
    elif menu == "Download Report":
        st.header("📥 Export to Excel")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            data.to_excel(writer, index=False, sheet_name='Movement_Report')
        
        st.download_button(
            label="Download Master Excel",
            data=output.getvalue(),
            file_name="Movement_Report_Master.xlsx",
            mime="application/vnd.ms-excel"
        )
else:
    st.error("Connection Failed. Check your URL.")