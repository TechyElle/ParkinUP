# ParkinUP Pseudocode

This pseudocode describes the main flows: vehicle entry (park), vehicle exit (pay), and OCR detection (simulated).

## Park Vehicle

1. Display `Park Vehicle` dialog
2. Read `owner_name`, `vehicle_number`
3. If `vehicle_number` is empty: show warning and abort
4. Connect to DB
5. Find first available slot (is_occupied=0)
6. If no slot: show error "No available slots" and abort
7. Insert vehicle record with entry_time = now
8. Mark slot as occupied
9. Commit and close DB
10. Show success message with slot number
11. Refresh main table

## Exit Vehicle

1. Display `Exit Vehicle` dialog
2. Read `vehicle_number`
3. If empty: show warning and abort
4. Connect to DB
5. Find active vehicle record (exit_time IS NULL) by vehicle_number
6. If not found: show error and abort
7. Compute duration = now - entry_time (minutes)
8. Calculate amount = duration * rate_per_min
9. Update vehicle.exit_time = now
10. Set slot.is_occupied = 0
11. Insert payment record with amount and payment_time
12. Commit and close DB
13. Show payment receipt dialog
14. Refresh main table

## OCR Detection (Simulated)

1. User selects image file or enters plate manually
2. If image selected: `ocr_stub(image_path)` attempts to parse a token from filename
3. If detection returns plate: pre-fill `Park Vehicle` dialog with detected plate
4. If manual input: pre-fill `Park Vehicle` dialog with manual plate

