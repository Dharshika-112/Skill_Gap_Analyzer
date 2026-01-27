# 🔍 Check All Terminal Errors

## Quick Diagnostic

Run this command to check all common errors:

```bash
python diagnose_errors.py
```

This will check:
- ✅ Python version
- ✅ All dependencies installed
- ✅ Backend file structure
- ✅ Frontend file structure
- ✅ MongoDB connection
- ✅ Dataset file exists
- ✅ Ports available
- ✅ Backend imports work

---

## Common Errors & Fixes

### Error: "ModuleNotFoundError: No module named 'X'"

**Fix:**
```bash
cd backend
pip install -r requirements.txt
```

**Or install specific package:**
```bash
pip install fastapi uvicorn pymongo pydantic passlib bcrypt python-jose scikit-learn numpy pandas python-dotenv pdfminer.six python-docx
```

---

### Error: "MongoDB connection failed"

**Fix:**

1. **If using local MongoDB:**
   ```bash
   # Start MongoDB
   mongod
   ```

2. **If using MongoDB Atlas:**
   - Check connection string in `backend/.env`
   - Format: `mongodb+srv://user:pass@cluster.mongodb.net/dbname`

3. **Check connection:**
   ```bash
   mongosh
   # Or
   mongo
   ```

---

### Error: "Dataset file not found"

**Fix:**
```bash
# Make sure file exists
ls backend/data/raw/job_dataset.csv

# Initialize dataset
cd backend
python scripts/init_dataset.py --dataset data/raw/job_dataset.csv
```

---

### Error: "Port 8000 already in use"

**Fix:**

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Or change port in backend:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

---

### Error: "Port 3000 already in use"

**Fix:**

**Windows:**
```bash
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:3000 | xargs kill -9
```

**Or change port in `frontend/server.py`:**
```python
PORT = 3001  # Change this
```

---

### Error: "ImportError: cannot import name 'X'"

**Fix:**

1. **Check file exists:**
   ```bash
   ls backend/app/api/routes/auth.py
   ```

2. **Check Python path:**
   ```bash
   cd backend
   python -c "from app.main import app; print('OK')"
   ```

3. **Reinstall dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

---

### Error: "FileNotFoundError: dataset not found"

**Fix:**

1. **Check file location:**
   ```bash
   ls backend/data/raw/job_dataset.csv
   ```

2. **Use absolute path:**
   ```bash
   python scripts/init_dataset.py --dataset "C:/full/path/to/job_dataset.csv"
   ```

---

### Error: "SyntaxError" or "IndentationError"

**Fix:**

1. **Check Python version:**
   ```bash
   python --version  # Should be 3.8+
   ```

2. **Check file encoding:**
   - Make sure files are UTF-8 encoded
   - No BOM (Byte Order Mark)

---

### Error: "Permission denied" (Linux/Mac)

**Fix:**
```bash
chmod +x scripts/*.py
chmod +x diagnose_errors.py
chmod +x test_endpoints.py
```

---

## Auto-Fix Script

### Windows:
```bash
fix_all.bat
```

### Linux/Mac:
```bash
bash fix_all.sh
```

This will:
1. Install all dependencies
2. Check MongoDB
3. Initialize dataset
4. Show next steps

---

## Manual Step-by-Step Fix

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Check MongoDB
```bash
# Test connection
mongosh
# Or check .env file
cat backend/.env
```

### Step 3: Initialize Dataset
```bash
cd backend
python scripts/init_dataset.py --dataset data/raw/job_dataset.csv
```

### Step 4: Test Backend
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 5: Test Frontend
```bash
cd frontend
python server.py
```

### Step 6: Test Endpoints
```bash
python test_endpoints.py
```

---

## Share Your Errors

If you still have errors, share:

1. **Full error message** from terminal
2. **What command** you ran
3. **Output of diagnostic:**
   ```bash
   python diagnose_errors.py
   ```

This will help identify the exact issue!

---

## Quick Test Commands

```bash
# Test Python
python --version

# Test imports
python -c "import fastapi; print('OK')"

# Test MongoDB
mongosh --eval "db.version()"

# Test backend
curl http://localhost:8000/

# Test frontend
curl http://localhost:3000/
```

---

Run `python diagnose_errors.py` to check everything automatically! 🔍
