import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd

# Page Config
st.set_page_config(page_title="KSAL Transport Management", layout="wide")

# Connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Authentication logic
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🚚 KSAL Transport Login")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and password == "jagatsinh@123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Username or Password")
else:
    st.sidebar.title("Menu")
    page = st.sidebar.radio("Select Page", ["Dashboard", "New Trip Entry"])

    # Read existing data
    df = conn.read()
    if not df.empty:
        df['DATE'] = pd.to_datetime(df['DATE'])

    if page == "Dashboard":
        st.title("📊 Monthly Reports")
        if not df.empty:
            # 12. Auto-sorting: Date Old to New
            sorted_df = df.sort_values(by='DATE', ascending=True)
            st.dataframe(sorted_df, use_container_width=True)
        else:
            st.warning("No data found.")

    elif page == "New Trip Entry":
        st.title("📝 Register New Trip")
        
        # 1. Automatic SR Number
        next_sr = len(df) + 1 if not df.empty else 1

        with st.form("entry_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"Auto SR No: {next_sr}")
                date = st.date_input("Trip Date")
                vehicle_no = st.text_input("VEHICLE NO")
                driver_name = st.text_input("DRIVER NAME")
                size = st.selectbox("SIZE", ["20 FT", "40 FT"])
                
                # 3. Double Container for 20 FT
                cont1 = st.text_input("CONTAINER-1 (11 Chars)")
                cont2 = ""
                if size == "20 FT":
                    cont2 = st.text_input("CONTAINER-2 (Optional)")
            
            with col2:
                # 13. Trip Status Dropdown
                status = st.selectbox("STATUS", ["Full Trip", "Return Trip"])
                loc_from = st.text_input("FROM")
                loc_to = st.text_input("TO")
                party = st.text_input("PARTY")
                diesel = st.number_input("DRIVERSAL (Diesel)", min_value=0.0)
                # Extra field for Cycle if needed
                cycle = st.text_input("CYCLE")

            submit = st.form_submit_button("Save Trip")

            if submit:
                # 2. Container Validation
                if len(cont1) != 11:
                    st.error("Error: CONTAINER-1 must be exactly 11 characters!")
                else:
                    new_data = pd.DataFrame([{
                        "SR": next_sr,
                        "DATE": date.strftime('%Y-%m-%d'),
                        "VEHICLE NO": vehicle_no.upper(),
                        "DRIVER NAME": driver_name,
                        "CONTAINER-1": cont1.upper(),
                        "CONTAINER-2": cont2.upper() if cont2 else "",
                        "SIZE": size,
                        "STATUS": status,
                        "FROM": loc_from,
                        "TO": loc_to,
                        "CYCLE": cycle,
                        "PARTY": party,
                        "DRIVERSAL": diesel
                    }])
                    
                    # Merge, Sort and Update
                    updated_df = pd.concat([df, new_data], ignore_index=True)
                    updated_df['DATE'] = pd.to_datetime(updated_df['DATE'])
                    updated_df = updated_df.sort_values(by='DATE', ascending=True)
                    updated_df['SR'] = range(1, len(updated_df) + 1)
                    
                    conn.update(data=updated_df)
                    st.success("Trip saved in CONTAINER-1 & CONTAINER-2 columns!")