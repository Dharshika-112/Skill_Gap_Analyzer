# 📁 CareerBoost AI - Project Structure

## 🏗️ Complete Project Architecture

```
CareerBoost-AI/
├── 📁 .git/                           # Git repository data
├── 📁 .kiro/                          # Kiro AI assistant configuration
│   └── specs/skill-gap-analyzer/      # Project specifications
├── 📁 .vscode/                        # VS Code settings
├── 📁 backend/                        # Backend Services & APIs
│   ├── 📁 app/                        # Core Application
│   │   ├── 📁 api/                    # API Routes
│   │   │   ├── 📁 routes/             # Route handlers
│   │   │   └── __init__.py
│   │   ├── 📁 core/                   # Core Functionality
│   │   │   ├── config.py              # Configuration settings
│   │   │   ├── database.py            # Database connections
│   │   │   ├── dependencies.py        # FastAPI dependencies
│   │   │   ├── file_database.py       # File-based database fallback
│   │   │   ├── mongodb_setup.py       # MongoDB initialization
│   │   │   ├── security.py            # Authentication & security
│   │   │   └── utils.py               # Utility functions
│   │   ├── 📁 models/                 # Data Models
│   │   │   ├── analysis.py            # Analysis data models
│   │   │   ├── role.py                # Role data models
│   │   │   ├── skill.py               # Skill data models
│   │   │   ├── user.py                # User data models
│   │   │   └── user_activity.py       # User activity tracking
│   │   ├── 📁 services/               # Business Logic & ML
│   │   │   ├── advanced_ml.py         # Advanced ML algorithms
│   │   │   ├── ats_system.py          # ATS scoring system
│   │   │   ├── common_role_skills.py  # Role-skill mappings
│   │   │   ├── dataset_loader.py      # Data loading utilities
│   │   │   ├── dataset_normalizer.py  # Data normalization
│   │   │   ├── deep_learning_parser.py # Deep learning text parsing
│   │   │   ├── enhanced_skill_matcher.py # Enhanced skill matching
│   │   │   ├── experience_weighting.py # Experience scoring
│   │   │   ├── extended_dataset.py    # Extended dataset handling
│   │   │   ├── intelligent_role_matcher.py # AI role matching
│   │   │   ├── intelligent_skill_matcher.py # AI skill matching
│   │   │   ├── learning_roadmap_generator.py # Learning path generation
│   │   │   ├── ml_skill_matcher.py    # ML-based skill matching
│   │   │   ├── resume_parser.py       # Resume parsing logic
│   │   │   ├── role_based_ml.py       # Role-based ML models
│   │   │   ├── role_based_ml_scorer.py # Role-based scoring
│   │   │   ├── role_matcher.py        # Role matching algorithms
│   │   │   ├── skill_categorizer.py   # Skill categorization
│   │   │   ├── skill_cleaner.py       # Skill data cleaning
│   │   │   ├── skill_gap_analyzer.py  # Skill gap analysis
│   │   │   ├── skill_matcher.py       # Basic skill matching
│   │   │   ├── skill_normalizer.py    # Skill normalization
│   │   │   ├── skill_taxonomy.py      # Skill taxonomy management
│   │   │   └── weighted_gap_scorer.py # Weighted gap scoring
│   │   ├── main.py                    # Main FastAPI application
│   │   └── __init__.py
│   ├── 📁 data/                       # Data Storage
│   │   ├── 📁 models/                 # Trained ML Models
│   │   │   ├── ats_system.pkl         # ATS scoring model
│   │   │   └── 📁 role_based/         # Role-specific models
│   │   ├── 📁 processed/              # Processed Datasets
│   │   │   ├── ats_dataset_normalized.csv # Normalized ATS data
│   │   │   ├── ats_skills_list.json   # ATS skills database
│   │   │   ├── job_dataset_normalized.csv # Normalized job data
│   │   │   ├── job_skills_list.json   # Job skills database
│   │   │   ├── role_*_dataset.csv     # Role-specific datasets
│   │   │   └── skill_gap_reference.json # Skill gap reference
│   │   └── 📁 raw/                    # Raw Datasets
│   │       ├── AI_Resume_Screening.csv # ATS training data (1000+ resumes)
│   │       ├── job_dataset.csv        # Job postings data (1068+ jobs)
│   │       └── 📁 uploads/            # User uploaded resumes
│   ├── 📁 logs/                       # Application Logs
│   │   └── data_processor.log         # Data processing logs
│   ├── 📁 scripts/                    # Backend Scripts
│   │   ├── init_dataset.py            # Dataset initialization
│   │   └── setup_roles_database.py    # Role database setup
│   ├── enhanced_resume_scoring_server.py # Resume Scoring API (Port 8007)
│   ├── simple_enhanced_skill_server.py   # Skill Gap API (Port 8006)
│   ├── simple_role_server.py         # Role Management API (Port 8004)
│   ├── requirements.txt               # Backend dependencies
│   ├── requirements_basic.txt         # Basic requirements
│   ├── requirements_minimal.txt       # Minimal requirements
│   └── requirements_simple.txt        # Simple requirements
├── 📁 frontend-react/                 # React Frontend Application
│   ├── 📁 build/                      # Production build (generated)
│   ├── 📁 node_modules/               # Node.js dependencies (generated)
│   ├── 📁 public/                     # Public Assets
│   │   └── index.html                 # Main HTML template
│   ├── 📁 src/                        # Source Code
│   │   ├── 📁 components/             # Reusable Components
│   │   │   ├── Navbar.css             # Navigation styling
│   │   │   ├── Navbar.js              # Navigation component
│   │   │   └── ProtectedRoute.js      # Route protection
│   │   ├── 📁 contexts/               # React Contexts
│   │   │   └── AuthContext.js         # Authentication context
│   │   ├── 📁 pages/                  # Main Pages
│   │   │   ├── AdminDashboard.css     # Admin dashboard styling
│   │   │   ├── AdminDashboard.js      # Admin dashboard page
│   │   │   ├── AdminLogin.css         # Admin login styling
│   │   │   ├── AdminLogin.js          # Admin login page
│   │   │   ├── Auth.css               # Authentication styling
│   │   │   ├── Dashboard.css          # Main dashboard styling
│   │   │   ├── Dashboard.js           # Main dashboard page
│   │   │   ├── ImprovementSuggestions.js # Improvement suggestions
│   │   │   ├── LandingPage.css        # Landing page styling
│   │   │   ├── LandingPage.js         # Landing page
│   │   │   ├── Login.js               # User login page
│   │   │   ├── Profile.css            # User profile styling
│   │   │   ├── Profile.js             # User profile page
│   │   │   ├── Register.js            # User registration
│   │   │   ├── ResumeScoring.css      # Resume scoring styling
│   │   │   ├── ResumeScoring.js       # Resume scoring page
│   │   │   ├── RoleDetail.css         # Role detail styling
│   │   │   ├── RoleDetail.js          # Role detail page
│   │   │   ├── Signup.js              # User signup page
│   │   │   ├── SkillGapAnalyzer.css   # Skill gap analyzer styling
│   │   │   └── SkillGapAnalyzer.js    # Skill gap analyzer page
│   │   ├── App.css                    # Main app styling
│   │   ├── App.js                     # Main app component
│   │   ├── index.css                  # Global styling
│   │   └── index.js                   # React entry point
│   ├── package.json                   # Node.js dependencies
│   └── package-lock.json              # Dependency lock file
├── 📁 mongodb_data/                   # MongoDB Database Files
│   ├── 📁 diagnostic.data/            # MongoDB diagnostics
│   ├── 📁 journal/                    # MongoDB journal
│   ├── 📁 _tmp/                       # Temporary files
│   ├── collection-*.wt                # Collection data files
│   ├── index-*.wt                     # Index files
│   ├── mongod.lock                    # MongoDB lock file
│   ├── sizeStorer.wt                  # Size storage
│   ├── storage.bson                   # Storage configuration
│   ├── WiredTiger*                    # WiredTiger storage engine files
│   └── _mdb_catalog.wt                # MongoDB catalog
├── 📁 scripts/                        # Utility Scripts
│   ├── api_e2e_test.py                # End-to-end API tests
│   ├── final_test.py                  # Final system test
│   ├── push_to_github.ps1             # PowerShell GitHub push script
│   ├── push_to_github.sh              # Bash GitHub push script
│   ├── run_smoke_tests.py             # Smoke tests
│   ├── simple_port_test.py            # Port availability test
│   ├── start_backend_test.py          # Backend startup test
│   ├── system_test.py                 # System integration test
│   ├── test_complete_flow.py          # Complete workflow test
│   ├── test_resume_parsing.py         # Resume parsing test
│   └── _test_import_resume_parser.py  # Resume parser import test
├── 📄 .gitignore                      # Git ignore rules
├── 📄 CareerBoost_AI_API.postman_collection.json # Postman API collection
├── 📄 CareerBoost_AI_Environment.postman_environment.json # Postman environment
├── 📄 DATABASE_STRUCTURE.md           # Database schema documentation
├── 📄 FINAL_SYSTEM_STATUS_COMPLETE.md # Complete system status
├── 📄 LICENSE                         # MIT License
├── 📄 populate_roles_database.py      # Role database population script
├── 📄 PROJECT_STRUCTURE.md            # This file
├── 📄 quick_system_test.py            # Quick system verification
├── 📄 README.md                       # Main project documentation
├── 📄 requirements.txt                # Main Python dependencies
├── 📄 setup_admin_and_roles.py        # Admin and roles setup
├── 📄 simple_auth_server.py           # Authentication server (Port 8003)
├── 📄 STARTUP_COMMANDS_GUIDE.md       # Startup instructions
└── 📄 test_resume_upload.py           # Resume upload test
```

