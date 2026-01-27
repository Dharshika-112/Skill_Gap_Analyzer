# 🔧 Fixed Network Errors & Dataset Issues

## ✅ What Was Fixed

### 1. **Network Error Fixes**
- ✅ Better API URL detection (handles localhost, 127.0.0.1, and custom ports)
- ✅ Detailed error messages showing actual error instead of generic "Network error"
- ✅ Console logging for debugging
- ✅ Backend connection test on page load
- ✅ Better error handling for failed requests

### 2. **Dataset Normalization Fixes**
- ✅ Properly handles semicolon-separated skills (`;`) from your CSV
- ✅ Better skill name normalization (preserves proper capitalization)
- ✅ Improved parsing for various skill formats
- ✅ Auto-detects dataset file location

---

## 🚀 Quick Fix Steps

### Step 1: Make Sure Backend is Running

**Terminal 1:**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**You should see:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
[*] Initializing database...
[OK] Database initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Make Sure Frontend is Running

**Terminal 2:**
```bash
cd frontend
python server.py
```

**You should see:**
```
Frontend Server: http://localhost:3000/index.html
```

### Step 3: Initialize Dataset (If Not Done)

```bash
cd backend
python scripts/init_dataset.py --dataset data/raw/job_dataset.csv
```

---

## 🐛 Troubleshooting

### Error: "Network error: Failed to fetch"

**Causes:**
1. Backend not running
2. Wrong API URL
3. CORS issues
4. Port mismatch

**Solutions:**

1. **Check Backend is Running:**
   ```bash
   # Test backend directly
   curl http://localhost:8000/
   # Should return: {"message": "Skill Gap Analyzer API v2.0", ...}
   ```

2. **Check Browser Console:**
   - Open browser DevTools (F12)
   - Go to Console tab
   - Look for: `API URL: http://localhost:8000`
   - Look for: `✅ Backend connection successful` or `❌ Backend connection failed`

3. **Verify Ports:**
   - Backend: `http://localhost:8000`
   - Frontend: `http://localhost:3000`
   - If using different ports, update `frontend/static/app.js` API_URL

4. **Check CORS:**
   - Backend already has CORS enabled (`allow_origins=["*"]`)
   - If still issues, check browser console for CORS errors

### Error: "Server error: 500" or "Server error: 404"

**Causes:**
1. Backend endpoint not found
2. Backend error
3. Missing dependencies

**Solutions:**

1. **Check Backend Logs:**
   - Look at Terminal 1 (backend) for error messages
   - Common errors:
     - MongoDB connection failed
     - Missing module (install with `pip install -r requirements.txt`)
     - Dataset not initialized

2. **Test API Endpoints:**
   ```bash
   # Test health check
   curl http://localhost:8000/
   
   # Test auth endpoint
   curl -X POST http://localhost:8000/api/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"name":"Test","email":"test@test.com","password":"test123"}'
   ```

3. **Check MongoDB:**
   ```bash
   # Test MongoDB connection
   mongosh
   # Or if using MongoDB Atlas, check connection string in backend/.env
   ```

### Error: "Upload failed: Failed to fetch"

**Causes:**
1. Backend not running
2. File too large
3. Wrong file format
4. Missing authorization token

**Solutions:**

1. **Check Backend is Running** (see above)

2. **Check File Format:**
   - Supported: PDF, DOCX, TXT
   - Check file extension matches

3. **Check Authorization:**
   - Make sure you're logged in
   - Token should be in browser localStorage (check DevTools → Application → Local Storage)

4. **Check File Size:**
   - Try smaller file first
   - Check backend logs for file size errors

---

## 📊 Dataset Normalization

### Your CSV Format
Your dataset uses **semicolon-separated** skills:
```
Skills: C#; VB.NET basics; .NET Framework; ASP.NET; MVC; HTML; CSS
```

### What Was Fixed
- ✅ Parser now handles semicolons (`;`) correctly
- ✅ Also handles commas (`,`), pipes (`|`), and slashes (`/`)
- ✅ Proper capitalization (C# → C#, JavaScript → JavaScript)
- ✅ Normalizes common abbreviations (JS → JavaScript, SQL → SQL)

### Verify Dataset Loaded

**Check MongoDB:**
```bash
mongosh
use skill_gap_analyzer
db.dataset_skills.countDocuments()
db.dataset_roles.countDocuments()
```

**Or check API:**
```bash
curl http://localhost:8000/api/data/skills | head -20
curl http://localhost:8000/api/data/roles | head -20
```

---

## 🔍 Debugging Tips

### 1. Open Browser Console (F12)
- Check for error messages
- Look for `API URL:` log
- Check network tab for failed requests

### 2. Check Backend Logs
- All errors are printed to terminal
- Look for `[ERROR]` messages
- Check startup messages

### 3. Test API Directly
```bash
# Health check
curl http://localhost:8000/

# List skills
curl http://localhost:8000/api/data/skills

# List roles
curl http://localhost:8000/api/data/roles
```

### 4. Check MongoDB Collections
```bash
mongosh
use skill_gap_analyzer
show collections
db.dataset_skills.findOne()
db.dataset_roles.findOne()
```

---

## ✅ Verification Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] MongoDB running (local or cloud)
- [ ] Dataset initialized (`python scripts/init_dataset.py`)
- [ ] Browser console shows: `✅ Backend connection successful`
- [ ] Can access: `http://localhost:8000/`
- [ ] Can access: `http://localhost:3000/index.html`

---

## 🎯 Test Flow

1. **Open:** `http://localhost:3000/index.html`
2. **Check Console:** Should see `✅ Backend connection successful`
3. **Sign Up:** Create account
4. **Check Error Messages:** Should show detailed errors if something fails
5. **Upload Resume:** Should work if backend is running
6. **Select Role:** Should load roles from MongoDB

---

## 📝 Common Error Messages & Solutions

| Error Message | Solution |
|--------------|----------|
| `Network error: Failed to fetch` | Backend not running - start it |
| `Server error: 500` | Check backend logs for details |
| `Server error: 404` | Endpoint not found - check API URL |
| `MongoDB connection failed` | Start MongoDB or check connection string |
| `Dataset not found` | Run `python scripts/init_dataset.py` |
| `Missing token` | Login first before accessing protected routes |

---

## 🚀 Quick Test Commands

```bash
# Test backend
curl http://localhost:8000/

# Test skills endpoint
curl http://localhost:8000/api/data/skills

# Test signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@test.com","password":"test123"}'
```

---

Your application should now work correctly! 🎉

If you still see errors, check:
1. Browser console (F12)
2. Backend terminal logs
3. MongoDB connection
4. Dataset initialization
