import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="KSAL Transport Management", layout="wide", page_icon="🚛")

# 2. Correct Google Sheet Parameters
# Your Sheet ID from the link provided
SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
# GID for Sheet2 is 1114565751 as seen in your previous screenshots
GID = "1114565751"

# Constructing the stable export URL
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60)
def load_data():
    try:
        # Fetching CSV data from Google Sheets
        df = pd.read_csv(SHEET_URL)
        return df
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# 3. Login Logic
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.title("🚛 KSAL Transport Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "jagatsinh@123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Username or Password")

# 4. Main Dashboard
def main_dashboard():
    st.title("Welcome to KSAL Dashboard")
    
    df = load_data()
    
    if df is not None:
        try:
            # Using column index to avoid header mismatch (B=1, C=2)
            # Based on your Sheet2 screenshot
            vehicles = df.iloc[:, 1].dropna().unique().tolist()
            drivers = df.iloc[:, 2].dropna().unique().tolist()

            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("Select Vehicle No", ["Select"] + vehicles)
            with col2:
                st.selectbox("Select Driver Name", ["Select"] + drivers)

            st.success("Master data loaded from Sheet2 successfully!")
            
        except Exception as e:
            st.warning("Data format error. Please ensure Sheet2 has columns B and C filled.")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Logic to switch screens
if not st.session_state.logged_in:
    login_page()
else:
    main_dashboard()