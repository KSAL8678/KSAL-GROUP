import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="KSAL Transport Management", layout="wide", page_icon="🚛")

# 2. Google Sheet Settings (Direct Access)
# Using the sheet ID and GID you provided
SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
SHEET2_GID = "1114565751"

# Construction of the export URL
# This specific format is most stable for public sheets
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET2_GID}"

@st.cache_data(ttl=60)
def load_sheet_data():
    try:
        # Fetching data using pandas
        return pd.read_csv(SHEET_URL)
    except Exception as e:
        return None

# 3. Session State for Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 4. Dashboard Logic
def main_dashboard():
    st.title("Welcome to KSAL Dashboard")
    
    df = load_sheet_data()
    
    if df is not None:
        try:
            # According to your screenshot: Column B is Vehicle, Column C is Driver
            # We use iloc to pick columns by position to avoid header naming issues
            vehicle_list = df.iloc[:, 1].dropna().unique().tolist()
            driver_list = df.iloc[:, 2].dropna().unique().tolist()

            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("Select Vehicle No", ["Select"] + vehicle_list)
            with col2:
                st.selectbox("Select Driver Name", ["Select"] + driver_list)
            
            st.success("Data successfully loaded from Google Sheet!")
            
        except Exception as e:
            st.error("Sheet format error. Please check Column B and C in Sheet2.")
    else:
        st.error("Connection Error: Please check if Google Sheet is shared 'Anyone with link'.")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# 5. Login Logic
def login_screen():
    st.title("🚛 KSAL Transport Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "jagatsinh@123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Username or Password")

# Execution
if not st.session_state.logged_in:
    login_screen()
else:
    main_dashboard()