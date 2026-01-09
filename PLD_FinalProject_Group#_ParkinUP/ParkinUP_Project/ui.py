import os
import tkinter as tk
from tkinter import messagebox, font

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE_UI = True
except ImportError:
    PIL_AVAILABLE_UI = False

# Color Scheme (matching React design)
COLORS = {
    'white': '#ffffff',
    'gray_50': '#f9fafb',
    'gray_100': '#f3f4f6',
    'gray_200': '#e5e7eb',
    'blue_50': '#eff6ff',
    'blue_600': '#2563eb',
    'blue_700': '#1d4ed8',
    'red_600': '#dc2626',
    'red_700': '#b91c1c',
    'red_800': '#991b1b',
    'red_500': '#ef4444',
    'red_400': '#f87171',
    'yellow_500': '#eab308',
    'gray_900': '#111827',
    'gray_700': '#374151',
    'gray_600': '#4b5563',
    'gray_500': '#6b7280',
    'green_600': '#16a34a',
    'green_500': '#22c55e',
    'blue_100': '#dbeafe',
    'yellow_100': '#fef9c3',
    'red_100': '#fee2e2',
}

# Custom fonts
FONTS = {
    'header': ('Segoe UI', 28, 'bold'),
    'sub_header': ('Segoe UI', 20, 'bold'),
    'body': ('Segoe UI', 12),
    'body_bold': ('Segoe UI', 12, 'bold'),
    'button': ('Segoe UI', 12, 'bold'),
    'label': ('Segoe UI', 11),
}

