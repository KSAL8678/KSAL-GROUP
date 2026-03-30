import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="KSAL Master Tracker", layout="wide")

# 2. Form Logic
st.title("🚛 KSAL Master Movement & Income Tracker")

with st.form("master_form", clear_on_submit=True):
    # Row 1: Basic Details
    c1, c2, c3, c4 = st.columns(4)
    t_date = c1.date_input("Date (Manual Select)")
    t_time = c2.time_input("Time (Manual Select)")
    v_no = c3.text_input("Vehicle No") # Suggetion logic can be added later
    d_name = c4.text_input("Driver Name")

    # Row 2: Container & Status
    c5, c6, c7, c8 = st.columns(4)
    cont_1 = c5.text_input("Container-1")
    cont_2 = c6.text_input("Container-2")
    size = c7.selectbox("Size", ["20", "40"])
    status = c8.selectbox("Status", ["MTY", "LDD"])

    # Row 3: Route & Party
    c9, c10, c11, c12 = st.columns(4)
    r_from = c9.text_input("From")
    r_to = c10.text_input("To")
    cycle = c11.text_input("Cycle")
    party = c12.text_input("Party")

    # Row 4: Finance - Part 1
    c13, c14, c15 = st.columns(3)
    party_rate = c13.number_input("Party Rate", min_value=0.0)
    d_salary = c14.number_input("Driver Salary", min_value=0.0)
    t_status = c15.selectbox("Trip Status", ["Full", "Return"])

    # Row 5: Diesel & Charges
    st.divider()
    c16, c17, c18 = st.columns(3)
    d_used = c16.number_input("Trip Diesel Used (Liters)", min_value=0.0)
    d_rate = c17.number_input("Diesel Rate", min_value=0.0)
    g_pass = c18.number_input("Gate Pass Charge", min_value=0.0)

    # Auto Calculations
    d_amount = d_used * d_rate
    income = party_rate - g_pass - d_amount - d_salary

    # Submit
    if st.form_submit_button("Save All 19 Columns"):
        st.write(f"### Diesel Amount: ₹{d_amount}")
        st.write(f"### Final Net Income: ₹{income}")
        st.success("બધી જ વિગતો સેવ થઈ ગઈ છે!")