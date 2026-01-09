import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
from types import ModuleType
from typing import Any, Optional, Protocol, cast
from ui import create_homepage, create_login_page, COLORS, FONTS, show_parking_slots_overview

# --------- Database path (same folder) ----------
DB_PATH = os.path.join(os.path.dirname(__file__), "parking.db")

# --------- DB helper functions ----------
def get_connection():
    return sqlite3.connect(DB_PATH)

def ensure_tables_exist():
    """Create minimal tables if not exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS slots (
        slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
        slot_number TEXT UNIQUE NOT NULL,
        is_occupied INTEGER DEFAULT 0
    );""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_name TEXT,
        vehicle_number TEXT UNIQUE,
        slot_id INTEGER,
        entry_time TEXT,
        exit_time TEXT,
        FOREIGN KEY(slot_id) REFERENCES slots(slot_id)
    );""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER,
        amount REAL,
        payment_time TEXT,
        FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id)
    );""")
    conn.commit()
    conn.close()

# Ensure DB ready
ensure_tables_exist()
from utils import init_db, calculate_fee, format_currency, ocr_stub
# Seed a small default set of slots if the DB has none
init_db(DB_PATH, total_slots=20)

# Optional camera / OCR libs (safe imports)
cv2: Optional[ModuleType] = None
try:
    import cv2
except ImportError:
    pass

CAMERA_LIB: bool = cv2 is not None

class _PILImageObject(Protocol):
    def resize(self, size: tuple[int, int]):
        ...

class _PILImageModule(Protocol):
    def fromarray(self, obj: Any) -> _PILImageObject:
        ...

class _PILImageTkModule(Protocol):
    PhotoImage: type[Any]

Image: _PILImageModule | None = None
ImageTk: _PILImageTkModule | None = None
PIL_AVAILABLE: bool = False

try:
    from PIL import Image as _PIL_Image
    from PIL import ImageTk as _PIL_ImageTk
except ImportError:
    pass
else:
    Image = cast(_PILImageModule, _PIL_Image)
    ImageTk = cast(_PILImageTkModule, _PIL_ImageTk)
    PIL_AVAILABLE = True

# Optional OCR lib
pytesseract: Optional[ModuleType] = None
try:
    import pytesseract
except ImportError:
    pass

PYTESSERACT_AVAILABLE: bool = pytesseract is not None

# Camera state (optional)
cam = None
cam_frame = None
cam_label = None

def start_camera():
    global cam
    if cv2 is None:
        return
    if cam is None:
        cam = cv2.VideoCapture(0)
    update_camera()

def stop_camera():
    global cam
    if cam is not None:
        try:
            cam.release()
        except Exception:
            pass
        cam = None

def update_camera():
    global cam, cam_frame, cam_label
    if cam is None:
        return
    ret, frame = cam.read()
    if not ret:
        root.after(200, update_camera)
        return
    cam_frame = frame.copy()
    if PIL_AVAILABLE and cv2 is not None and Image is not None and ImageTk is not None:
        try:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            # Dynamically resize based on cam_label size, maintaining 16:9 aspect ratio
            if cam_label and cam_label.winfo_exists():
                width = cam_label.winfo_width()
                height = cam_label.winfo_height()
                if width > 1 and height > 1:
                    # Maintain 16:9 aspect ratio within the label dimensions
                    target_ratio = 16 / 9
                    if width / height > target_ratio:
                        new_height = height
                        new_width = int(height * target_ratio)
                    else:
                        new_width = width
                        new_height = int(width / target_ratio)
                    img = img.resize((new_width, new_height))
                else:
                    img = img.resize((1000, 562))
            else:
                img = img.resize((1000, 562))
            imgtk = ImageTk.PhotoImage(img)
            try:
                if cam_label and cam_label.winfo_exists():
                    cam_label.config(image=imgtk)
                    cam_label.image = imgtk
            except Exception:
                pass
        except Exception:
            pass
    root.after(30, update_camera)

# --------- GUI root ----------
root = tk.Tk()
root.title("ParkinUP - Automated Parking System")
root.geometry("1200x800")
root.minsize(1000, 700)
root.resizable(True, True)

# Set window icon
if PIL_AVAILABLE:
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "favicon.png")
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path)
            icon_photo = ImageTk.PhotoImage(icon_img)
            root.iconphoto(True, icon_photo)
    except Exception as e:
        print(f"Error loading window icon: {e}")

# Application state
app_state = {
    'current_page': 'home',
    'is_logged_in': False,
    'sidebar_open': True
}

# Page navigation functions
def navigate_to(page):
    """Navigate to different pages."""
    app_state['current_page'] = page
    
    if page == 'home':
        create_homepage(root, on_start_now=show_login, on_learn_more=show_learn_more_dialog)
    elif page == 'login':
        create_login_page(root, on_login=show_dashboard, on_back=navigate_home)
    elif page == 'dashboard':
        if app_state['is_logged_in']:
            show_dashboard()
        else:
            show_login()

def navigate_home():
    navigate_to('home')

def show_learn_more_dialog():
    messagebox.showinfo("Learn More", "ParkInUP is an automated parking system that uses license plate recognition to manage parking efficiently. Features include real-time tracking, automatic fee calculation, and more.")

def show_login():
    navigate_to('login')

def show_dashboard():
    """Shows the dashboard after login."""
    app_state['is_logged_in'] = True
    app_state['current_page'] = 'dashboard'
    
    # Clear any existing widgets
    for widget in root.winfo_children():
        widget.destroy()
    
    root.configure(bg=COLORS['gray_50'])
    setup_dashboard()


