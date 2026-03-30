import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="KSAL Transport", layout="wide")

# 2. Connection Settings
# I have simplified the URL to avoid 400 errors
SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
# Direct Export URL
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=1114565751"

@st.cache_data(ttl=5)
def load_data():
    try:
        # Fetching data directly
        df = pd.read_csv(URL)
        return df
    except Exception as e:
        return None

# 3. Auth Logic
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🚛 KSAL Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == "admin" and p == "jagatsinh@123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Invalid credentials")
else:
    st.title("KSAL Management Dashboard")
    
    data = load_data()
    
    if data is not None:
        try:
            # Picking Vehicle (Col 2) and Driver (Col 3) from your Sheet2
            vehicles = data.iloc[:, 1].dropna().unique().tolist()
            drivers = data.iloc[:, 2].dropna().unique().tolist()
            
            c1, c2 = st.columns(2)
            with c1:
                st.selectbox("Select Vehicle", ["Select"] + vehicles)
            with c2:
                st.selectbox("Select Driver", ["Select"] + drivers)
            
            st.success("Successfully Connected to Sheet2!")
        except Exception:
            st.error("Could not find columns. Please check Sheet2 data.")
    else:
        # Shown in your photo
        st.error("Still unable to connect. Trying a different method...")
        st.info("Check if your internet is stable and GitHub is updated.")

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()