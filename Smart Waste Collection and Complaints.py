# --- Smart Waste Collection and Complaint System ---
# Streamlit app with Citizen, Admin, and Collector roles

import streamlit as st
import os
import sqlite3
import datetime
from PIL import Image

# --- Setup ---
st.set_page_config(page_title="Smart Waste System", layout="wide")
os.makedirs("data", exist_ok=True)
DB_PATH = "data/complaints.db"

# --- DB Init ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        complaint TEXT,
        photo_path TEXT,
        location TEXT,
        type TEXT,
        status TEXT,
        date TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# --- Sidebar Menu ---
menu = st.sidebar.selectbox("Select Role", ["Citizen", "Admin", "Collector"])

# --- Citizen ---
if menu == "Citizen":
    st.header("🙋 Citizen - Report Waste Problem")
    name = st.text_input("Your Name")
    complaint = st.text_area("Describe the Problem")
    photo = st.file_uploader("Upload a Photo", type=["jpg", "jpeg", "png"])
    location = st.text_input("Paste Google Maps Location Link")
    waste_type = st.selectbox("Type of Waste", ["Recyclable Waste", "General Waste", "Hazardous Waste"])

    if st.button("Submit Complaint"):
        if name and complaint and location:
            photo_path = ""
            if photo:
                photo_path = f"data/{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{photo.name}"
                with open(photo_path, "wb") as f:
                    f.write(photo.read())

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO complaints (user, complaint, photo_path, location, type, status, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (name, complaint, photo_path, location, waste_type, "Pending", str(datetime.datetime.now())))
            conn.commit()
            conn.close()
            st.success("✅ Complaint submitted successfully!")
        else:
            st.error("Please fill in all required fields.")

# --- Admin ---
elif menu == "Admin":
    st.header("🧑‍💼 Admin Dashboard")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM complaints")
    complaints = c.fetchall()

    if complaints:
        for row in complaints:
            st.markdown(f"### ID: {row[0]} | User: {row[1]} | Type: {row[5]} | Status: {row[6]}")
            st.markdown(f"📝 {row[2]}")
            if row[3]:
                st.image(row[3], width=200)
            st.markdown(f"📍 [View Location]({row[4]})")

            new_status = st.selectbox("Update status for Complaint #{}".format(row[0]), ["Pending", "In Progress", "Resolved"], index=["Pending", "In Progress", "Resolved"].index(row[6]), key=f"status_{row[0]}")
            if st.button(f"Update Complaint #{row[0]}"):
                c.execute("UPDATE complaints SET status = ? WHERE id = ?", (new_status, row[0]))
                conn.commit()
                st.success(f"Complaint #{row[0]} status updated to {new_status}")
    else:
        st.info("No complaints yet.")
    conn.close()

# --- Collector ---
elif menu == "Collector":
    st.header("🚛 Collector Panel")
    collector_name = st.text_input("Enter Collector Name")

    if collector_name:
        st.subheader("📋 Assigned Complaints (In Progress)")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM complaints WHERE status = 'In Progress'")
        rows = c.fetchall()
        conn.close()

        if rows:
            for row in rows:
                st.markdown(f"**ID:** {row[0]} | **Type:** {row[5]} | **Status:** {row[6]}")
                st.markdown(f"📝 {row[2]}")
                if row[3]:
                    st.image(row[3], width=200)
                st.markdown(f"📍 [View Location]({row[4]})")

                completion_photo = st.file_uploader(f"Upload Completion Photo for #{row[0]}", type=["jpg", "png", "jpeg"], key=f"photo_{row[0]}")
                if st.button(f"Mark as Collected ✅ (ID {row[0]})", key=f"collect_{row[0]}"):
                    if completion_photo:
                        completion_path = f"data/collector_{row[0]}_{completion_photo.name}"
                        with open(completion_path, "wb") as f:
                            f.write(completion_photo.read())
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("UPDATE complaints SET status = 'Resolved' WHERE id = ?", (row[0],))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Complaint #{row[0]} marked as collected by {collector_name}.")
        else:
            st.info("No pending collection tasks right now.")