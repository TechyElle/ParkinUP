# Technical Specification: Parking Slots Overview

## Technical Context
- **Language**: Python 3.x
- **GUI Framework**: Tkinter
- **Database**: SQLite3
- **Dependencies**: `Pillow` (for potential image handling, already used in project)

## Technical Implementation Brief
- Implement a modal using `tk.Toplevel`.
- Use a 4x5 grid layout using `tk.Frame` for each slot card.
- Each card will display "Slot [number]" and its status.
- Colors will be derived from the existing `COLORS` palette in `ui.py`:
  - `green_500` (#22c55e) for Available background/border.
  - `red_500` (#ef4444) for Occupied background/border.
  - White background for the card.
- The modal will be non-resizable and modal (using `grab_set()`).

## Source Code Structure
- **`ParkinUP_Project/ui.py`**:
  - Add `ParkingSlotsModal` class or `show_parking_slots_overview` function.
  - Define styles for the slot cards (rounded corners if possible via images or just standard frames).
- **`ParkinUP_Project/main.py`**:
  - Update `create_dashboard` (or equivalent) to add a button for "Parking Slots Overview".
  - Implement the callback to fetch data and show the modal.

## Contracts
### Database
- Table: `slots`
- Query: `SELECT slot_number, is_occupied FROM slots ORDER BY slot_id ASC LIMIT 20`

### UI Function
- `show_parking_slots_overview(parent, slots_data)`:
  - `parent`: The root or current frame.
  - `slots_data`: List of dictionaries `{'number': str, 'occupied': bool}`.

## Delivery Phases
1. **Phase 1: UI Prototype**: Static modal with 20 dummy slots in 4x5 grid.
2. **Phase 2: Data Wiring**: Fetch real slot data from `parking.db`.
3. **Phase 3: Integration**: Add the "View Parking Slots" button to the Dashboard.

## Verification Strategy
- **Visual Check**: Compare the rendered modal with `docs/viewslots.png`.
- **Functionality**:
  - Open modal -> Close modal.
  - Toggle a slot in DB -> Reopen modal -> Check status change.
- **Automated Check**:
  - `python ParkinUP_Project/main.py` (Manual verification)
  - Ensure no new console errors are logged.
