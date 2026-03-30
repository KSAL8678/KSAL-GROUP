import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="KSAL Transport Management", layout="wide")

# 2. Google Sheet Connection for Sheet2
# Change the gid to match your Sheet2 (usually gid=Sheet2 ID)
sheet_id = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
# Added 'gid' to specifically target Sheet2
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1114565751"

@st.cache_data(ttl=60)
def load_data():
    # Load Sheet2 data and skip the first empty column if needed
    df = pd.read_csv(sheet_url)
    return df

# 3. Login Logic
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🚛 KSAL Transport Login")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and password == "jagatsinh@123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Login")
else:
    st.title("Main Dashboard - KSAL")
    
    try:
        df = load_data()
        
        # Mapping columns based on your sheet
        # B is typically 'Unnamed: 1' and C is 'Unnamed: 2' in raw CSV if headers are missing
        # Let's use column index to be safe
        vehicles = df.iloc[:, 1].dropna().unique().tolist() # Column B
        drivers = df.iloc[:, 2].dropna().unique().tolist()  # Column C

        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("ગાડી નંબર પસંદ કરો (Vehicle)", vehicles)
        with col2:
            st.selectbox("ડ્રાઈવરનું નામ પસંદ કરો (Driver)", drivers)
            
        st.divider()
        st.subheader("નવી ટ્રીપ એન્ટ્રી")
        # Add entry fields here
        
    except Exception as e:
        st.error(f"Error: {e}. Please check Sheet2 gid and sharing settings.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()