def create_navigation_bar():
    """Create the navigation bar for the dashboard."""
    nav_frame = tk.Frame(root, bg=COLORS['white'], height=80)
    nav_frame.pack(fill="x", side="top")
    nav_frame.pack_propagate(False)

    # Logo
    logo_container = tk.Frame(nav_frame, bg=COLORS['white'], height=80)
    logo_container.pack(side="left", padx=20)
    logo_container.pack_propagate(False)

    def on_logo_click():
        if messagebox.askyesno("Logout", "Do you want to logout and return to home?"):
            app_state['is_logged_in'] = False
            navigate_to('home')

    logo_frame = tk.Frame(logo_container, bg=COLORS['white'], cursor="hand2")
    logo_frame.pack(side="left", padx=5, pady=10)
    logo_frame.bind("<Button-1>", lambda e: on_logo_click())

    if PIL_AVAILABLE:
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "docs", "logo.png")
            if not os.path.exists(logo_path):
                 logo_path = os.path.join(os.path.dirname(__file__), "docs", "logo.png")
            
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((160, 60), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(logo_frame, image=logo_photo, bg=COLORS['white'], cursor="hand2")
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack()
            logo_label.bind("<Button-1>", lambda e: on_logo_click())
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback to text
            p_label = tk.Label(logo_frame, text="P", font=('Segoe UI', 20, 'bold'),
                              fg=COLORS['yellow_500'], bg=COLORS['white'],
                              cursor="hand2")
            p_label.pack(side="left")
            p_label.bind("<Button-1>", lambda e: on_logo_click())

            car_label = tk.Label(logo_frame, text="🚗", font=('Segoe UI', 16), bg=COLORS['white'],
                                cursor="hand2")
            car_label.pack(side="left")
            car_label.bind("<Button-1>", lambda e: on_logo_click())

            arkin_label = tk.Label(logo_frame, text="arkin", font=('Segoe UI', 20, 'bold'),
                                  fg=COLORS['red_600'], bg=COLORS['white'],
                                  cursor="hand2")
            arkin_label.pack(side="left")
            arkin_label.bind("<Button-1>", lambda e: on_logo_click())

            bike_label = tk.Label(logo_frame, text="🚲", font=('Segoe UI', 16), bg=COLORS['white'],
                                cursor="hand2")
            bike_label.pack(side="left")
            bike_label.bind("<Button-1>", lambda e: on_logo_click())

            up_label = tk.Label(logo_frame, text="UP", font=('Segoe UI', 20, 'bold'),
                               fg=COLORS['yellow_500'], bg=COLORS['white'],
                               cursor="hand2")
            up_label.pack(side="left")
            up_label.bind("<Button-1>", lambda e: on_logo_click())
    else:
        # Fallback to text
        p_label = tk.Label(logo_frame, text="P", font=('Segoe UI', 20, 'bold'),
                          fg=COLORS['yellow_500'], bg=COLORS['white'],
                          cursor="hand2")
        p_label.pack(side="left")
        p_label.bind("<Button-1>", lambda e: on_logo_click())

        car_label = tk.Label(logo_frame, text="🚗", font=('Segoe UI', 16), bg=COLORS['white'],
                            cursor="hand2")
        car_label.pack(side="left")
        car_label.bind("<Button-1>", lambda e: on_logo_click())

        arkin_label = tk.Label(logo_frame, text="arkin", font=('Segoe UI', 20, 'bold'),
                              fg=COLORS['red_600'], bg=COLORS['white'],
                              cursor="hand2")
        arkin_label.pack(side="left")
        arkin_label.bind("<Button-1>", lambda e: on_logo_click())

        bike_label = tk.Label(logo_frame, text="🚲", font=('Segoe UI', 16), bg=COLORS['white'],
                            cursor="hand2")
        bike_label.pack(side="left")
        bike_label.bind("<Button-1>", lambda e: on_logo_click())

        up_label = tk.Label(logo_frame, text="UP", font=('Segoe UI', 20, 'bold'),
                           fg=COLORS['yellow_500'], bg=COLORS['white'],
                           cursor="hand2")
        up_label.pack(side="left")
        up_label.bind("<Button-1>", lambda e: on_logo_click())

    # Navigation items
    nav_items_frame = tk.Frame(nav_frame, bg=COLORS['white'], height=60)
    nav_items_frame.pack(side="right", padx=20)
    nav_items_frame.pack_propagate(False)

    nav_buttons = [
        ("📊 Dashboard", None),
        ("🚘 Vehicles", lambda: vehicles_window()),
        ("💰 Payments", lambda: payments_window()),
        ("📍 Slots", lambda: open_parking_overview()),
    ]

    for text, command in nav_buttons:
        if command:
            btn = tk.Button(nav_items_frame, text=text, command=command,
                           bg=COLORS['white'], fg=COLORS['gray_700'],
                           font=FONTS['button'], relief='flat', bd=0, padx=15)
            btn.pack(side="left", padx=5, pady=18)
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=COLORS['red_600']))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg=COLORS['gray_700']))
        else:
            # Dashboard button (current page)
            btn = tk.Button(nav_items_frame, text=text,
                           bg=COLORS['white'], fg=COLORS['red_600'],
                           font=('Segoe UI', 12, 'bold'), relief='flat', bd=0, padx=15)
            btn.pack(side="left", padx=5, pady=18)

    # Logout button
    def on_logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            app_state['is_logged_in'] = False
            navigate_to('home')

    logout_btn = tk.Button(nav_items_frame, text="🚪 Logout", command=on_logout,
                          bg=COLORS['white'], fg=COLORS['gray_700'],
                          font=FONTS['button'], relief='flat', bd=0, padx=15)
    logout_btn.pack(side="left", padx=5, pady=18)
    logout_btn.bind("<Enter>", lambda e, b=logout_btn: b.config(fg=COLORS['red_600']))
    logout_btn.bind("<Leave>", lambda e, b=logout_btn: b.config(fg=COLORS['gray_700']))


def create_stat_card(parent, title, value, subtitle, icon_color, bg_color, width=220, height=140):
    """Create a stat card similar to React design."""
    card = tk.Frame(parent, bg=COLORS['white'], width=width, height=height, bd=1, relief="solid")
    card.pack(padx=8, pady=8)
    card.pack_propagate(False)
    card.config(highlightbackground=COLORS['gray_100'], highlightthickness=1)

    # Icon and title row
    top_row = tk.Frame(card, bg=COLORS['white'])
    top_row.pack(fill="x", padx=15, pady=(15, 5))

    tk.Label(top_row, text=title, font=('Segoe UI', 11),
            fg=COLORS['gray_600'], bg=COLORS['white']).pack(side="left")

    # Icon
    icon_label = tk.Label(top_row, text="●", font=('Segoe UI', 20),
                         fg=icon_color, bg=COLORS['white'])
    icon_label.pack(side="right")

    # Main value
    value_label = tk.Label(card, text=str(value),
                          font=('Segoe UI', 28, 'bold'),
                          fg=COLORS['gray_900'], bg=COLORS['white'])
    value_label.pack(padx=15, anchor="w")

    # Subtitle
    subtitle_label = tk.Label(card, text=subtitle,
                             font=('Segoe UI', 11),
                             fg=COLORS['gray_500'], bg=COLORS['white'])
    subtitle_label.pack(padx=15, pady=(0, 15), anchor="w")


