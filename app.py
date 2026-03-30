import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="KSAL Transport Management", layout="wide", page_icon="🚛")

# 2. Simplified Google Sheet URL
# Jagatsingh, I am using a very simple version of your link now
SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
# fetching only Sheet2 via gid
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1114565751"

@st.cache_data(ttl=10) # Reduced cache time to see updates faster
def load_data():
    try:
        # Fetching data using simple pandas read
        return pd.read_csv(SHEET_URL)
    except Exception as e:
        return None

# 3. Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 4. Main App
def main_dashboard():
    st.title("Welcome to KSAL Dashboard")
    
    df = load_data()
    
    if df is not None:
        try:
            # Your Sheet2 data starts from row 1
            # Vehicle in Col B (index 1), Driver in Col C (index 2)
            vehicle_list = df.iloc[:, 1].dropna().unique().tolist()
            driver_list = df.iloc[:, 2].dropna().unique().tolist()

            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("Select Vehicle No", ["Choose Vehicle"] + vehicle_list)
            with col2:
                st.selectbox("Select Driver Name", ["Choose Driver"] + driver_list)
            
            st.success("Successfully connected to Sheet2!")
        except Exception as e:
            st.error("Error reading columns. Make sure Sheet2 has data.")
    else:
        st.error("Connection Error: Still failing to get data. Please verify 'Anyone with link' setting.")

# 5. Login
def login_screen():
    st.title("🚛 KSAL Transport Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == "admin" and p == "jagatsinh@123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials.")

if not st.session_state.logged_in:
    login_screen()
else:
    main_dashboard()