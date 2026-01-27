# 📁 CareerBoost AI - Project Structure

## 🏗️ Complete Project Architecture

```
CareerBoost-AI/
├── 📄 README.md                              # Main project documentation
├── 📄 LICENSE                                # MIT License
├── 📄 .gitignore                            # Git ignore rules
├── 📄 requirements.txt                       # Python dependencies
├── 📄 push_to_github.bat                    # Windows GitHub push script
├── 📄 push_to_github.sh                     # Linux/Mac GitHub push script
├── 📄 PROJECT_STRUCTURE.md                  # This file
│
├── 🚀 MAIN APPLICATION FILES
│   ├── 📄 skill_gap_analyzer_complete.html  # Complete integrated application
│   ├── 📄 run_enhanced_app.py               # Production server (Port 3003)
│   ├── 📄 start_backend.py                  # Backend server starter
│   └── 📄 start_server.py                   # Alternative server starter
│
├── 🖥️ BACKEND/
│   ├── 📁 app/
│   │   ├── 📁 api/
│   │   │   ├── 📁 routes/
│   │   │   │   ├── 📄 auth.py               # Authentication endpoints
│   │   │   │   ├── 📄 resume_analysis.py   # Resume analysis endpoints
│   │   │   │   └── 📄 __init__.py
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📁 __pycache__/
│   │   ├── 📁 core/
│   │   │   ├── 📄 config.py                 # Configuration settings
│   │   │   ├── 📄 database.py              # MongoDB connection
│   │   │   ├── 📄 dependencies.py          # FastAPI dependencies
│   │   │   ├── 📄 security.py              # JWT & password handling
│   │   │   ├── 📄 utils.py                 # Utility functions
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📁 __pycache__/
│   │   ├── 📁 models/
│   │   │   ├── 📄 analysis.py              # Analysis data models
│   │   │   ├── 📄 skill.py                 # Skill data models
│   │   │   ├── 📄 user.py                  # User data models
│   │   │   └── 📄 __init__.py
│   │   ├── 📁 services/
│   │   │   ├── 📄 advanced_ml.py           # Advanced ML algorithms
│   │   │   ├── 📄 ats_system.py            # ATS scoring system
│   │   │   ├── 📄 common_role_skills.py    # Role-skill mappings
│   │   │   ├── 📄 dataset_loader.py        # Dataset loading utilities
│   │   │   ├── 📄 dataset_normalizer.py    # Data normalization
│   │   │   ├── 📄 experience_weighting.py  # Experience calculations
│   │   │   ├── 📄 extended_dataset.py      # Extended dataset handling
│   │   │   ├── 📄 intelligent_role_matcher.py # AI role matching
│   │   │   ├── 📄 resume_parser.py         # Resume parsing logic
│   │   │   ├── 📄 role_matcher.py          # Role matching algorithms
│   │   │   ├── 📄 skill_categorizer.py     # Skill categorization
│   │   │   ├── 📄 skill_cleaner.py         # Skill data cleaning
│   │   │   ├── 📄 skill_matcher.py         # Skill matching logic
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📁 __pycache__/
│   │   ├── 📄 main.py                      # FastAPI application entry
│   │   ├── 📄 __init__.py
│   │   └── 📁 __pycache__/
│   ├── 📁 data/
│   │   ├── 📁 models/
│   │   │   └── 📄 ats_system.pkl           # Trained ML model
│   │   └── 📁 raw/
│   │       ├── 📄 AI_Resume_Screening.csv  # ATS training dataset
│   │       ├── 📄 job_dataset.csv          # Job requirements dataset
│   │       └── 📁 uploads/                 # Resume upload directory
│   ├── 📁 logs/
│   │   └── 📄 data_processor.log           # Application logs
│   ├── 📄 requirements.txt                 # Backend dependencies
│   ├── 📄 .env.example                     # Environment variables template
│   └── 📁 scripts/
│       └── 📄 init_dataset.py              # Dataset initialization
│
├── 🌐 FRONTEND/
│   ├── 📄 index.html                       # Main frontend application
│   ├── 📄 app.html                         # Alternative app interface
│   ├── 📄 debug_frontend.html              # Debug interface
│   ├── 📄 test_frontend.html               # Test interface
│   ├── 📄 server.py                        # Frontend development server
│   └── 📁 static/
│       ├── 📄 app.js                       # Main application JavaScript
│       ├── 📄 error-handler.js             # Error handling
│       ├── 📄 main.css                     # Main stylesheet
│       └── 📄 upload.js                    # File upload handling
│
├── 🧪 TESTING/
│   ├── 📄 test_complete_integrated_app.py  # Complete integration tests
│   ├── 📄 test_enhanced_features.py        # Enhanced features tests
│   ├── 📄 test_updated_resume_scoring.py   # Resume scoring tests
│   ├── 📄 comprehensive_api_test.py        # API endpoint tests
│   ├── 📄 test_all_features.py             # All features test suite
│   ├── 📄 test_complete_system.py          # System-wide tests
│   ├── 📄 final_system_test.py             # Final validation tests
│   └── 📁 scripts/
│       ├── 📄 api_e2e_test.py              # End-to-end API tests
│       ├── 📄 final_test.py                # Final test suite
│       ├── 📄 run_smoke_tests.py           # Smoke tests
│       ├── 📄 system_test.py               # System tests
│       └── 📄 test_complete_flow.py        # Complete workflow tests
│
├── 📚 DOCUMENTATION/
│   ├── 📄 COMPLETE_INTEGRATED_APP.md       # Complete app documentation
│   ├── 📄 RESUME_SCORING_UPDATE_SUMMARY.md # Resume scoring details
│   ├── 📄 CAREERBOOST_AI_COMPLETE.md       # Technical guide
│   ├── 📄 DOCUMENTATION_INDEX.md           # Documentation index
│   ├── 📄 FINAL_DELIVERY.md                # Final delivery notes
│   ├── 📄 HOW_TO_OPEN_APP.md               # Quick start guide
│   ├── 📄 QUICK_START.md                   # Quick start instructions
│   ├── 📄 RUN_AND_TEST.md                  # Run and test guide
│   ├── 📄 SETUP_GUIDE.md                   # Setup instructions
│   ├── 📄 SYSTEM_STATUS_FINAL.md           # Final system status
│   ├── 📄 SYSTEM_STATUS_REPORT.md          # System status report
│   ├── 📄 UPLOAD_INSTRUCTIONS.md           # Upload instructions
│   └── 📄 FILE_STRUCTURE.txt               # File structure overview
│
├── 🔧 UTILITIES & HELPERS/
│   ├── 📄 analyze_dataset.py               # Dataset analysis tools
│   ├── 📄 debug_dataset_skills.py          # Dataset debugging
│   ├── 📄 debug_parser_step_by_step.py     # Parser debugging
│   ├── 📄 debug_role_matching.py           # Role matching debug
│   ├── 📄 diagnose_errors.py               # Error diagnosis
│   ├── 📄 minimal_server.py                # Minimal server for testing
│   ├── 📄 minimal_test_app.py              # Minimal test application
│   └── 📄 quick_auth_test.py               # Authentication testing
│
├── 📋 CONFIGURATION/
│   ├── 📄 CHECK_ERRORS.md                  # Error checking guide
│   ├── 📄 DATASET_INSTRUCTIONS.txt         # Dataset usage instructions
│   ├── 📄 FIX_ALL_ERRORS.md               # Error fixing guide
│   ├── 📄 FIX_NETWORK_ERRORS.md           # Network error fixes
│   ├── 📄 fix_all.bat                     # Windows fix script
│   ├── 📄 fix_all.sh                      # Linux/Mac fix script
│   └── 📄 SYSTEM_READY.txt                # System readiness check
│
└── 📁 __pycache__/                        # Python cache files
```