def setup_dashboard():
    """Setup the modern dashboard with dark red gradient header and card-based design."""
    global cam_label, ocr_text, main_table

    # Clear any existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Main container background (Light Gray)
    root.configure(bg=COLORS['gray_100'])
    
    # ---------- Header Section ----------
    header_container = tk.Frame(root, bg=COLORS['white'], height=100, bd=0)
    header_container.pack(fill="x", side="top")
    header_container.pack_propagate(False)

    # Add a subtle bottom border to header
    header_border = tk.Frame(root, bg=COLORS['gray_200'], height=1)
    header_border.pack(fill="x", side="top")

    # Logo in header (centered)
    header_content = tk.Frame(header_container, bg=COLORS['white'])
    header_content.place(relx=0.5, rely=0.5, anchor='center')

    # White Logo Image
    if PIL_AVAILABLE:
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "docs", "logo.png")
            if not os.path.exists(logo_path):
                 logo_path = os.path.join(os.path.dirname(__file__), "docs", "logo.png")
            
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((240, 80), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header_content, image=logo_photo, bg=COLORS['white'])
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack()
        except Exception as e:
            print(f"Error loading logo in dashboard: {e}")
            logo_label = tk.Label(header_content, text="🚗 ParkinUP", font=('Segoe UI', 28, 'bold'),
                                 fg=COLORS['gray_900'], bg=COLORS['white'])
            logo_label.pack()
    else:
        logo_label = tk.Label(header_content, text="🚗 ParkinUP", font=('Segoe UI', 28, 'bold'),
                             fg=COLORS['gray_900'], bg=COLORS['white'])
        logo_label.pack()
    
    # ---------- Main Content Card ----------
    main_content = tk.Frame(root, bg=COLORS['gray_100'])
    main_content.pack(fill="both", expand=True, padx=40, pady=30)
    
    # Main card with rounded look
    main_card = tk.Frame(main_content, bg=COLORS['white'], bd=0)
    main_card.pack(fill="both", expand=True)
    
    # ---------- Status Bar (Inside Card) ----------
    status_bar = tk.Frame(main_card, bg=COLORS['white'], height=70, bd=1, relief="solid")
    status_bar.pack(fill="x", padx=30, pady=30)
    status_bar.pack_propagate(False)
    status_bar.config(highlightbackground=COLORS['blue_100'], highlightthickness=1)

    def get_available_slots():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM slots WHERE is_occupied=0")
        available = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM slots")
        total = cur.fetchone()[0] or 20
        conn.close()
        return available, total
    
    available, total = get_available_slots()

    # Available Slots (Left)
    status_left = tk.Frame(status_bar, bg=COLORS['blue_50'])
    status_left.pack(side="left", fill="both", expand=True)
    
    available_text = tk.Label(status_left, text=f"🅿️ Available Slots: ",
                          font=('Segoe UI', 12),
                          fg=COLORS['gray_700'], bg=COLORS['blue_50'])
    available_text.pack(side="left", padx=(20, 0))
    
    available_val = tk.Label(status_left, text=f"{available} / {total}",
                          font=('Segoe UI', 18, 'bold'),
                          fg=COLORS['blue_600'], bg=COLORS['blue_50'])
    available_val.pack(side="left", padx=5)

    # Rate (Right)
    rate_label = tk.Label(status_bar, text="🕒 Rate: ₱10/hour",
                         font=('Segoe UI', 11),
                         fg=COLORS['gray_500'], bg=COLORS['white'])
    rate_label.pack(side="right", padx=20)
    
    # ---------- Action Bar ----------
    action_bar = tk.Frame(main_card, bg=COLORS['white'])
    action_bar.pack(fill="x", padx=30, pady=(0, 30))
    
    # Configure grid for equal width buttons
    action_bar.grid_columnconfigure(0, weight=1)
    action_bar.grid_columnconfigure(1, weight=1)
    action_bar.grid_columnconfigure(2, weight=1)
    action_bar.grid_columnconfigure(3, weight=1)

    # Button common styles
    btn_params = {
        'font': ('Segoe UI', 12, 'bold'),
        'relief': 'solid',
        'bd': 1,
        'pady': 20,
        'cursor': 'hand2'
    }

    # Park Vehicle button (Dark)
    park_btn = tk.Button(action_bar, text="Park Vehicle", command=create_park_vehicle_popup,
                        bg=COLORS['gray_900'], fg='white', **btn_params)
    park_btn.grid(row=0, column=0, padx=10, sticky="ew")
    
    # Exit Vehicle button (White)
    exit_btn = tk.Button(action_bar, text="Exit Vehicle", command=create_exit_vehicle_popup,
                        bg='white', fg=COLORS['gray_900'], **btn_params)
    exit_btn.grid(row=0, column=1, padx=10, sticky="ew")
    
    # OCR Detect button
    ocr_btn = tk.Button(action_bar, text="OCR Detect", command=create_ocr_popup,
                       bg='white', fg=COLORS['gray_900'], **btn_params)
    ocr_btn.grid(row=0, column=2, padx=10, sticky="ew")
    
    # View Slots button
    slots_btn = tk.Button(action_bar, text="View Slots", command=open_parking_overview,
                         bg='white', fg=COLORS['gray_900'], **btn_params)
    slots_btn.grid(row=0, column=3, padx=10, sticky="ew")

    # ---------- Camera Preview Area ----------
    camera_container = tk.Frame(main_card, bg=COLORS['white'])
    camera_container.pack(fill="x", padx=30, pady=(0, 30))
    
    # Large camera preview area with icon and text
    cam_preview_frame = tk.Frame(camera_container, bg=COLORS['blue_50'], height=250, bd=1, relief="solid")
    cam_preview_frame.pack(fill="x", expand=True)
    cam_preview_frame.pack_propagate(False)
    
    # Simulated dashed border using a Frame with specific configuration isn't easy in Tkinter,
    # so we use a clean solid border or custom drawing if needed. Here we use solid as fallback.
    
    cam_label = tk.Label(cam_preview_frame,
                        text="📷\n\nCamera Preview Area\n(Simulated - Use OCR Detect for plate recognition)",
                        bg=COLORS['blue_50'], fg=COLORS['gray_500'],
                        font=('Segoe UI', 12), anchor="center",
                        justify="center")
    cam_label.pack(fill="both", expand=True)
    
    # ---------- Currently Parked Vehicles Table ----------
    table_container = tk.Frame(main_card, bg=COLORS['white'])
    table_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))
    
    tk.Label(table_container, text="Currently Parked Vehicles",
            font=('Segoe UI', 18, 'bold'),
            fg=COLORS['gray_900'], bg=COLORS['white']).pack(anchor="w", pady=(0, 15))
    
    # Table with scrollbar
    table_frame = tk.Frame(table_container, bg=COLORS['white'], bd=1, relief="solid")
    table_frame.pack(fill="both", expand=True)
    
    main_table = ttk.Treeview(table_frame, columns=("License Plate", "Slot Number", "Entry Time", "Duration", "Status"),
                             show="headings", height=8)
    for c in ("License Plate", "Slot Number", "Entry Time", "Duration", "Status"):
        main_table.heading(c, text=c)
        main_table.column(c, anchor="center", width=150)
    main_table.pack(fill="both", expand=True)
    
    # Scrollbar for table
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=main_table.yview)
    scrollbar.pack(side="right", fill="y")
    main_table.configure(yscrollcommand=scrollbar.set)
    
    # Define tags for status badges
    main_table.tag_configure("parked", background=COLORS['green_600'], foreground="white")
    main_table.tag_configure("empty", foreground=COLORS['gray_500'])
    
    # Message for empty table (simulated by checking children in refresh_main_table)
    
    # OCR Results log (hidden but defined for popup use)
    ocr_log = []

    # Start camera (optional)
    start_camera()
    
    # Initialize table
    refresh_main_table()
    update_durations()
    
    # Refresh status indicator periodically
    def refresh_status():
        available, total = get_available_slots()
        available_val.config(text=f"{available} / {total}")
        root.after(30000, refresh_status)
    
    refresh_status()


