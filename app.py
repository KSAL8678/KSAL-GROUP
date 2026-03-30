import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="KSAL Transport Management", layout="wide", page_icon="🚛")

# 2. Google Sheet Connection Logic
# Jagatsingh, I have used your specific Sheet ID and GID directly in the link below
SHEET_URL = "https://docs.google.com/spreadsheets/d/1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk/export?format=csv&gid=1114565751"

@st.cache_data(ttl=60)
def load_data_from_google():
    try:
        # Fetching data as CSV directly
        df = pd.read_csv(SHEET_URL)
        return df
    except Exception as e:
        return None

# 3. Session State for Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 4. Login Logic
def login_screen():
    st.title("🚛 KSAL Transport Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == "admin" and password == "jagatsinh@123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Username or Password")

# 5. Main Dashboard
def main_dashboard():
    st.title("Welcome to KSAL Dashboard")
    
    # Try to load data
    df = load_data_from_google()
    
    if df is not None:
        try:
            # Your Sheet2 has Vehicle in Col B (index 1) and Driver in Col C (index 2)
            vehicle_list = df.iloc[:, 1].dropna().unique().tolist()
            driver_list = df.iloc[:, 2].dropna().unique().tolist()

            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("Select Vehicle No", ["Select"] + vehicle_list)
            with col2:
                st.selectbox("Select Driver Name", ["Select"] + driver_list)
                
            st.success("Success: Connection established with Sheet2!")
            
        except Exception as e:
            st.error(f"Error parsing sheet: {e}")
    else:
        # This error is shown in your latest photo
        st.error("Connection Error: Still unable to fetch data. Please double check Google Sheet 'Share' settings.")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Application Entry Point
if not st.session_state.logged_in:
    login_screen()
else:
    main_dashboard()