def create_homepage(root, on_start_now, on_learn_more):
    """Create the modern React-style homepage."""
    # Clear any existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Create main container with gradient background effect
    root.configure(bg=COLORS['white'])
    
    # Main frame
    main_frame = tk.Frame(root, bg=COLORS['white'])
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)

    # ---------- Navigation Bar ----------
    nav_frame = tk.Frame(main_frame, bg=COLORS['white'], height=100)
    nav_frame.pack(fill="x", pady=(0, 20))
    nav_frame.pack_propagate(False)

    # Logo
    logo_frame = tk.Frame(nav_frame, bg=COLORS['white'])
    logo_frame.pack(side="left", padx=20, pady=10)

    if PIL_AVAILABLE_UI:
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "docs", "logo.png")
            if not os.path.exists(logo_path):
                 # Try another common location just in case
                 logo_path = os.path.join(os.path.dirname(__file__), "docs", "logo.png")
            
            logo_img = Image.open(logo_path)
            # Adjust size to fit in the 100px height frame with some padding
            logo_img = logo_img.resize((210, 80), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(logo_frame, image=logo_photo, bg=COLORS['white'])
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack()
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback to text
            p_label = tk.Label(logo_frame, text="P", font=('Segoe UI', 24, 'bold'),
                              fg=COLORS['yellow_500'], bg=COLORS['white'])
            p_label.pack(side="left")
            car_label = tk.Label(logo_frame, text="🚗", font=('Segoe UI', 20), bg=COLORS['white'])
            car_label.pack(side="left")
            arkin_label = tk.Label(logo_frame, text="arkin", font=('Segoe UI', 24, 'bold'),
                                  fg=COLORS['red_600'], bg=COLORS['white'])
            arkin_label.pack(side="left")
            bike_label = tk.Label(logo_frame, text="🚲", font=('Segoe UI', 20), bg=COLORS['white'])
            bike_label.pack(side="left")
            up_label = tk.Label(logo_frame, text="UP", font=('Segoe UI', 24, 'bold'),
                               fg=COLORS['yellow_500'], bg=COLORS['white'])
            up_label.pack(side="left")
    else:
        # Fallback to text
        p_label = tk.Label(logo_frame, text="P", font=('Segoe UI', 24, 'bold'),
                          fg=COLORS['yellow_500'], bg=COLORS['white'])
        p_label.pack(side="left")
        car_label = tk.Label(logo_frame, text="🚗", font=('Segoe UI', 20), bg=COLORS['white'])
        car_label.pack(side="left")
        arkin_label = tk.Label(logo_frame, text="arkin", font=('Segoe UI', 24, 'bold'),
                              fg=COLORS['white'], bg=COLORS['white'])
        arkin_label.pack(side="left")
        bike_label = tk.Label(logo_frame, text="🚲", font=('Segoe UI', 20), bg=COLORS['white'])
        bike_label.pack(side="left")
        up_label = tk.Label(logo_frame, text="UP", font=('Segoe UI', 24, 'bold'),
                           fg=COLORS['yellow_500'], bg=COLORS['white'])
        up_label.pack(side="left")

    # Navigation buttons
    nav_buttons_frame = tk.Frame(nav_frame, bg=COLORS['white'])
    nav_buttons_frame.pack(side="right", padx=20, pady=15)

    nav_styles = {
        'bg': COLORS['white'],
        'fg': COLORS['gray_700'],
        'font': FONTS['button'],
        'relief': 'flat',
        'bd': 0,
        'padx': 15,
    }

    nav_buttons = [
        ("About us", lambda: None),
        ("Features", lambda: None),
        ("Blog", lambda: None),
        ("Resources", lambda: None),
    ]

    for text, command in nav_buttons:
        btn = tk.Button(nav_buttons_frame, text=text, command=command, **nav_styles)
        btn.pack(side="left", padx=10)
        # Hover effect
        btn.bind("<Enter>", lambda e, b=btn: b.config(fg=COLORS['red_600']))
        btn.bind("<Leave>", lambda e, b=btn: b.config(fg=COLORS['gray_700']))

    # Sign in button
    sign_in_btn = tk.Button(nav_buttons_frame, text="Sign in", command=on_start_now,
                           bg=COLORS['white'], fg=COLORS['gray_700'],
                           font=FONTS['button'], relief='flat', bd=0, padx=15)
    sign_in_btn.pack(side="left", padx=10)

    # Start free button (blue)
    start_free_btn = tk.Button(nav_buttons_frame, text="Start free", command=on_start_now,
                              bg=COLORS['blue_600'], fg='white',
                              font=FONTS['button'], relief='flat', bd=0, padx=20, pady=8)
    start_free_btn.pack(side="left", padx=10)
    start_free_btn.bind("<Enter>", lambda e, b=start_free_btn: b.config(bg=COLORS['blue_700']))
    start_free_btn.bind("<Leave>", lambda e, b=start_free_btn: b.config(bg=COLORS['blue_600']))

    # ---------- Hero Section ----------
    hero_container = tk.Frame(main_frame, bg=COLORS['white'])
    hero_container.pack(fill="both", expand=True, pady=40)

    # Left side - text content
    left_container = tk.Frame(hero_container, bg=COLORS['white'])
    left_container.pack(side="left", fill="both", expand=True, padx=40)

    # Main heading
    heading = tk.Label(left_container, 
                      text="Parking made\nsimple and automatic",
                      font=('Segoe UI', 32, 'bold'),
                      fg=COLORS['gray_900'],
                      bg=COLORS['white'],
                      justify="left")
    heading.pack(pady=(0, 20), anchor="w")

    # Description
    description = ("ParkInUP uses license plate recognition to track your vehicle "
                  "and calculate fees instantly. No more manual payments or confusion "
                  "about how much you owe.")
    desc_label = tk.Label(left_container, text=description,
                         font=('Segoe UI', 14),
                         fg=COLORS['gray_600'],
                         bg=COLORS['white'],
                         wraplength=500,
                         justify="left")
    desc_label.pack(pady=(0, 30), anchor="w")

    # Buttons container
    buttons_container = tk.Frame(left_container, bg=COLORS['white'])
    buttons_container.pack(anchor="w", pady=(0, 20))

    # Start now button (blue)
    start_now_btn = tk.Button(buttons_container, text="Start now", command=on_start_now,
                            bg=COLORS['blue_600'], fg='white',
                            font=('Segoe UI', 14, 'bold'),
                            relief='flat', bd=0, width=15, height=1, pady=10)
    start_now_btn.pack(side="left", padx=(0, 15), pady=10)
    start_now_btn.bind("<Enter>", lambda e, b=start_now_btn: b.config(bg=COLORS['blue_700']))
    start_now_btn.bind("<Leave>", lambda e, b=start_now_btn: b.config(bg=COLORS['blue_600']))

    # Learn more button
    learn_more_btn = tk.Button(buttons_container, text="Learn more", command=on_learn_more,
                              bg=COLORS['white'], fg=COLORS['gray_700'],
                              font=('Segoe UI', 14, 'bold'),
                              relief='solid', bd=2, width=15, height=1, pady=10)
    learn_more_btn.pack(side="left", padx=(0, 15), pady=10)
    learn_more_btn.bind("<Enter>", lambda e, b=learn_more_btn: b.config(bg=COLORS['gray_100']))
    learn_more_btn.bind("<Leave>", lambda e, b=learn_more_btn: b.config(bg=COLORS['white']))

    # Right side - Features list
    right_container = tk.Frame(hero_container, bg=COLORS['white'])
    right_container.pack(side="right", fill="both", expand=True, padx=40)

    features_list = [
        {
            "title": "Automatic Recognition",
            "desc": "Advanced AI recognizes your vehicle instantly as you enter and exit parking facilities.",
            "icon": "🚗",
            "bg": COLORS['red_100']
        },
        {
            "title": "Instant Payment",
            "desc": "Fees are calculated and charged automatically. No need to stop at payment kiosks.",
            "icon": "💳",
            "bg": COLORS['yellow_100']
        },
        {
            "title": "Time Tracking",
            "desc": "Real-time tracking of parking duration with transparent, itemized billing.",
            "icon": "⏰",
            "bg": COLORS['blue_100']
        }
    ]

    for feat in features_list:
        card = tk.Frame(right_container, bg=COLORS['white'], bd=1, relief="solid", highlightthickness=0)
        card.pack(fill="x", pady=10)
        card.config(highlightbackground=COLORS['gray_200'], highlightthickness=1, bd=0)
        
        inner = tk.Frame(card, bg=COLORS['white'], padx=20, pady=20)
        inner.pack(fill="both")

        icon_frame = tk.Frame(inner, bg=feat['bg'], width=48, height=48)
        icon_frame.pack(side="left", padx=(0, 20))
        icon_frame.pack_propagate(False)
        
        # Making it look circular-ish (Tkinter limitation, but we can use a smaller square with padding)
        tk.Label(icon_frame, text=feat['icon'], font=('Segoe UI', 20), bg=feat['bg']).pack(expand=True)

        text_frame = tk.Frame(inner, bg=COLORS['white'])
        text_frame.pack(side="left", fill="both", expand=True)

        tk.Label(text_frame, text=feat['title'], font=('Segoe UI', 14, 'bold'), 
                 fg=COLORS['gray_900'], bg=COLORS['white'], justify="left").pack(anchor="w")
        
        tk.Label(text_frame, text=feat['desc'], font=('Segoe UI', 10), 
                 fg=COLORS['gray_600'], bg=COLORS['white'], justify="left", wraplength=350).pack(anchor="w")


def create_login_page(root, on_login, on_back):
    """Create the modern React-style login page."""
    # Clear any existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=COLORS['blue_50'])
    
    # Main container
    main_frame = tk.Frame(root, bg=COLORS['blue_50'])
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)

    # Login card
    login_card = tk.Frame(main_frame, bg=COLORS['white'], bd=0)
    login_card.pack(expand=True)

    # Logo
    logo_frame = tk.Frame(login_card, bg=COLORS['white'])
    logo_frame.pack(pady=30)

    if PIL_AVAILABLE_UI:
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "docs", "logo.png")
            if not os.path.exists(logo_path):
                 logo_path = os.path.join(os.path.dirname(__file__), "docs", "logo.png")
            
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((210, 80), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(logo_frame, image=logo_photo, bg=COLORS['white'])
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack()
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback to text
            p_label = tk.Label(logo_frame, text="P", font=('Segoe UI', 32, 'bold'),
                              fg=COLORS['yellow_500'], bg=COLORS['white'])
            p_label.pack(side="left")
            car_label = tk.Label(logo_frame, text="🚗", font=('Segoe UI', 26), bg=COLORS['white'])
            car_label.pack(side="left")
            arkin_label = tk.Label(logo_frame, text="arkin", font=('Segoe UI', 32, 'bold'),
                                  fg=COLORS['red_600'], bg=COLORS['white'])
            arkin_label.pack(side="left")
            bike_label = tk.Label(logo_frame, text="🚲", font=('Segoe UI', 26), bg=COLORS['white'])
            bike_label.pack(side="left")
            up_label = tk.Label(logo_frame, text="UP", font=('Segoe UI', 32, 'bold'),
                               fg=COLORS['yellow_500'], bg=COLORS['white'])
            up_label.pack(side="left")
    else:
        # Fallback to text
        p_label = tk.Label(logo_frame, text="P", font=('Segoe UI', 32, 'bold'),
                          fg=COLORS['yellow_500'], bg=COLORS['white'])
        p_label.pack(side="left")
        car_label = tk.Label(logo_frame, text="🚗", font=('Segoe UI', 26), bg=COLORS['white'])
        car_label.pack(side="left")
        arkin_label = tk.Label(logo_frame, text="arkin", font=('Segoe UI', 32, 'bold'),
                              fg=COLORS['red_600'], bg=COLORS['white'])
        arkin_label.pack(side="left")
        bike_label = tk.Label(logo_frame, text="🚲", font=('Segoe UI', 26), bg=COLORS['white'])
        bike_label.pack(side="left")
        up_label = tk.Label(logo_frame, text="UP", font=('Segoe UI', 32, 'bold'),
                           fg=COLORS['yellow_500'], bg=COLORS['white'])
        up_label.pack(side="left")

    # Welcome message
    welcome_label = tk.Label(login_card, text="Welcome back",
                            font=('Segoe UI', 24, 'bold'),
                            fg=COLORS['gray_900'], bg=COLORS['white'])
    welcome_label.pack(pady=(10, 5))

    sub_label = tk.Label(login_card, text="Sign in to manage your parking",
                        font=('Segoe UI', 12),
                        fg=COLORS['gray_600'], bg=COLORS['white'])
    sub_label.pack(pady=(0, 30))

    # Email field
    email_frame = tk.Frame(login_card, bg=COLORS['white'])
    email_frame.pack(pady=10, padx=40, fill="x")

    tk.Label(email_frame, text="Email address",
            font=('Segoe UI', 11),
            fg=COLORS['gray_700'], bg=COLORS['white']).pack(anchor="w")

    email_entry = tk.Entry(email_frame, font=('Segoe UI', 11),
                          bg=COLORS['white'], relief='solid', bd=2)
    email_entry.pack(fill="x", pady=5, ipady=8)
    email_entry.insert(0, "you@example.com")

    # Password field
    password_frame = tk.Frame(login_card, bg=COLORS['white'])
    password_frame.pack(pady=10, padx=40, fill="x")

    tk.Label(password_frame, text="Password",
            font=('Segoe UI', 11),
            fg=COLORS['gray_700'], bg=COLORS['white']).pack(anchor="w")

    password_entry = tk.Entry(password_frame, font=('Segoe UI', 11),
                             bg=COLORS['white'], relief='solid', bd=2, show="•")
    password_entry.pack(fill="x", pady=5, ipady=8)
    password_entry.insert(0, "••••••••")

    # Remember me and Forgot password
    options_frame = tk.Frame(login_card, bg=COLORS['white'])
    options_frame.pack(pady=15, padx=40, fill="x")

    check_var = tk.IntVar()
    check_btn = tk.Checkbutton(options_frame, text="Remember me",
                              variable=check_var,
                              font=('Segoe UI', 11),
                              fg=COLORS['gray_600'], bg=COLORS['white'],
                              activebackground=COLORS['white'],
                              selectcolor=COLORS['white'])
    check_btn.pack(side="left")

    forgot_btn = tk.Button(options_frame, text="Forgot password?",
                          command=lambda: None,
                          font=('Segoe UI', 11),
                          fg=COLORS['blue_600'], bg=COLORS['white'],
                          relief='flat', bd=0)
    forgot_btn.pack(side="right")

    # Sign in button
    login_btn = tk.Button(login_card, text="Sign in", command=on_login,
                         bg=COLORS['blue_600'], fg='white',
                         font=('Segoe UI', 12, 'bold'),
                         relief='flat', bd=0, width=40, pady=10)
    login_btn.pack(pady=20, padx=40)
    login_btn.bind("<Enter>", lambda e, b=login_btn: b.config(bg=COLORS['blue_700']))
    login_btn.bind("<Leave>", lambda e, b=login_btn: b.config(bg=COLORS['blue_600']))

    # Sign up link
    signup_frame = tk.Frame(login_card, bg=COLORS['white'])
    signup_frame.pack(pady=10)

    tk.Label(signup_frame, text="Don't have an account?",
            font=('Segoe UI', 11),
            fg=COLORS['gray_600'], bg=COLORS['white']).pack(side="left")

    signup_btn = tk.Button(signup_frame, text="Sign up", command=lambda: None,
                          font=('Segoe UI', 11, 'bold'),
                          fg=COLORS['blue_600'], bg=COLORS['white'],
                          relief='flat', bd=0)
    signup_btn.pack(pady=5)
    signup_btn.bind("<Enter>", lambda e, b=signup_btn: b.config(fg=COLORS['blue_700']))
    signup_btn.bind("<Leave>", lambda e, b=signup_btn: b.config(fg=COLORS['blue_600']))

    # Back button
    back_btn = tk.Button(login_card, text="← Back", command=on_back,
                        font=('Segoe UI', 11),
                        fg=COLORS['gray_600'], bg=COLORS['white'],
                        relief='flat', bd=0)
    back_btn.pack(pady=20)
    back_btn.bind("<Enter>", lambda e, b=back_btn: b.config(fg=COLORS['gray_900']))
    back_btn.bind("<Leave>", lambda e, b=back_btn: b.config(fg=COLORS['gray_600']))

def show_parking_slots_overview(parent, slots_data):
    """Create a modal to view all parking slots and their status."""
    modal = tk.Toplevel(parent)
    modal.title("Parking Slots Overview")
    modal.geometry("600x700")
    modal.configure(bg=COLORS['white'])
    modal.resizable(False, False)
    modal.transient(parent)
    modal.grab_set()

    # Header
    header_frame = tk.Frame(modal, bg=COLORS['white'], padx=30, pady=20)
    header_frame.pack(fill="x")

    tk.Label(header_frame, text="Parking Slots Overview",
             font=('Segoe UI', 18, 'bold'), fg=COLORS['gray_900'],
             bg=COLORS['white']).pack(anchor="w")
    
    tk.Label(header_frame, text="View all parking slots and their availability status",
             font=('Segoe UI', 11), fg=COLORS['gray_500'],
             bg=COLORS['white']).pack(anchor="w")

    # Grid Container
    grid_container = tk.Frame(modal, bg=COLORS['white'], padx=30, pady=10)
    grid_container.pack(fill="both", expand=True)

    # 4x5 Grid
    for i, slot in enumerate(slots_data):
        row = i // 5
        col = i % 5
        
        # Exact colors from mockup
        COLOR_AVAILABLE = "#10b981"    # Emerald 500
        COLOR_BG_AVAILABLE = "#ecfdf5" # Emerald 50
        COLOR_OCCUPIED = "#ef4444"     # Red 500
        COLOR_BG_OCCUPIED = "#fef2f2"  # Red 50

        status_color = COLOR_AVAILABLE if not slot['occupied'] else COLOR_OCCUPIED
        bg_color = COLOR_BG_AVAILABLE if not slot['occupied'] else COLOR_BG_OCCUPIED
        
        card = tk.Frame(grid_container, bg=bg_color, highlightbackground=status_color,
                        highlightthickness=1, padx=10, pady=15)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
        
        tk.Label(card, text="Slot", font=('Segoe UI', 9),
                 fg=status_color, bg=bg_color).pack()
        
        tk.Label(card, text=slot['number'], font=('Segoe UI', 18, 'bold'),
                 fg=status_color, bg=bg_color).pack(pady=2)
        
        status_text = "Available" if not slot['occupied'] else "Occupied"
        tk.Label(card, text=status_text, font=('Segoe UI', 9),
                 fg=status_color, bg=bg_color).pack()

    # Footer with Legend and Close Button
    footer_frame = tk.Frame(modal, bg=COLORS['white'], padx=30, pady=20)
    footer_frame.pack(fill="x")

    # Legend
    legend_frame = tk.Frame(footer_frame, bg=COLORS['white'])
    legend_frame.pack(side="left")

    # Available Legend
    tk.Frame(legend_frame, bg="#ecfdf5", width=15, height=15, 
             highlightthickness=1, highlightbackground="#10b981").pack(side="left", padx=(0, 5))
    tk.Label(legend_frame, text="Available", font=('Segoe UI', 10),
             fg=COLORS['gray_700'], bg=COLORS['white']).pack(side="left", padx=(0, 15))

    # Occupied Legend
    tk.Frame(legend_frame, bg="#fef2f2", width=15, height=15,
             highlightthickness=1, highlightbackground="#ef4444").pack(side="left", padx=(0, 5))
    tk.Label(legend_frame, text="Occupied", font=('Segoe UI', 10),
             fg=COLORS['gray_700'], bg=COLORS['white']).pack(side="left")

    # Close Button
    close_btn = tk.Button(footer_frame, text="Close", command=modal.destroy,
                          bg=COLORS['gray_900'], fg='white',
                          font=('Segoe UI', 11, 'bold'),
                          relief='flat', bd=0, padx=20, pady=8)
    close_btn.pack(side="right")
    close_btn.bind("<Enter>", lambda e, b=close_btn: b.config(bg=COLORS['gray_700']))
    close_btn.bind("<Leave>", lambda e, b=close_btn: b.config(bg=COLORS['gray_900']))