# ---------- Core functions ----------
def refresh_main_table():
    for r in main_table.get_children():
        main_table.delete(r)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT v.vehicle_number, s.slot_number, v.entry_time, v.exit_time
                   FROM vehicles v LEFT JOIN slots s ON v.slot_id = s.slot_id
                   WHERE v.exit_time IS NULL OR v.exit_time = '-'
                   ORDER BY v.vehicle_id DESC LIMIT 50""")
    now = datetime.now()
    rows = cur.fetchall()
    if not rows:
        # Show "No vehicles currently parked" message if needed
        # In Treeview, we usually just leave it empty or insert a placeholder
        main_table.insert("", "end", values=("No vehicles currently parked", "", "", "", ""), tags=("empty",))
    else:
        for row in rows:
            vehicle_number, slot_number, entry_time_str, exit_time_str = row
            entry_time = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S")
            if exit_time_str and exit_time_str != '-':
                exit_time = datetime.strptime(exit_time_str, "%Y-%m-%d %H:%M:%S")
                duration_minutes = int((exit_time - entry_time).total_seconds() / 60)
                status = "Exited"
                tag = "exited"
            else:
                duration_minutes = int((now - entry_time).total_seconds() / 60)
                status = "Parked"
                tag = "parked"
            if duration_minutes >= 60:
                hrs = duration_minutes // 60
                mins = duration_minutes % 60
                duration = f"{hrs} hr {mins} min" if mins else f"{hrs} hr"
            else:
                duration = f"{duration_minutes} min"
            main_table.insert("", "end", values=(vehicle_number, slot_number, entry_time_str, duration, status), tags=(tag,))
    conn.close()

def update_durations():
    """Update durations for parked vehicles in real-time."""
    now = datetime.now()
    for item in main_table.get_children():
        values = main_table.item(item, "values")
        if len(values) > 4 and values[4] == "Parked":  # Status is Parked
            entry_time_str = values[2]
            entry_time = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S")
            duration_minutes = int((now - entry_time).total_seconds() / 60)
            if duration_minutes >= 60:
                hrs = duration_minutes // 60
                mins = duration_minutes % 60
                duration = f"{hrs} hr {mins} min" if mins else f"{hrs} hr"
            else:
                duration = f"{duration_minutes} min"
            main_table.set(item, column="Duration", value=duration)
    # Schedule next update in 60 seconds
    root.after(60000, update_durations)

def log_ocr_result(text: str):
    """Log OCR result."""
    # ocr_text may not be global or available in all contexts now
    print(f"OCR: {text}")

def create_park_vehicle_popup(initial_plate=""):
    """Create a popup modal for parking a vehicle."""
    win = tk.Toplevel(root)
    win.title("Park Vehicle")
    win.geometry("500x250")
    win.configure(bg=COLORS['white'], highlightbackground=COLORS['gray_200'], highlightthickness=1)
    win.resizable(False, False)
    
    # Center the popup
    win.transient(root)
    win.grab_set()
    x = root.winfo_x() + (root.winfo_width() // 2) - (500 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (250 // 2)
    win.geometry(f"+{x}+{y}")
    
    # Title and Subtitle
    tk.Label(win, text="Park Vehicle", font=('Segoe UI', 18, 'bold'),
            fg=COLORS['gray_900'], bg=COLORS['white']).pack(anchor="w", padx=30, pady=(20, 0))
    
    tk.Label(win, text="Enter the license plate number to park a vehicle", font=('Segoe UI', 11),
            fg=COLORS['gray_500'], bg=COLORS['white']).pack(anchor="w", padx=30, pady=(5, 15))
    
    # License Plate Field
    tk.Label(win, text="License Plate", bg=COLORS['white'],
            font=('Segoe UI', 11, 'bold')).pack(anchor="w", padx=30)
    
    plate_frame = tk.Frame(win, bg=COLORS['white'], highlightbackground=COLORS['gray_200'], 
                          highlightthickness=2, bd=0)
    plate_frame.pack(fill="x", padx=30, pady=5)
    
    plate_entry = tk.Entry(plate_frame, font=('Segoe UI', 14), bg="#f9fafb", 
                          relief='flat', bd=0, fg=COLORS['gray_500'])
    plate_entry.pack(fill="x", padx=10, pady=8)
    
    placeholder = "ABC-1234"
    if initial_plate:
        plate_entry.insert(0, initial_plate)
        plate_entry.config(fg=COLORS['gray_900'])
    else:
        plate_entry.insert(0, placeholder)
    
    def on_focus_in(e):
        if plate_entry.get() == placeholder:
            plate_entry.delete(0, tk.END)
            plate_entry.config(fg=COLORS['gray_900'])
            
    def on_focus_out(e):
        if not plate_entry.get():
            plate_entry.insert(0, placeholder)
            plate_entry.config(fg=COLORS['gray_500'])
            
    plate_entry.bind("<FocusIn>", on_focus_in)
    plate_entry.bind("<FocusOut>", on_focus_out)
    
    def submit():
        plate = plate_entry.get().strip()
        if not plate or plate == placeholder:
            messagebox.showwarning("Input", "Please enter a license plate.")
            return
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT slot_id, slot_number FROM slots WHERE is_occupied=0 LIMIT 1")
        row = cur.fetchone()
        if not row:
            conn.close()
            messagebox.showerror("Full", "No available slots.")
            return
        slot_id, slot_no = row
        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cur.execute("INSERT INTO vehicles (owner_name, vehicle_number, slot_id, entry_time) VALUES (?,?,?,?)",
                       ("", plate, slot_id, entry_time))
            cur.execute("UPDATE slots SET is_occupied=1 WHERE slot_id=?", (slot_id,))
            conn.commit()
            messagebox.showinfo("Parked", f"Vehicle parked in {slot_no}")
            win.destroy()
            refresh_main_table()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Vehicle already exists.")
        finally:
            conn.close()
    
    # Buttons container
    btn_frame = tk.Frame(win, bg=COLORS['white'])
    btn_frame.pack(side="bottom", fill="x", padx=30, pady=20)
    
    # Park button (Right)
    park_btn = tk.Button(btn_frame, text="Park Vehicle", command=submit,
                        bg=COLORS['gray_600'], fg='white',
                        font=('Segoe UI', 11, 'bold'), width=12,
                        relief='flat', bd=0, padx=15, pady=8)
    park_btn.pack(side="right", padx=(10, 0))
    
    # Cancel button (Left)
    cancel_btn = tk.Button(btn_frame, text="Cancel", command=win.destroy,
                          bg=COLORS['white'], fg=COLORS['gray_900'],
                          font=('Segoe UI', 11, 'bold'), width=10,
                          relief='solid', bd=1, padx=15, pady=8)
    cancel_btn.pack(side="right")
    cancel_btn.config(highlightbackground=COLORS['gray_200'], bd=1)


def create_exit_vehicle_popup():
    """Create a popup modal for exiting a vehicle."""
    win = tk.Toplevel(root)
    win.title("Exit Vehicle")
    win.geometry("500x300")
    win.configure(bg=COLORS['white'], highlightbackground=COLORS['gray_200'], highlightthickness=1)
    win.resizable(False, False)
    
    # Center the popup
    win.transient(root)
    win.grab_set()
    x = root.winfo_x() + (root.winfo_width() // 2) - (500 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (300 // 2)
    win.geometry(f"+{x}+{y}")
    
    # Title and Subtitle
    tk.Label(win, text="Exit Vehicle", font=('Segoe UI', 18, 'bold'),
            fg=COLORS['gray_900'], bg=COLORS['white']).pack(anchor="w", padx=30, pady=(20, 0))
    
    tk.Label(win, text="Enter the license plate number to process vehicle exit", font=('Segoe UI', 11),
            fg=COLORS['gray_500'], bg=COLORS['white']).pack(anchor="w", padx=30, pady=(5, 15))
    
    # License Plate Field
    tk.Label(win, text="License Plate", bg=COLORS['white'],
            font=('Segoe UI', 11, 'bold')).pack(anchor="w", padx=30)
    
    plate_frame = tk.Frame(win, bg=COLORS['white'], highlightbackground=COLORS['gray_200'], 
                          highlightthickness=2, bd=0)
    plate_frame.pack(fill="x", padx=30, pady=5)
    
    plate_entry = tk.Entry(plate_frame, font=('Segoe UI', 14), bg="#f9fafb", 
                          relief='flat', bd=0, fg=COLORS['gray_500'])
    plate_entry.pack(fill="x", padx=10, pady=8)
    
    placeholder = "ABC-1234"
    plate_entry.insert(0, placeholder)
    
    def on_focus_in(e):
        if plate_entry.get() == placeholder:
            plate_entry.delete(0, tk.END)
            plate_entry.config(fg=COLORS['gray_900'])
            
    def on_focus_out(e):
        if not plate_entry.get():
            plate_entry.insert(0, placeholder)
            plate_entry.config(fg=COLORS['gray_500'])
            
    plate_entry.bind("<FocusIn>", on_focus_in)
    plate_entry.bind("<FocusOut>", on_focus_out)
    
    def submit():
        plate = plate_entry.get().strip()
        if not plate or plate == placeholder:
            messagebox.showwarning("Input", "Please enter license plate number.")
            return
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT v.vehicle_id, v.entry_time, v.slot_id, s.slot_number
                      FROM vehicles v JOIN slots s ON v.slot_id = s.slot_id
                      WHERE v.vehicle_number=? AND v.exit_time IS NULL""", (plate,))
        rec = cur.fetchone()
        if not rec:
            conn.close()
            messagebox.showerror("Not found", "No active parked vehicle with this number.")
            return
        vehicle_id, entry_time_str, slot_id, slot_no = rec
        now = datetime.now()
        exit_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        minutes, amount = calculate_fee(entry_time_str, exit_time_str, rate_per_min=10/60)
        cur.execute("UPDATE vehicles SET exit_time=? WHERE vehicle_id=?", (exit_time_str, vehicle_id))
        cur.execute("UPDATE slots SET is_occupied=0 WHERE slot_id=?", (slot_id,))
        cur.execute("INSERT INTO payments (vehicle_id, amount, payment_time) VALUES (?, ?, ?)",
                   (vehicle_id, amount, exit_time_str))
        conn.commit()
        conn.close()
        show_receipt(plate, entry_time_str, exit_time_str, minutes, amount, rate_per_min=10/60, slot_no=slot_no, vehicle_id=vehicle_id)
        win.destroy()
        refresh_main_table()
    
    # Buttons container
    btn_frame = tk.Frame(win, bg=COLORS['white'])
    btn_frame.pack(side="bottom", fill="x", padx=30, pady=20)
    
    # Process Exit button (Right)
    exit_btn = tk.Button(btn_frame, text="Process Exit", command=submit,
                        bg=COLORS['gray_600'], fg='white',
                        font=('Segoe UI', 11, 'bold'), width=12,
                        relief='flat', bd=0, padx=15, pady=8)
    exit_btn.pack(side="right", padx=(10, 0))
    
    # Cancel button (Right, next to Process)
    cancel_btn = tk.Button(btn_frame, text="Cancel", command=win.destroy,
                          bg=COLORS['white'], fg=COLORS['gray_900'],
                          font=('Segoe UI', 11, 'bold'), width=8,
                          relief='solid', bd=1, padx=15, pady=8)
    cancel_btn.pack(side="right")
    cancel_btn.config(highlightbackground=COLORS['gray_200'], bd=1)
    
    # Use OCR button (Left)
    def open_ocr():
        win.destroy()
        create_ocr_popup()
        
    ocr_btn = tk.Button(btn_frame, text="📷 Use OCR", command=open_ocr,
                       bg=COLORS['white'], fg=COLORS['gray_900'],
                       font=('Segoe UI', 11, 'bold'),
                       relief='solid', bd=1, padx=15, pady=8)
    ocr_btn.pack(side="left")
    ocr_btn.config(highlightbackground=COLORS['gray_200'], bd=1)


