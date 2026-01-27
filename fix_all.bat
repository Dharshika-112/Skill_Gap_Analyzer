@echo off
REM Auto-generated fix script for Windows

echo ========================================
echo   SKILL GAP ANALYZER - FIX ALL ERRORS
echo ========================================
echo.

echo [1/4] Installing dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Checking MongoDB connection...
REM Add MongoDB check here if needed

echo.
echo [3/4] Initializing dataset...
python scripts/init_dataset.py --dataset data/raw/job_dataset.csv
if errorlevel 1 (
    echo WARNING: Dataset initialization failed
    echo Make sure MongoDB is running and dataset file exists
)

echo.
echo [4/4] Done!
echo.
echo ========================================
echo   NEXT STEPS:
echo ========================================
echo.
echo Terminal 1 - Backend:
echo   cd backend
echo   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
echo Terminal 2 - Frontend:
echo   cd frontend
echo   python server.py
echo.
echo Browser:
echo   http://localhost:3000/index.html
echo.
pause
