# 🚀 CareerBoost AI - Startup Commands Guide

## 📋 Quick Start Checklist

### ✅ Prerequisites Check
- [ ] Python 3.8+ installed
- [ ] Node.js 14+ installed  
- [ ] MongoDB 4.4+ installed
- [ ] Git installed

### 🔧 Installation Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/Dharshika-112/Skill_Gap_Analyzer.git
   cd Skill_Gap_Analyzer
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install PyPDF2 pdfplumber  # For PDF processing
   ```

3. **Install React Dependencies**
   ```bash
   cd frontend-react
   npm install
   cd ..
   ```

## 🚀 Starting the Application

### Option 1: Full Development Setup (Recommended)

**Terminal 1: MongoDB Database**
```bash
mongod --dbpath mongodb_data --port 27017
```

**Terminal 2: Authentication Server**
```bash
python simple_auth_server.py
# Server starts on http://localhost:8003
```

**Terminal 3: Role Management Server**
```bash
cd backend
python simple_role_server.py
# Server starts on http://localhost:8004
```

**Terminal 4: Skill Gap Analyzer**
```bash
cd backend
python simple_enhanced_skill_server.py
# Server starts on http://localhost:8006
```

**Terminal 5: Resume Scoring Server**
```bash
cd backend
python enhanced_resume_scoring_server.py
# Server starts on http://localhost:8007
```

**Terminal 6: React Frontend**
```bash
cd frontend-react
npm start
# Application opens at http://localhost:3000
```

### Option 2: Quick Start (Essential Services Only)

```bash
# Start MongoDB
mongod --dbpath mongodb_data --port 27017 &

# Start essential backend services
python simple_auth_server.py &
cd backend && python simple_enhanced_skill_server.py &
cd backend && python enhanced_resume_scoring_server.py &

# Start frontend
cd frontend-react && npm start
```

### Option 3: Production Mode

```bash
# Build React app
cd frontend-react
npm run build

# Start all services
python simple_auth_server.py &
cd backend && python simple_role_server.py &
cd backend && python simple_enhanced_skill_server.py &
cd backend && python enhanced_resume_scoring_server.py &

# Serve React build
npx serve -s frontend-react/build -l 3000
```

## 🔧 Initial Setup (First Time Only)

**Setup Database and Admin User**
```bash
python setup_admin_and_roles.py
python populate_roles_database.py
```

**Verify Installation**
```bash
python quick_system_test.py
```

## 🌐 Access Points

- **🏠 Main Application**: http://localhost:3000
- **📊 Dashboard**: http://localhost:3000/dashboard
- **🎯 Skill Gap Analyzer**: http://localhost:3000/skill-gap-analyzer
- **📄 Resume Scoring**: http://localhost:3000/resume-scoring
- **👤 User Profile**: http://localhost:3000/profile

## 📚 API Documentation

- **Skill Gap API**: http://localhost:8006/docs
- **Resume Scoring API**: http://localhost:8007/docs
- **Role Management**: http://localhost:8004/api/roles

## 🐛 Troubleshooting

### MongoDB Issues
```bash
# If MongoDB fails to start
mongod --repair --dbpath mongodb_data
mongod --dbpath mongodb_data --port 27017
```

### Port Conflicts
```bash
# Check if ports are in use
netstat -an | findstr :3000
netstat -an | findstr :8003
netstat -an | findstr :8006
netstat -an | findstr :8007
```

### React Build Issues
```bash
cd frontend-react
rm -rf node_modules package-lock.json
npm install
npm start
```

### Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 🎯 System Status Check

Run this command to verify all services are working:
```bash
python quick_system_test.py
```

Expected output:
```
✅ Database: 6 roles loaded
✅ Auth Server: Running
✅ Skill Analyzer: 2346 skills
✅ Resume Scorer: Running
✅ Frontend: Accessible
```

## 🔄 Development Workflow

1. **Start MongoDB** (always first)
2. **Start backend services** (in any order)
3. **Start React frontend** (last)
4. **Access application** at http://localhost:3000
5. **Make changes** and test
6. **Run tests** before committing

## 📊 Performance Tips

- Keep MongoDB running in background
- Use `npm start` for development (hot reload)
- Use `npm run build` for production
- Monitor logs for errors
- Use browser dev tools for debugging

## 🔒 Security Notes

- Default admin credentials are in setup script
- Change JWT secret in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Regular security updates

This guide ensures smooth startup and operation of CareerBoost AI!