def create_ocr_popup():
    """Create a popup modal for OCR detection."""
    win = tk.Toplevel(root)
    win.title("OCR License Plate Detection")
    win.geometry("550x450")
    win.configure(bg=COLORS['white'], highlightbackground=COLORS['gray_200'], highlightthickness=1)
    win.resizable(False, False)
    
    # Center the popup and make it look like an overlay
    win.transient(root)
    win.grab_set()
    x = root.winfo_x() + (root.winfo_width() // 2) - (550 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (450 // 2)
    win.geometry(f"+{x}+{y}")
    
    # Title
    tk.Label(win, text="OCR License Plate Detection", font=('Segoe UI', 20, 'bold'),
            fg=COLORS['gray_900'], bg=COLORS['white']).pack(anchor="w", padx=30, pady=(25, 0))
    
    # Subtitle
    tk.Label(win, text="Detect plate to park vehicle", font=('Segoe UI', 12),
            fg=COLORS['gray_500'], bg=COLORS['white']).pack(anchor="w", padx=30, pady=(5, 10))
    
    def upload_image():
        filename = filedialog.askopenfilename(
            title="Upload License Plate Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if filename:
            # Simulate OCR detection
            plate = ocr_stub(filename)
            if plate:
                messagebox.showinfo("Detection Result", f"Detected Plate: {plate}")
                win.destroy()
                create_park_vehicle_popup(plate)
            else:
                messagebox.showerror("Detection Failed", "Plate not detected in image.")

    # Upload Area with dashed border using Canvas
    upload_canvas = tk.Canvas(win, bg=COLORS['white'], highlightthickness=0, width=490, height=220)
    upload_canvas.pack(padx=30, pady=20)
    
    # Draw dashed rectangle
    # We use a slight offset (2,2) to ensure the line is visible within canvas bounds
    upload_canvas.create_rectangle(2, 2, 488, 218, outline="#cbd5e1", dash=(5, 5), width=2)
    upload_canvas.bind("<Button-1>", lambda e: upload_image())
    
    # Inner content for upload area
    inner_upload = tk.Frame(upload_canvas, bg=COLORS['white'])
    upload_canvas.create_window(245, 110, window=inner_upload)
    inner_upload.bind("<Button-1>", lambda e: upload_image())
    
    # Camera Icon
    cam_icon = tk.Label(inner_upload, text="📷", font=('Segoe UI', 64), 
                       fg="#94a3b8", bg=COLORS['white'], cursor="hand2")
    cam_icon.pack()
    cam_icon.bind("<Button-1>", lambda e: upload_image())
    
    # Text in upload area
    tk.Label(inner_upload, text="Upload image with license plate", font=('Segoe UI', 14, 'bold'),
            fg="#475569", bg=COLORS['white']).pack(pady=(10, 5))
    
    tk.Label(inner_upload, text="(Filename should contain plate number, e.g., plate_ABC1234.jpg)", 
            font=('Segoe UI', 10), fg="#94a3b8", bg=COLORS['white']).pack()

    # Enter Manually Button
    def enter_manually():
        win.destroy()
        create_park_vehicle_popup()
        
    manual_btn = tk.Button(win, text="⌨️  Enter Manually", command=enter_manually,
                          bg=COLORS['white'], fg=COLORS['gray_900'],
                          font=('Segoe UI', 13, 'bold'),
                          relief='solid', bd=1, padx=20, pady=12)
    manual_btn.pack(side="bottom", fill="x", padx=30, pady=(0, 30))
    # Make it look rounded-ish by adjusting highlightthickness and highlightbackground
    manual_btn.config(highlightbackground="#e2e8f0", highlightthickness=1, bd=1, relief="flat", 
                     highlightcolor="#e2e8f0", activebackground="#f8fafc")
    
    # Add a rounded border simulation for the button
    # Tkinter buttons don't support true rounded corners without custom shapes or images,
    # but we can make it look clean with a light border.


def create_view_slots_popup():
    """Create a popup modal showing parking slot overview with visual grid as per design."""
    win = tk.Toplevel(root)
    win.title("Parking Slots Overview")
    win.geometry("520x620")
    win.configure(bg=COLORS['white'], highlightbackground=COLORS['gray_200'], highlightthickness=1)
    win.resizable(False, False)

    # Center the popup
    win.transient(root)
    win.grab_set()
    x = root.winfo_x() + (root.winfo_width() // 2) - (520 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (620 // 2)
    win.geometry(f"+{x}+{y}")

    # Header Section
    header_frame = tk.Frame(win, bg=COLORS['white'], padx=20, pady=(20, 10))
    header_frame.pack(fill="x")

    tk.Label(header_frame, text="Parking Slots Overview", font=('Segoe UI', 18, 'bold'),
            fg=COLORS['gray_900'], bg=COLORS['white']).pack(anchor="w")

    tk.Label(header_frame, text="View all parking slots and their availability status",
            font=('Segoe UI', 10), fg=COLORS['gray_500'], bg=COLORS['white']).pack(anchor="w", pady=(3, 0))

    # Fetch slots from DB
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT slot_number, is_occupied FROM slots ORDER BY CAST(SUBSTR(slot_number, 6) AS INTEGER)")
    slots = cur.fetchall()
    conn.close()

    # Grid of slots
    container_frame = tk.Frame(win, bg=COLORS['white'], padx=20, pady=10)
    container_frame.pack(fill="both", expand=True)

    grid_frame = tk.Frame(container_frame, bg=COLORS['white'])
    grid_frame.pack()

    # Define status colors from screenshot
    COLOR_AVAILABLE = "#10b981"    # Emerald 500
    COLOR_BG_AVAILABLE = "#ecfdf5" # Emerald 50
    COLOR_OCCUPIED = "#ef4444"     # Red 500
    COLOR_BG_OCCUPIED = "#fef2f2"  # Red 50

    def show_slot_details(slot_name, is_occ):
        if is_occ:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""SELECT v.vehicle_number, v.owner_name, v.entry_time 
                           FROM vehicles v JOIN slots s ON v.slot_id = s.slot_id 
                           WHERE s.slot_number=? AND v.exit_time IS NULL""", (slot_name,))
            res = cur.fetchone()
            conn.close()
            if res:
                vnum, owner, entry = res
                msg = f"Slot: {slot_name}\nStatus: Occupied\nVehicle: {vnum}\nOwner: {owner}\nEntry: {entry}"
            else:
                msg = f"Slot: {slot_name}\nStatus: Occupied\nInformation not found."
        else:
            msg = f"Slot: {slot_name}\nStatus: Available\nNo vehicle parked."
        messagebox.showinfo("Slot Details", msg)

    for idx, (slot_name, is_occupied) in enumerate(slots):
        row = idx // 5
        col = idx % 5

        # Get the number part of "Slot-X"
        slot_display_num = slot_name.split('-')[-1] if '-' in slot_name else slot_name

        if is_occupied:
            status_color = COLOR_OCCUPIED
            status_text = "Occupied"
            bg_color = COLOR_BG_OCCUPIED
        else:
            status_color = COLOR_AVAILABLE
            status_text = "Available"
            bg_color = COLOR_BG_AVAILABLE

        # Slot Card with border and background
        card = tk.Frame(grid_frame, bg=bg_color, width=85, height=105,
                       highlightthickness=1, highlightbackground=status_color, cursor="hand2")
        card.grid(row=row, column=col, padx=6, pady=6)
        card.pack_propagate(False)
        card.bind("<Button-1>", lambda e, sn=slot_name, io=is_occupied: show_slot_details(sn, io))

        # Center the labels within the card
        content_frame = tk.Frame(card, bg=bg_color)
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        content_frame.bind("<Button-1>", lambda e, sn=slot_name, io=is_occupied: show_slot_details(sn, io))

        tk.Label(content_frame, text="Slot", font=('Segoe UI', 9, 'bold'),
                fg=status_color, bg=bg_color).pack()
        tk.Label(content_frame, text=slot_display_num, font=('Segoe UI', 18, 'bold'),
                fg=status_color, bg=bg_color).pack(pady=2)
        tk.Label(content_frame, text=status_text, font=('Segoe UI', 9),
                fg=status_color, bg=bg_color).pack()

    # Footer Section
    footer_frame = tk.Frame(win, bg=COLORS['white'], padx=20, pady=20)
    footer_frame.pack(fill="x", side="bottom")

    # Legend
    legend_frame = tk.Frame(footer_frame, bg=COLORS['white'])
    legend_frame.pack(side="left")

    # Available Legend
    tk.Frame(legend_frame, bg=COLOR_BG_AVAILABLE, width=15, height=15,
             highlightthickness=1, highlightbackground=COLOR_AVAILABLE).pack(side="left")
    tk.Label(legend_frame, text="Available", font=('Segoe UI', 10),
            bg=COLORS['white'], fg=COLORS['gray_700']).pack(side="left", padx=(5, 15))

    # Occupied Legend
    tk.Frame(legend_frame, bg=COLOR_BG_OCCUPIED, width=15, height=15,
             highlightthickness=1, highlightbackground=COLOR_OCCUPIED).pack(side="left")
    tk.Label(legend_frame, text="Occupied", font=('Segoe UI', 10),
            bg=COLORS['white'], fg=COLORS['gray_700']).pack(side="left", padx=(5, 15))

    # Close Button
    tk.Button(footer_frame, text="Close", command=win.destroy,
             bg="#0f172a", fg='white',
             font=('Segoe UI', 10, 'bold'), width=10, pady=8,
             relief='flat', bd=0, cursor="hand2").pack(side="right")



def add_vehicle_window():
    def submit():
        owner = win_owner.get().strip()
        vnum = win_number.get().strip()
        if not vnum:
            messagebox.showwarning("Input", "Please enter a vehicle number.")
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT slot_id, slot_number FROM slots WHERE is_occupied=0 LIMIT 1")
        row = cur.fetchone()
        if not row:
            conn.close()
            messagebox.showerror("Full", "No available slots.")
            return
        slot_id, slot_no = row
        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cur.execute("INSERT INTO vehicles (owner_name, vehicle_number, slot_id, entry_time) VALUES (?,?,?,?)",
                        (owner, vnum, slot_id, entry_time))
            cur.execute("UPDATE slots SET is_occupied=1 WHERE slot_id=?", (slot_id,))
            conn.commit()
            messagebox.showinfo("Parked", f"Vehicle parked in {slot_no}")
            win.destroy()
            refresh_main_table()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Vehicle number already exists.")
        finally:
            conn.close()

    win = tk.Toplevel(root)
    win.title("Park Vehicle")
    win.geometry("400x230")
    win.configure(bg=COLORS['white'])
    
    tk.Label(win, text="Park Vehicle", font=('Segoe UI', 18, 'bold'),
            fg=COLORS['gray_900'], bg=COLORS['white']).pack(pady=20)
    
    tk.Label(win, text="Owner Name:", bg=COLORS['white']).pack()
    win_owner = tk.Entry(win, width=32, font=('Segoe UI', 11), relief='solid', bd=2)
    win_owner.pack(pady=5)
    
    tk.Label(win, text="Vehicle Number:", bg=COLORS['white']).pack()
    win_number = tk.Entry(win, width=32, font=('Segoe UI', 11), relief='solid', bd=2)
    win_number.pack(pady=5)
    
    b = tk.Button(win, text="Park Vehicle", command=submit, bg=COLORS['blue_600'], fg='white',
                 font=('Segoe UI', 12, 'bold'), width=20, height=2, relief='flat', bd=0)
    b.pack(pady=20)
    b.bind("<Enter>", lambda e, b=b: b.config(bg=COLORS['blue_700']))
    b.bind("<Leave>", lambda e, b=b: b.config(bg=COLORS['blue_600']))

def exit_vehicle_window():
    def submit_exit():
        vnum = win_number.get().strip()
        if not vnum:
            messagebox.showwarning("Input", "Please enter vehicle number.")
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT v.vehicle_id, v.entry_time, v.slot_id, s.slot_number
                       FROM vehicles v JOIN slots s ON v.slot_id = s.slot_id
                       WHERE v.vehicle_number=? AND v.exit_time IS NULL""", (vnum,))
        rec = cur.fetchone()
        if not rec:
            conn.close()
            messagebox.showerror("Not found", "No active parked vehicle with this number.")
            return
        vehicle_id, entry_time_str, slot_id, slot_no = rec
        now = datetime.now()
        exit_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        minutes, amount = calculate_fee(entry_time_str, exit_time_str, rate_per_min=10/60)
        cur.execute("UPDATE vehicles SET exit_time=? WHERE vehicle_id=?", (exit_time_str, vehicle_id))
        cur.execute("UPDATE slots SET is_occupied=0 WHERE slot_id=?", (slot_id,))
        cur.execute("INSERT INTO payments (vehicle_id, amount, payment_time) VALUES (?, ?, ?)",
                    (vehicle_id, amount, exit_time_str))
        conn.commit()
        conn.close()
        show_receipt(vnum, entry_time_str, exit_time_str, minutes, amount, rate_per_min=10/60, slot_no=slot_no, vehicle_id=vehicle_id)
        win.destroy()
        refresh_main_table()

    win = tk.Toplevel(root)
    win.title("Exit Vehicle")
    win.geometry("380x220")
    win.configure(bg=COLORS['white'])
    
    tk.Label(win, text="Exit Vehicle", font=('Segoe UI', 18, 'bold'),
            fg=COLORS['gray_900'], bg=COLORS['white']).pack(pady=20)
    
    tk.Label(win, text="Vehicle Number:", bg=COLORS['white']).pack()
    win_number = tk.Entry(win, width=30, font=('Segoe UI', 11), relief='solid', bd=2)
    win_number.pack(pady=5)
    
    b = tk.Button(win, text="Process Exit & Pay", command=submit_exit, bg=COLORS['red_600'], fg='white',
                 font=('Segoe UI', 12, 'bold'), width=20, height=2, relief='flat', bd=0)
    b.pack(pady=20)
    b.bind("<Enter>", lambda e, b=b: b.config(bg=COLORS['red_700']))
    b.bind("<Leave>", lambda e, b=b: b.config(bg=COLORS['red_600']))

def view_parked_window():
    win = tk.Toplevel(root)
    win.title("Currently Parked Vehicles")
    win.geometry("760x420")
    win.configure(bg=COLORS['white'])
    
    tree = ttk.Treeview(win, columns=("Owner","Vehicle","Slot","Entry"), show="headings")
    for col in ("Owner","Vehicle","Slot","Entry"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=180)
    tree.pack(expand=True, fill="both", padx=8, pady=8)
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT v.owner_name, v.vehicle_number, s.slot_number, v.entry_time
                   FROM vehicles v JOIN slots s ON v.slot_id=s.slot_id
                   WHERE v.exit_time IS NULL ORDER BY v.entry_time DESC""")
    for row in cur.fetchall():
        tree.insert("", "end", values=row)
    conn.close()

def payments_window():
    win = tk.Toplevel(root)
    win.title("Payments / Revenue")
    win.geometry("760x420")
    win.configure(bg=COLORS['white'])
    
    tree = ttk.Treeview(win, columns=("Vehicle","Amount","Time"), show="headings")
    for col in ("Vehicle","Amount","Time"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=180)
    tree.pack(expand=True, fill="both", padx=8, pady=8)
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT v.vehicle_number, p.amount, p.payment_time
                   FROM payments p JOIN vehicles v ON p.vehicle_id=v.vehicle_id
                   ORDER BY p.payment_time DESC""")
    for row in cur.fetchall():
        tree.insert("", "end", values=row)
    cur.execute("SELECT COALESCE(SUM(amount),0) FROM payments")
    total = cur.fetchone()[0] or 0
    conn.close()
    tk.Label(win, text=f"Total Revenue: P{round(total,2)}", font=('Segoe UI', 12, 'bold'),
            bg=COLORS['white']).pack(pady=6)

def vehicles_window():
    win = tk.Toplevel(root)
    win.title("Vehicles")
    win.geometry("760x420")
    win.configure(bg=COLORS['white'])
    
    tree = ttk.Treeview(win, columns=("Owner","Vehicle","Entry","Exit","Status"), show="headings")
    for col in ("Owner","Vehicle","Entry","Exit","Status"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=140)
    tree.pack(expand=True, fill="both", padx=8, pady=8)
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT v.owner_name, v.vehicle_number, v.entry_time, v.exit_time
                   FROM vehicles v ORDER BY v.entry_time DESC""")
    for row in cur.fetchall():
        owner, vehicle, entry, exit_time = row
        status = "Parked" if exit_time is None else "Exited"
        row_values = (owner, vehicle, entry, exit_time or "-", status)
        tree.insert("", "end", values=row_values)
    conn.close()

def open_parking_overview():
    """Fetch slot data and show the grid overview modal."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Sort by slot number to ensure consistent 4x5 grid layout
        cur.execute("""SELECT slot_number, is_occupied 
                       FROM slots 
                       ORDER BY CAST(SUBSTR(slot_number, INSTR(slot_number, '-') + 1) AS INTEGER) 
                       LIMIT 20""")
        rows = cur.fetchall()
        conn.close()
        
        slots_data = []
        for number, occupied in rows:
            # Strip "Slot-" prefix for display in the card if needed, 
            # or keep it. The design shows just numbers 1, 2, 3...
            display_number = number.replace("Slot-", "")
            slots_data.append({'number': display_number, 'occupied': bool(occupied)})
            
        if not slots_data:
            messagebox.showinfo("No Data", "No parking slots found in the database.")
            return
            
        show_parking_slots_overview(root, slots_data)
    except Exception as e:
        messagebox.showerror("Error", f"Could not load parking slots: {e}")

def slot_status_window():
    win = tk.Toplevel(root)
    win.title("Slot Status")
    win.geometry("900x600")
    win.configure(bg=COLORS['gray_50'])
    
    tk.Label(win, text="Parking Slots Status", font=('Segoe UI', 18, 'bold'),
            fg=COLORS['gray_900'], bg=COLORS['gray_50']).pack(pady=20)
    
    table = ttk.Treeview(win, columns=("Slot","Status"), show="headings")
    for c in ("Slot","Status"):
        table.heading(c, text=c)
        table.column(c, anchor="center", width=200)
    table.pack(expand=True, fill="both", padx=12, pady=12)
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT slot_number, is_occupied 
                   FROM slots 
                   ORDER BY CAST(SUBSTR(slot_number, INSTR(slot_number, '-') + 1) AS INTEGER)""")
    rows = cur.fetchall()
    conn.close()
    
    for s, occ in rows:
        status = "Occupied" if occ else "Available"
        table.insert("", "end", values=(s, status))
    
    total = len(rows)
    occupied = sum(1 for _, occ in rows if occ)
    available = total - occupied
    tk.Label(win, text=f"Total Slots: {total} | Occupied: {occupied} | Available: {available}",
             font=('Segoe UI', 11, 'bold'), bg=COLORS['gray_50']).pack(pady=8)

def add_slots_window():
    win = tk.Toplevel(root)
    win.title("➕ Add Parking Slots")
    win.geometry("400x220")
    win.configure(bg=COLORS['white'])
    win.resizable(False, False)

    tk.Label(win, text="🚘 Add or Update Total Slots",
             font=('Segoe UI', 14, 'bold'), bg=COLORS['white'], fg=COLORS['gray_900']).pack(pady=20)
    tk.Label(win, text="Enter total number of slots:", bg=COLORS['white'],
             font=('Segoe UI', 11)).pack(pady=5)
    entry = tk.Entry(win, width=15, font=('Segoe UI', 11), justify="center", relief='solid', bd=2)
    entry.pack(pady=5)

    def update_slots():
        try:
            total = int(entry.get().strip())
            if total <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid", "Enter a valid positive number.")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS slots (
                        slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        slot_number TEXT UNIQUE NOT NULL,
                        is_occupied INTEGER DEFAULT 0
                       );""")
        for i in range(1, total + 1):
            slot_name = f"Slot-{i}"
            cur.execute("INSERT OR IGNORE INTO slots (slot_number, is_occupied) VALUES (?, 0)", (slot_name,))
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM slots")
        count = cur.fetchone()[0]
        conn.close()

        messagebox.showinfo("Success", f"Slots updated!\nTotal slots: {count}")
        win.destroy()
        refresh_main_table()

    b = tk.Button(win, text="Update Slots", command=update_slots, bg=COLORS['blue_600'], fg="white",
                  font=('Segoe UI', 10, 'bold'), width=15, height=2, relief='flat', bd=0)
    b.pack(pady=20)
    b.bind("<Enter>", lambda e, b=b: b.config(bg=COLORS['blue_700']))
    b.bind("<Leave>", lambda e, b=b: b.config(bg=COLORS['blue_600']))

