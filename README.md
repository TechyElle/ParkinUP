# ParkinUP

## Quick start (Windows)

This project depends on `opencv-python`, which in turn depends on NumPy. On Windows, NumPy is easiest to install via prebuilt wheels, so use a stable Python version (recommended: Python 3.12 64-bit).

1) Create & activate a virtualenv

```powershell
cd "c:\Users\CM\OneDrive\Desktop\PLD_FinalProject_Group#_ParkinUP"
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies

```powershell
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
```

3) Run

```powershell
python .\ParkinUP_Project\main.py
```

## Troubleshooting

NumPy build errors / missing compiler

If pip tries to build NumPy from source and errors about missing compilers / Visual Studio tools, you are likely using a Python version that doesn’t have NumPy wheels available yet.

Fix: use Python 3.12 (recommended) and recreate the venv.

If you must stay on that Python version, install Visual Studio Build Tools (Desktop development with C++ / MSVC + Windows SDK), then retry.
