# 🚀 START HERE - Quick Fix for "file://" Error

## ❌ The Problem

You're seeing this error:
```
Network error: Failed to parse URL from file://:8000/api/auth/signup
```

**This happens when you open the HTML file directly instead of using the HTTP server.**

---

## ✅ The Solution (3 Steps)

### Step 1: Start Backend Server

**Open Terminal/Command Prompt:**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Wait for:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start Frontend Server

**Open NEW Terminal/Command Prompt:**
```bash
cd frontend
python server.py
```

**Wait for:**
```
Frontend Server: http://localhost:3000/index.html
```

### Step 3: Open in Browser

**Open your browser and type:**
```
http://localhost:3000/index.html
```

**OR click this link:** [http://localhost:3000/index.html](http://localhost:3000/index.html)

---

## ⚠️ IMPORTANT

### ✅ DO THIS:
- Use `http://localhost:3000/index.html`
- Make sure both servers are running
- Check browser console (F12) for errors

### ❌ DON'T DO THIS:
- Don't double-click `index.html` file
- Don't open file from file explorer
- Don't use `file:///` protocol

---

## 🧪 Test if Everything Works

### Quick Test:
```bash
# Test backend
curl http://localhost:8000/

# Test frontend (should see HTML)
curl http://localhost:3000/index.html
```

### Full Test:
```bash
python test_endpoints.py
```

---

## 🐛 Still Having Issues?

### Check Browser Console (F12):
- Should see: `🌐 API URL: http://localhost:8000`
- Should see: `✅ Backend connection successful`
- Should NOT see: `file://` anywhere

### Check URL Bar:
- Should show: `http://localhost:3000/index.html`
- Should NOT show: `file:///C:/Users/...`

### Check Servers:
- Backend: `http://localhost:8000` should respond
- Frontend: `http://localhost:3000` should show page

---

## 📋 Complete Checklist

- [ ] Backend server running (Terminal 1)
- [ ] Frontend server running (Terminal 2)
- [ ] Opened `http://localhost:3000/index.html` (NOT file://)
- [ ] Browser console shows: `✅ Backend connection successful`
- [ ] Can see login/signup page

---

## 🎯 Summary

**The application MUST be opened from:**
```
http://localhost:3000/index.html
```

**NOT from:**
```
file:///C:/Users/.../index.html
```

**Both servers must be running!**

---

## 📚 More Help

- See `HOW_TO_OPEN_APP.md` for detailed instructions
- See `FIX_NETWORK_ERRORS.md` for troubleshooting
- See `RUN_AND_TEST.md` for complete testing guide
