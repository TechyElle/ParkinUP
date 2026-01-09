---
description: Repository Information Overview
alwaysApply: true
---

# ParkinUP Information

## Summary
ParkinUP is an automated parking management system built with Python and Tkinter. It features a modern user interface, license plate recognition (OCR) capabilities, and an integrated SQLite database to manage parking slots, vehicle entries, and payments.

## Structure
- **ParkinUP_Project/**: Contains the main application source code.
    - `main.py`: Entry point for the application, handling database initialization and core logic.
    - `ui.py`: Modern React-inspired UI components and styling.
    - `utils.py`: Business logic for OCR, fee calculations, and database helpers.
    - `simulate_receipt.py`: Utility for generating and displaying parking receipts.
- **docs/**: Documentation and visual assets including flowcharts and logos.
- **.venv/**: Python virtual environment for dependency management.

## Language & Runtime
**Language**: Python  
**Version**: 3.14.2 (Detected), 3.12 (Recommended)  
**Build System**: N/A (Script-based execution)  
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- `opencv-python`: Camera integration and image processing.
- `Pillow`: Image handling for the GUI and OCR preprocessing.
- `pytesseract`: Optical Character Recognition for license plate detection.
- `sqlite3`: Built-in database engine for managing persistent data.
- `tkinter`: Built-in GUI framework for the application.

## Build & Installation
```bash
# 1) Create and activate a virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\Activate.ps1

# 2) Install dependencies
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt

# 3) Run the application
python .\ParkinUP_Project\main.py
```

## Main Files & Resources
- **Entry Point**: `ParkinUP_Project/main.py`
- **Database**: `ParkinUP_Project/parking.db` (SQLite)
- **UI Definitions**: `ParkinUP_Project/ui.py`
- **Helper Utilities**: `ParkinUP_Project/utils.py`

## Testing & Validation
The project includes a simulation script for validating receipt generation and fee calculation:
```bash
python .\ParkinUP_Project\simulate_receipt.py
```
This script tests the database interaction, duration calculation, and the UI receipt layout.
