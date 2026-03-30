import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="KSAL Transport Management", layout="wide", page_icon="🚛")

# 2. Google Sheet Connection Settings
# Your Google Sheet ID and Sheet2 GID
SHEET_ID = "1F0fWEZSmOjC5it_q0ew_hulVPVzEHwdgpVvEKaT0ndk"
SHEET2_GID = "1114565751"

# Constructing the CSV Export URL
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET2_GID}"

@st.cache_data(ttl=60)
def load_sheet_data():
    try:
        # Loading data from the specific Sheet2
        df = pd.read_csv(SHEET_URL)
        return df
    except Exception as e:
        st.error(f"Error: Could not connect to Google Sheet. {e}")
        return None

# 3. Session State for Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 4. Login Function
def login_screen():
    st.title("🚛 KSAL Transport Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == "admin" and password == "jagatsinh@123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")

# 5. Main Application Dashboard
def main_dashboard():
    st.title("Welcome to KSAL Dashboard")
    st.sidebar.title("Navigation")
    
    # Load Master Data from Sheet2
    df = load_sheet_data()
    
    if df is not None:
        try:
            # Getting data from Column B (Vehicle) and Column C (Driver)
            # Using iloc to avoid header name issues
            vehicle_list = df.iloc[:, 1].dropna().unique().tolist()
            driver_list = df.iloc[:, 2].dropna().unique().tolist()

            col1, col2 = st.columns(2)
            
            with col1:
                selected_v = st.selectbox("Select Vehicle No", ["Select"] + vehicle_list)
            
            with col2:
                selected_d = st.selectbox("Select Driver Name", ["Select"] + driver_list)

            st.divider()

            if selected_v != "Select" and selected_d != "Select":
                st.success(f"Selected: {selected_v} | Driver: {selected_d}")
                
                # Placeholder for Trip Entry
                st.subheader("New Trip Entry")
                route = st.text_input("Route (From - To)")
                diesel = st.number_input("Diesel (Liters)", min_value=0.0)
                amount = st.number_input("Amount (INR)", min_value=0)
                
                if st.button("Save Trip Details"):
                    st.info("Saving feature will be added in the next step.")

        except Exception as e:
            st.warning("Data format error. Please check Sheet2 structure.")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Logic to switch between Login and Dashboard
if not st.session_state.logged_in:
    login_screen()
else:
    main_dashboard()