## 🎯 Key Application Files

### **Main Application (Recommended)**
- **`skill_gap_analyzer_complete.html`** - Complete integrated single-page application
- **`run_enhanced_app.py`** - Production server (Port 3003)

### **Backend API**
- **`backend/app/main.py`** - FastAPI application
- **`start_backend.py`** - Backend server starter (Port 8000)

### **Frontend Interface**
- **`frontend/index.html`** - Main frontend application
- **`frontend/server.py`** - Frontend server (Port 3000)

## 📊 Data Files

### **Datasets**
- **`backend/data/raw/AI_Resume_Screening.csv`** - 1000+ resumes for ATS training
- **`backend/data/raw/job_dataset.csv`** - 1068+ job postings for skill matching

### **Models**
- **`backend/data/models/ats_system.pkl`** - Trained ML model (96%+ accuracy)

## 🧪 Testing Suite

### **Integration Tests**
- **`test_complete_integrated_app.py`** - Complete system testing
- **`comprehensive_api_test.py`** - API endpoint validation

### **Feature Tests**
- **`test_enhanced_features.py`** - Enhanced features validation
- **`test_updated_resume_scoring.py`** - Resume scoring workflow

## 📚 Documentation

### **User Guides**
- **`README.md`** - Main project documentation
- **`HOW_TO_OPEN_APP.md`** - Quick start guide
- **`SETUP_GUIDE.md`** - Detailed setup instructions

### **Technical Documentation**
- **`COMPLETE_INTEGRATED_APP.md`** - Complete feature documentation
- **`PROJECT_STRUCTURE.md`** - This file
- **`SYSTEM_STATUS_FINAL.md`** - System status and metrics

## 🚀 Quick Access

### **Start the Application**
```bash
# Complete integrated app (recommended)
python run_enhanced_app.py
# Access: http://localhost:3003

# Or full backend + frontend
python start_backend.py &
python frontend/server.py
# Access: http://localhost:3000
```

### **Run Tests**
```bash
# Complete system test
python test_complete_integrated_app.py

# API tests
python comprehensive_api_test.py
```

---

This structure provides a complete, production-ready application with comprehensive testing, documentation, and deployment scripts. All components are organized logically for easy maintenance and development.