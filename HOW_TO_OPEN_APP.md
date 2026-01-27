# 🚨 IMPORTANT: How to Open the Application

## ❌ WRONG WAY (Causes "file://" Error)

**DO NOT:**
- Double-click `index.html` file
- Open file directly from file explorer
- Use `file:///` protocol

**This causes errors like:**
```
Network error: Failed to parse URL from file://:8000/api/auth/signup
```

---

## ✅ CORRECT WAY

### Step 1: Start Frontend Server

**Open Terminal/Command Prompt:**
```bash
cd frontend
python server.py
```

**You should see:**
```
Frontend Server: http://localhost:3000/index.html
```

### Step 2: Open in Browser

**Open your browser and go to:**
```
http://localhost:3000/index.html
```

**NOT:**
- ❌ `file:///C:/Users/.../index.html`
- ❌ Double-clicking the HTML file
- ❌ Opening from file explorer

---

## 🔍 How to Check if You're Using the Right URL

### ✅ Correct URL (HTTP):
```
http://localhost:3000/index.html
```
- Starts with `http://` or `https://`
- Has `localhost:3000` or your server address
- Works with API calls

### ❌ Wrong URL (File):
```
file:///C:/Users/.../index.html
```
- Starts with `file://`
- Has your file system path
- **Won't work** with API calls

---

## 🛠️ Quick Fix

### If You See "file://" Error:

1. **Close the current browser tab**
2. **Make sure frontend server is running:**
   ```bash
   cd frontend
   python server.py
   ```
3. **Open browser and type:**
   ```
   http://localhost:3000/index.html
   ```

---

## 📋 Complete Startup Checklist

### Terminal 1 - Backend:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend:
```bash
cd frontend
python server.py
```

### Browser:
```
http://localhost:3000/index.html
```

---

## 🐛 Troubleshooting

### Error: "file://:8000/api/auth/signup"

**Cause:** Opened HTML file directly

**Solution:**
1. Close the browser tab
2. Start frontend server: `cd frontend && python server.py`
3. Open: `http://localhost:3000/index.html`

### Error: "Failed to fetch"

**Cause:** Backend not running or wrong URL

**Solution:**
1. Check backend is running: `curl http://localhost:8000/`
2. Check browser console (F12) for API URL
3. Should see: `API URL: http://localhost:8000`

### Error: "Port 3000 already in use"

**Cause:** Another server using port 3000

**Solution:**
1. Close other server
2. Or change PORT in `frontend/server.py`

---

## ✅ Verification

### Check Browser Console (F12):
- Should see: `🌐 API URL: http://localhost:8000`
- Should see: `✅ Backend connection successful`
- Should NOT see: `file://` anywhere

### Check URL Bar:
- Should show: `http://localhost:3000/index.html`
- Should NOT show: `file:///...`

---

## 🎯 Summary

**ALWAYS use:**
```
http://localhost:3000/index.html
```

**NEVER use:**
```
file:///C:/Users/.../index.html
```

The application **must** be served by the HTTP server, not opened directly as a file!
