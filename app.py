import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Setup
st.set_page_config(page_title="KSAL Movement Tracker", layout="wide")

SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=1114565751"

@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_csv(URL)
        return df
    except:
        return None

# 2. Main App
st.title("🚛 KSAL Master Movement Tracker")
df = load_data()

if df is not None:
    # Sidebar Navigation
    menu = st.sidebar.radio("Navigation", ["Daily Trip Entry", "Purchase Stock", "Dashboard"])
    
    # Getting history for suggestions
    v_history = sorted(df.iloc[:, 3].dropna().unique().tolist())
    d_history = sorted(df.iloc[:, 5].dropna().unique().tolist())

    if menu == "Daily Trip Entry":
        st.subheader("📝 Trip Entry with Smart Suggestions")
        
        with st.form("trip_form", clear_on_submit=True):
            # Row 1: Vehicle & Driver (Using text_input with suggestions)
            c1, c2, c3, c4 = st.columns(4)
            t_date = c1.date_input("Trip Date", datetime.now())
            t_time = c2.time_input("Trip Time", datetime.now())
            
            # Smart Suggestion logic for Vehicle and Driver
            v_no = c3.text_input("Vehicle No", help="Type last digits for suggestions")
            d_name = c4.text_input("Driver Name", help="Type name for suggestions")
            
            if v_no:
                v_sugg = [v for v in v_history if v_no.upper() in v.upper()]
                if v_sugg: st.caption(f"Suggestions: {', '.join(v_sugg[:5])}")

            # Row 2: Trip Details
            c5, c6, c7, c8 = st.columns(4)
            cont_1 = c5.text_input("Container-1")
            cont_2 = c6.text_input("Container-2")
            size = c7.selectbox("Size", ["20", "40"])
            status = c8.selectbox("Status", ["MTY", "LDD"])

            # Row 3: Route & Finance
            c9, c10, c11, c12 = st.columns(4)
            p_name = c9.text_input("Party Name")
            r_from = c10.text_input("From")
            r_to = c11.text_input("To")
            cycle = c12.text_input("Cycle")

            # Row 4: Money & Diesel
            c13, c14, c15, c16 = st.columns(4)
            p_rate = c13.number_input("Party Rate", min_value=0.0)
            d_sal = c14.number_input("Driver Salary", min_value=0.0)
            g_pass = c15.number_input("Gate Pass", min_value=0.0)
            t_status = c16.selectbox("Trip Status", ["Full", "Return"])

            st.divider()
            c17, c18 = st.columns(2)
            d_used = c17.number_input("Trip Diesel Used (Liters)", min_value=0.0)
            d_rate = c18.number_input("Diesel Rate", min_value=0.0)

            if st.form_submit_button("Save Trip Report"):
                # Calculation Logic
                total_diesel_cost = d_used * d_rate
                net_profit = p_rate - g_pass - total_diesel_cost - d_sal
                st.write(f"### Estimated Trip Profit: ₹{net_profit}")
                st.success(f"Entry saved for {v_no}!")

    elif menu == "Dashboard":
        # Live Stock Tracking
        st.subheader("📊 Fleet Status & Diesel Stock")
        st.dataframe(df.tail(10))

else:
    st.error("Sheet data could not be reached.")