import os
import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk

from utils import calculate_fee, format_currency

DB_PATH = os.path.join(os.path.dirname(__file__), "parking.db")

# Create a sample record (2 hours ago) and compute fee
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
# Ensure there is at least one slot
cur.execute("CREATE TABLE IF NOT EXISTS slots (slot_id INTEGER PRIMARY KEY AUTOINCREMENT, slot_number TEXT UNIQUE NOT NULL, is_occupied INTEGER DEFAULT 0)")
cur.execute("INSERT OR IGNORE INTO slots (slot_number, is_occupied) VALUES (?,0)", ("Slot-1",))
conn.commit()
# Find a free slot
cur.execute("SELECT slot_id, slot_number FROM slots WHERE is_occupied=0 LIMIT 1")
row = cur.fetchone()
if not row:
    cur.execute("INSERT INTO slots (slot_number, is_occupied) VALUES (?,0)", ("Slot-2",))
    conn.commit()
    cur.execute("SELECT slot_id, slot_number FROM slots WHERE is_occupied=0 LIMIT 1")
    row = cur.fetchone()
slot_id, slot_no = row
# Insert a vehicle parked 2 hours ago
plate = "PUP-12345"
entry_time = (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
try:
    cur.execute("INSERT INTO vehicles (owner_name, vehicle_number, slot_id, entry_time) VALUES (?,?,?,?)", ("Test User", plate, slot_id, entry_time))
    vid = cur.lastrowid
    cur.execute("UPDATE slots SET is_occupied=1 WHERE slot_id=?", (slot_id,))
    conn.commit()
except sqlite3.IntegrityError:
    # vehicle exists; find it
    cur.execute("SELECT vehicle_id, entry_time FROM vehicles WHERE vehicle_number=? AND exit_time IS NULL", (plate,))
    r = cur.fetchone()
    if r:
        vid = r[0]
        entry_time = r[1]
    else:
        # create a new record with timestamp 2 hours ago
        cur.execute("INSERT INTO vehicles (owner_name, vehicle_number, slot_id, entry_time) VALUES (?,?,?,?)", ("Test User", plate+"-NEW", slot_id, entry_time))
        vid = cur.lastrowid
        cur.execute("UPDATE slots SET is_occupied=1 WHERE slot_id=?", (slot_id,))
        conn.commit()

# compute fee using utility
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
minutes, amount = calculate_fee(entry_time, now_str, rate_per_min= (10.0/60.0))
# (rate_per_min set to 10.00 per hour => 10/60 per minute)

conn.close()

# Show receipt window (reuse format from main.show_receipt)
root = tk.Tk()
root.withdraw()
win = tk.Toplevel()
win.title("ParkinUP - Sample Receipt")
win.geometry("420x420")
win.resizable(False, False)
frame = tk.Frame(win, bg="#ffffff", bd=12)
frame.pack(expand=True, fill="both")

title = tk.Label(frame, text="ParkinUP", font=("Segoe UI", 18, "bold"), bg="#ffffff")
title.pack()
subtitle = tk.Label(frame, text="Automated Parking System", font=("Segoe UI", 10), bg="#ffffff")
subtitle.pack()

sep = ttk.Separator(frame, orient="horizontal")
sep.pack(fill="x", pady=8)

body = tk.Frame(frame, bg="#ffffff")
body.pack(fill="both", expand=True, padx=6)
mono = ("Courier", 10)

def row(label_text, value_text):
    r = tk.Frame(body, bg="#ffffff")
    r.pack(fill="x", pady=2)
    tk.Label(r, text=label_text, font=mono, bg="#ffffff").pack(side="left")
    tk.Label(r, text=value_text, font=mono, bg="#ffffff").pack(side="right")

row("Plate Number:", plate)
row("Time-In:", entry_time)
row("Time-Out:", now_str)
if minutes >= 60:
    hrs = minutes // 60
    mins = minutes % 60
    dur_text = f"{hrs} hr {mins} min" if mins else f"{hrs} hr"
else:
    dur_text = f"{minutes} min"
row("Duration:", dur_text)
per_hour = 10.00
row("Rate:", f"{format_currency(per_hour)}/hour")

sep2 = ttk.Separator(body, orient="horizontal")
sep2.pack(fill="x", pady=8)

total_frame = tk.Frame(body, bg="#ffffff")
total_frame.pack(fill="x")
tk.Label(total_frame, text="TOTAL FEE:", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(side="left")
tk.Label(total_frame, text=f"{format_currency(amount)}", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(side="right")

sep3 = ttk.Separator(frame, orient="horizontal")
sep3.pack(fill="x", pady=8)

txn_id = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{vid}"
thank = tk.Label(frame, text="Thank you for parking with us!", font=("Segoe UI", 9), bg="#ffffff")
thank.pack()
tx = tk.Label(frame, text=f"Transaction ID: {txn_id}", font=("Segoe UI", 9), bg="#ffffff")
tx.pack()

btn = tk.Button(frame, text="Close", command=win.destroy, bg="#0b74d1", fg="white", width=12)
btn.pack(pady=10)

win.protocol("WM_DELETE_WINDOW", root.quit)
# show window
root.deiconify()
root.mainloop()
