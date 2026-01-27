#!/bin/bash
# Auto-generated fix script for Linux/Mac

echo "========================================"
echo "  SKILL GAP ANALYZER - FIX ALL ERRORS"
echo "========================================"
echo ""

echo "[1/4] Installing dependencies..."
cd backend
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[2/4] Checking MongoDB connection..."
# Add MongoDB check here if needed

echo ""
echo "[3/4] Initializing dataset..."
python scripts/init_dataset.py --dataset data/raw/job_dataset.csv
if [ $? -ne 0 ]; then
    echo "WARNING: Dataset initialization failed"
    echo "Make sure MongoDB is running and dataset file exists"
fi

echo ""
echo "[4/4] Done!"
echo ""
echo "========================================"
echo "  NEXT STEPS:"
echo "========================================"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend"
echo "  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  python server.py"
echo ""
echo "Browser:"
echo "  http://localhost:3000/index.html"
echo ""
