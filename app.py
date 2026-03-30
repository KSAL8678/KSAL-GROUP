import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="KSAL Transport", layout="wide")

# 2. Connection Settings
# Using your shared sheet ID and Sheet2 GID
SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
GID = "1114565751"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=10)
def load_data():
    try:
        return pd.read_csv(URL)
    except Exception as e:
        return None

# 3. Login State
if 'auth' not in st.session_state:
    st.session_state.auth = False

# 4. Main App
if not st.session_state.auth:
    st.title("🚛 KSAL Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == "admin" and p == "jagatsinh@123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Invalid Login")
else:
    st.title("KSAL Management Dashboard")
    df = load_data()
    if df is not None:
        # Columns B (Vehicle) and C (Driver)
        vehicles = df.iloc[:, 1].dropna().unique().tolist()
        drivers = df.iloc[:, 2].dropna().unique().tolist()
        
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Vehicle Number", ["Select"] + vehicles)
        with c2:
            st.selectbox("Driver Name", ["Select"] + drivers)
        st.success("Connected to Google Sheets!")
    else:
        st.error("Connection Failed. Please check URL.")
    
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()