## 🔧 Key Components Explained

### 🎯 Backend Services (Microservices Architecture)

1. **Authentication Server** (`simple_auth_server.py` - Port 8003)
   - JWT-based authentication
   - User registration and login
   - Profile management

2. **Role Management Server** (`backend/simple_role_server.py` - Port 8004)
   - Career roles database
   - Role details and requirements
   - Admin role management

3. **Skill Gap Analyzer** (`backend/simple_enhanced_skill_server.py` - Port 8006)
   - ML-powered skill analysis
   - Role recommendations
   - Quiz system
   - Activity tracking

4. **Resume Scoring Server** (`backend/enhanced_resume_scoring_server.py` - Port 8007)
   - PDF processing
   - ATS scoring algorithms
   - Role-based analysis
   - Improvement recommendations

### 🎨 Frontend Application (React SPA)

- **Modern React 18** with hooks and context
- **Responsive design** with CSS Grid and Flexbox
- **Framer Motion** for smooth animations
- **Axios** for API communication
- **React Router** for navigation
- **Context API** for state management

### 🗄️ Database Structure (MongoDB)

- **Users Collection**: User profiles and authentication
- **Roles Collection**: Career roles and requirements
- **Skills Collection**: Skills database and taxonomy
- **Activities Collection**: User activity tracking
- **Analyses Collection**: Analysis results and history
- **Resumes Collection**: Uploaded resumes and scores

### 📊 Data Pipeline

1. **Raw Data** → CSV files with job postings and ATS data
2. **Processing** → Normalization and feature extraction
3. **ML Training** → Model training and validation
4. **API Serving** → Real-time predictions and analysis
5. **Storage** → Results stored in MongoDB

## 🚀 Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   Backend APIs  │    │   MongoDB       │
│   (Port 3000)   │◄──►│   (Ports 8003-  │◄──►│   (Port 27017)  │
│                 │    │    8007)        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │   ML Models     │    │   File Storage  │
│   (CSS, JS)     │    │   (Pickle)      │    │   (Uploads)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📈 Performance Considerations

- **Lazy Loading**: Components loaded on demand
- **API Caching**: Responses cached for better performance
- **Database Indexing**: Optimized queries with proper indexes
- **File Compression**: Gzip compression for static assets
- **CDN Ready**: Static assets can be served from CDN

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **CORS Protection**: Configured for specific origins
- **Input Validation**: All inputs validated and sanitized
- **File Upload Security**: PDF files validated and processed safely
- **Environment Variables**: Sensitive data in environment variables

## 🧪 Testing Structure

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **End-to-End Tests**: Complete workflow testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability scanning

This structure ensures maintainability, scalability, and professional development practices.