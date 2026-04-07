import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Transport System", layout="wide")

# ---------------- SESSION ----------------

if "movement" not in st.session_state:
    st.session_state.movement = pd.DataFrame(columns=[
        "SR","Date","Time","Vehicle","Name","Container1","Container2","Size",
        "Status","From","To","Cycle","Party","DriverSalary","TripStatus",
        "WorkDiesel","Remarks"
    ])

if "diesel" not in st.session_state:
    st.session_state.diesel = pd.DataFrame(columns=[
        "Date","Vehicle","IssuedDiesel","Driver","Rate","Amount","Pump","Paid"
    ])

# ---------------- MENU ----------------

menu = st.sidebar.selectbox(
    "MENU",
    ["Dashboard","Movement Entry","Diesel Entry","Diesel Chart"]
)

# ---------------- DASHBOARD ----------------

if menu == "Dashboard":

    st.title("🚛 Transport Dashboard")

    filter_type = st.selectbox(
        "Trip Filter",
        ["Today","Monthly","Yearly"]
    )

    df = st.session_state.movement

    if not df.empty:

        df["Date"] = pd.to_datetime(df["Date"])

        today = datetime.date.today()

        if filter_type == "Today":
            data = df[df["Date"].dt.date == today]

        elif filter_type == "Monthly":
            data = df[df["Date"].dt.month == today.month]

        else:
            data = df[df["Date"].dt.year == today.year]

        st.metric("Total Trips", len(data))

    else:
        st.info("No Data")

# ---------------- MOVEMENT ENTRY ----------------

elif menu == "Movement Entry":

    st.title("Movement Entry")

    with st.form("movement_form"):

        col1,col2,col3 = st.columns(3)

        sr = col1.number_input("SR",step=1)
        date = col2.date_input("Date")
        time = col3.time_input("Time")

        vehicle = st.text_input("Vehicle Number")
        name = st.text_input("Name")

        container1 = st.text_input("Container 1 (11 char)")
        container2 = st.text_input("Container 2")

        size = st.selectbox("Size",["20","40"])

        status = st.selectbox("Status",["MTY","LDD"])

        frm = st.text_input("From")
        to = st.text_input("To")

        cycle = st.text_input("Cycle")
        party = st.text_input("Party")

        # Driver Salary Auto
        if size == "40":
            salary = 200
        else:
            salary = 400

        st.write(f"Driver Salary Auto: {salary}")

        trip_status = st.selectbox("Trip Status",["FULL","RETURN"])

        work_diesel = st.number_input("Work Diesel")

        remarks = st.text_input("Remarks")

        submit = st.form_submit_button("Save")

        if submit:

            if len(container1) != 11:
                st.error("Container1 must be 11 characters")
            else:

                new_row = pd.DataFrame([{
                    "SR":sr,
                    "Date":date,
                    "Time":time,
                    "Vehicle":vehicle,
                    "Name":name,
                    "Container1":container1,
                    "Container2":container2 if size=="40" else "",
                    "Size":size,
                    "Status":status,
                    "From":frm,
                    "To":to,
                    "Cycle":cycle,
                    "Party":party,
                    "DriverSalary":salary,
                    "TripStatus":trip_status,
                    "WorkDiesel":work_diesel,
                    "Remarks":remarks
                }])

                st.session_state.movement = pd.concat(
                    [st.session_state.movement,new_row],
                    ignore_index=True
                )

                st.success("Saved")

    # DELETE OPTION
    st.subheader("Delete Movement")

    df = st.session_state.movement

    if not df.empty:

        idx = st.selectbox("Select Index",df.index)

        if st.button("Delete Movement"):

            st.session_state.movement = df.drop(idx).reset_index(drop=True)

            st.success("Deleted")

        st.dataframe(st.session_state.movement)

# ---------------- DIESEL ENTRY ----------------

elif menu == "Diesel Entry":

    st.title("Diesel Entry")

    with st.form("diesel_form"):

        date = st.date_input("Date")
        vehicle = st.text_input("Vehicle")

        liter = st.number_input("Diesel (Liter)")
        driver = st.text_input("Driver")

        rate = st.number_input("Rate")

        pump = st.text_input("Pump Name")
        paid = st.number_input("Paid Amount")

        submit = st.form_submit_button("Save")

        if submit:

            amount = liter * rate

            new_row = pd.DataFrame([{
                "Date":date,
                "Vehicle":vehicle,
                "IssuedDiesel":liter,
                "Driver":driver,
                "Rate":rate,
                "Amount":amount,
                "Pump":pump,
                "Paid":paid
            }])

            st.session_state.diesel = pd.concat(
                [st.session_state.diesel,new_row],
                ignore_index=True
            )

            st.success("Saved")

    # DELETE
    st.subheader("Delete Diesel Entry")

    df = st.session_state.diesel

    if not df.empty:

        idx = st.selectbox("Select Index",df.index)

        if st.button("Delete Diesel"):

            st.session_state.diesel = df.drop(idx).reset_index(drop=True)

            st.success("Deleted")

        st.dataframe(st.session_state.diesel)

# ---------------- DIESEL CHART ----------------

elif menu == "Diesel Chart":

    st.title("Diesel Chart")

    d = st.session_state.diesel
    m = st.session_state.movement

    total = d["IssuedDiesel"].sum() if not d.empty else 0
    used = m["WorkDiesel"].sum() if not m.empty else 0

    balance = total - used

    c1,c2,c3 = st.columns(3)

    c1.metric("Total Diesel",total)
    c2.metric("Used Diesel",used)
    c3.metric("Balance",balance)

    st.subheader("Vehicle Wise")

    if not d.empty:

        v = d.groupby("Vehicle")["IssuedDiesel"].sum().reset_index()

        st.dataframe(v)