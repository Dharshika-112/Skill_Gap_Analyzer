# 🔧 Fix All Terminal Errors - Step by Step

## ✅ Errors Found & Fixed

### Error 1: Missing SECRET_KEY ✅ FIXED
**Error:**
```
ImportError: cannot import name 'SECRET_KEY' from 'core.config'
```

**Fix Applied:** Added SECRET_KEY to `backend/app/core/config.py`

---

### Error 2: scikit-learn Build Error ✅ FIXED
**Error:**
```
Microsoft Visual C++ 14.0 or greater is required
```

**Fix Applied:** Updated to scikit-learn>=1.4.0 (has pre-built wheels for Python 3.13)

---

### Error 3: Path Navigation Issues ✅ FIXED
**Error:**
```
Cannot find path 'C:\Users\...\backend\frontend'
```

**Fix:** Use correct paths (see below)

---

## 🚀 Quick Fix Commands

### Step 1: Fix SECRET_KEY (Already Fixed)
The SECRET_KEY has been added to config.py. No action needed.

### Step 2: Install Updated Dependencies

**From project root:**
```powershell
cd backend
pip install --upgrade scikit-learn>=1.4.0
pip install -r requirements.txt
```

**OR install without scikit-learn first, then upgrade:**
```powershell
cd backend
pip install fastapi uvicorn pymongo pydantic pydantic-settings python-jose passlib bcrypt python-multipart numpy pandas python-dotenv pdfminer.six python-docx
pip install --upgrade scikit-learn
```

### Step 3: Test Backend

**From project root:**
```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Start Frontend (NEW TERMINAL)

**From project root (NOT from backend folder!):**
```powershell
cd frontend
python server.py
```

**Should see:**
```
Frontend Server: http://localhost:3000/index.html
```

---

## 📋 Correct Directory Structure

```
Skill_Gap_Analyser/
├── backend/
│   ├── app/
│   ├── data/
│   ├── scripts/
│   └── requirements.txt
├── frontend/
│   ├── static/
│   ├── index.html
│   └── server.py
└── (root files)
```

---

## 🔍 Common Path Mistakes

### ❌ WRONG:
```powershell
PS backend> cd frontend  # Can't go to frontend from backend!
PS backend> cd backend   # Already in backend!
```

### ✅ CORRECT:
```powershell
# Start from project root
PS Skill_Gap_Analyser> cd backend
PS Skill_Gap_Analyser\backend> python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# NEW TERMINAL - Start from project root again
PS Skill_Gap_Analyser> cd frontend
PS Skill_Gap_Analyser\frontend> python server.py
```

---

## 🛠️ Alternative: Install Pre-built scikit-learn

If scikit-learn still fails, install pre-built wheel:

```powershell
pip install scikit-learn --only-binary :all:
```

Or use conda:
```powershell
conda install scikit-learn
```

---

## ✅ Verification Steps

### 1. Check SECRET_KEY exists:
```powershell
python -c "from backend.app.core.config import SECRET_KEY; print('OK')"
```

### 2. Check scikit-learn installed:
```powershell
python -c "import sklearn; print(sklearn.__version__)"
```

### 3. Test backend import:
```powershell
cd backend
python -c "from app.main import app; print('Backend OK')"
```

### 4. Test frontend:
```powershell
cd frontend
python -c "import server; print('Frontend OK')"
```

---

## 🎯 Complete Startup Sequence

### Terminal 1 - Backend:
```powershell
# Start from project root
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend:
```powershell
# Start from project root (NEW terminal)
cd frontend
python server.py
```

### Browser:
```
http://localhost:3000/index.html
```

---

## 🐛 If scikit-learn Still Fails

### Option 1: Install Visual C++ Build Tools
Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Option 2: Use Pre-built Wheel
```powershell
pip install --upgrade pip
pip install scikit-learn --only-binary :all:
```

### Option 3: Use Conda
```powershell
conda install scikit-learn
```

### Option 4: Skip scikit-learn (if not critical)
Comment out scikit-learn in requirements.txt temporarily:
```python
# scikit-learn>=1.4.0  # Comment this if build fails
```

---

## ✅ All Fixed!

After running the fixes above:
1. ✅ SECRET_KEY added to config
2. ✅ scikit-learn version updated
3. ✅ Path navigation corrected

Your application should now start successfully! 🎉