def show_receipt(plate: str, time_in: str, time_out: str, minutes: int, amount: float,
                 rate_per_min: float = 1.0, slot_no: str | None = None, vehicle_id: int | None = None):
    """Display a formatted receipt window similar to the provided sample."""
    win = tk.Toplevel(root)
    win.title("ParkinUP - Receipt")
    win.geometry("420x420")
    win.resizable(False, False)
    win.configure(bg=COLORS['white'])
    
    frame = tk.Frame(win, bg=COLORS['white'], bd=12)
    frame.pack(expand=True, fill="both")

    # Logo in receipt
    if PIL_AVAILABLE:
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "docs", "logo.png")
            if not os.path.exists(logo_path):
                 logo_path = os.path.join(os.path.dirname(__file__), "docs", "logo.png")
            
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((140, 50), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(frame, image=logo_photo, bg=COLORS['white'])
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack()
        except Exception:
            title = tk.Label(frame, text="ParkinUP", font=('Segoe UI', 18, 'bold'), bg=COLORS['white'])
            title.pack()
    else:
        title = tk.Label(frame, text="ParkinUP", font=('Segoe UI', 18, 'bold'), bg=COLORS['white'])
        title.pack()
    subtitle = tk.Label(frame, text="Automated Parking System", font=('Segoe UI', 10), bg=COLORS['white'])
    subtitle.pack()

    sep = ttk.Separator(frame, orient="horizontal")
    sep.pack(fill="x", pady=8)

    body = tk.Frame(frame, bg=COLORS['white'])
    body.pack(fill="both", expand=True, padx=6)

    # Use monospace layout for receipt-like appearance
    mono = ("Courier", 10)

    def row(label_text, value_text):
        r = tk.Frame(body, bg=COLORS['white'])
        r.pack(fill="x", pady=2)
        tk.Label(r, text=label_text, font=mono, bg=COLORS['white']).pack(side="left")
        tk.Label(r, text=value_text, font=mono, bg=COLORS['white']).pack(side="right")

    row("Plate Number:", plate)
    row("Time-In:", time_in)
    row("Time-Out:", time_out)
    # duration display in hours/minutes if >59
    if minutes >= 60:
        hrs = minutes // 60
        mins = minutes % 60
        dur_text = f"{hrs} hr {mins} min" if mins else f"{hrs} hr"
    else:
        dur_text = f"{minutes} min"
    row("Duration:", dur_text)
    per_hour = round(rate_per_min * 60, 2)
    row("Rate:", f"{format_currency(per_hour)}/hour")

    sep2 = ttk.Separator(body, orient="horizontal")
    sep2.pack(fill="x", pady=8)

    total_frame = tk.Frame(body, bg=COLORS['white'])
    total_frame.pack(fill="x")
    tk.Label(total_frame, text="TOTAL FEE:", font=('Segoe UI', 12, 'bold'), bg=COLORS['white']).pack(side="left")
    tk.Label(total_frame, text=f"{format_currency(amount)}", font=('Segoe UI', 12, 'bold'), bg=COLORS['white']).pack(side="right")

    sep3 = ttk.Separator(frame, orient="horizontal")
    sep3.pack(fill="x", pady=8)

    txn_id = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    if vehicle_id:
        txn_id = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{vehicle_id}"

    thank = tk.Label(frame, text="Thank you for parking with us!", font=('Segoe UI', 9), bg=COLORS['white'])
    thank.pack()
    tx = tk.Label(frame, text=f"Transaction ID: {txn_id}", font=('Segoe UI', 9), bg=COLORS['white'])
    tx.pack()

    btn = tk.Button(frame, text="Close", command=win.destroy, bg=COLORS['blue_600'], fg="white", width=12,
                   font=('Segoe UI', 10, 'bold'), relief='flat', bd=0)
    btn.pack(pady=10)

def detect_plate_window():
    """Capture current frame and detect plate using OCR, show result."""
    plate = None
    try:
        if cam_frame is not None and cv2 is not None:
            import tempfile
            fd, path = tempfile.mkstemp(suffix=".jpg")
            os.close(fd)
            cv2.imwrite(path, cam_frame)
            plate = ocr_stub(path)
            try:
                os.unlink(path)
            except OSError:
                pass
        else:
            plate = ocr_stub(None)
    except Exception:
        plate = ocr_stub(None)

    if plate:
        log_ocr_result(f"Detected Plate: {plate}")
        messagebox.showinfo("Detected Plate", f"Detected Plate: {plate}")
    else:
        log_ocr_result("Plate not detected")
        messagebox.showerror("OCR", "Plate not detected.")


# ---------- On Close ----------
def on_app_close():
    stop_camera()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_app_close)

# Show homepage initially
create_homepage(root, on_start_now=show_login, on_learn_more=show_learn_more_dialog)

root.mainloop()
