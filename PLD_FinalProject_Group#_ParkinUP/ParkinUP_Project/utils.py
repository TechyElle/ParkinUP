import os
import sqlite3
from datetime import datetime

# Optional OCR lib
pytesseract = None
try:
    import pytesseract
except ImportError:
    pass

PIL_Image = None
try:
    from PIL import Image
    PIL_Image = Image
except ImportError:
    pass


def init_db(db_path: str, total_slots: int = 20):
    """Ensure DB tables exist and seed a default number of slots if none present."""
    conn = sqlite3.connect(db_path)
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
    # Seed slots if none exist
    cur.execute("SELECT COUNT(*) FROM slots")
    count = cur.fetchone()[0] or 0
    if count == 0 and total_slots > 0:
        for i in range(1, total_slots + 1):
            slot_name = f"Slot-{i}"
            cur.execute("INSERT OR IGNORE INTO slots (slot_number, is_occupied) VALUES (?, 0)", (slot_name,))
    conn.commit()
    conn.close()


def calculate_fee(entry_time_str: str, exit_time_str: str | None = None, rate_per_min: float = 10/60):
    """Return (minutes, amount). If exit_time_str is None uses now."""
    entry_dt = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S")
    if exit_time_str:
        exit_dt = datetime.strptime(exit_time_str, "%Y-%m-%d %H:%M:%S")
    else:
        exit_dt = datetime.now()
    minutes = int((exit_dt - entry_dt).total_seconds() / 60)
    minutes = max(1, minutes)
    amount = round(minutes * rate_per_min, 2)
    return minutes, amount


def format_currency(amount: float, symbol: str = "P") -> str:
    return f"{symbol}{round(amount,2)}"


def parse_plate_from_filename(path: str) -> str:
    """Try to parse an alphanumeric plate-like token from a filename.
    Returns a placeholder if none found."""
    name = os.path.basename(path)
    # common naming like plate_ABC123.jpg or IMG_ABC123.png
    import re
    m = re.search(r"([A-Z0-9]{3,}-?[A-Z0-9]{2,})", name.upper())
    if m:
        return m.group(1).replace('-', '')
    # fallback: return filename without extension
    return os.path.splitext(name)[0]


def ocr_stub(image_path: str | None = None) -> str:
    """OCR using pytesseract if available, else simulated: if image_path provided, try to extract a token from filename.
    Otherwise return a deterministic simulated plate string.
    """
    if pytesseract is not None and PIL_Image is not None and image_path:
        try:
            img = PIL_Image.open(image_path)
            text = pytesseract.image_to_string(img)
            # Extract alphanumeric text that looks like a plate
            import re
            matches = re.findall(r'[A-Z0-9]{3,}', text.upper())
            for match in matches:
                if any(c.isdigit() for c in match):
                    return match
        except Exception:
            pass
    # Fallback to filename parsing or simulation
    if image_path:
        try:
            plate = parse_plate_from_filename(image_path)
            return plate
        except Exception:
            pass
    # deterministic simulated plate using timestamp
    ts = datetime.now().strftime("%H%M%S")
    return f"SIM{ts}"
