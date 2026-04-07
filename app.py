import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

# DATABASE
conn = sqlite3.connect("transport.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS movement(
sr INTEGER,
date TEXT,
time TEXT,
vehicle TEXT,
name TEXT,
container1 TEXT,
container2 TEXT,
size TEXT,
status TEXT,
frm TEXT,
to_location TEXT,
cycle TEXT,
party TEXT,
driver_salary INTEGER,
trip_status TEXT,
work_diesel INTEGER,
remarks TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS diesel(
date TEXT,
vehicle TEXT,
issued_diesel INTEGER,
driver TEXT,
rate INTEGER,
amount INTEGER,
pump TEXT,
paid INTEGER
)
""")

conn.commit()

# MAIN WINDOW
root = tk.Tk()
root.title("Transport Management System")
root.geometry("900x600")

# NOTEBOOK TABS
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

dashboard_tab = tk.Frame(notebook)
movement_tab = tk.Frame(notebook)
diesel_tab = tk.Frame(notebook)

notebook.add(dashboard_tab,text="Dashboard")
notebook.add(movement_tab,text="Movement Entry")
notebook.add(diesel_tab,text="Diesel Entry")

# DASHBOARD

tk.Label(dashboard_tab,text="Trip Filter").pack()

trip_filter = ttk.Combobox(dashboard_tab)
trip_filter['values']=("Today Trips","Monthly Trips","Yearly Trips")
trip_filter.pack()

tk.Label(dashboard_tab,text="Vehicle Diesel Stock").pack()

vehicle_stock = ttk.Combobox(dashboard_tab)
vehicle_stock.pack()

# MOVEMENT ENTRY

fields = [
"SR","Date","Time","Vehicle Number","Name","Container1",
"Container2","Size","Status","From","To","Cycle","Party",
"Driver Salary","Trip Status","Work Diesel","Remarks"
]

entries={}

for field in fields:
    frame=tk.Frame(movement_tab)
    frame.pack(fill="x")

    label=tk.Label(frame,text=field,width=15)
    label.pack(side="left")

    entry=tk.Entry(frame)
    entry.pack(side="left",fill="x",expand=True)

    entries[field]=entry

def save_movement():

    data=(
        entries["SR"].get(),
        entries["Date"].get(),
        entries["Time"].get(),
        entries["Vehicle Number"].get(),
        entries["Name"].get(),
        entries["Container1"].get(),
        entries["Container2"].get(),
        entries["Size"].get(),
        entries["Status"].get(),
        entries["From"].get(),
        entries["To"].get(),
        entries["Cycle"].get(),
        entries["Party"].get(),
        entries["Driver Salary"].get(),
        entries["Trip Status"].get(),
        entries["Work Diesel"].get(),
        entries["Remarks"].get()
    )

    cursor.execute("""
    INSERT INTO movement VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,data)

    conn.commit()

    print("Movement Saved")

tk.Button(movement_tab,text="Save Movement",command=save_movement).pack()

# DIESEL ENTRY

diesel_fields=[
"Date","Vehicle","Issued Diesel","Driver","Rate","Pump","Paid Amount"
]

diesel_entries={}

for field in diesel_fields:

    frame=tk.Frame(diesel_tab)
    frame.pack(fill="x")

    label=tk.Label(frame,text=field,width=15)
    label.pack(side="left")

    entry=tk.Entry(frame)
    entry.pack(side="left",fill="x",expand=True)

    diesel_entries[field]=entry

def save_diesel():

    rate=int(diesel_entries["Rate"].get())
    liter=int(diesel_entries["Issued Diesel"].get())

    amount=rate*liter

    data=(
        diesel_entries["Date"].get(),
        diesel_entries["Vehicle"].get(),
        liter,
        diesel_entries["Driver"].get(),
        rate,
        amount,
        diesel_entries["Pump"].get(),
        diesel_entries["Paid Amount"].get()
    )

    cursor.execute("""
    INSERT INTO diesel VALUES (?,?,?,?,?,?,?,?)
    """,data)

    conn.commit()

    print("Diesel Saved")

tk.Button(diesel_tab,text="Save Diesel",command=save_diesel).pack()

root.mainloop()