#!/usr/bin/env python3
"""
Comprehensive Error Diagnostic Tool
Checks for common errors and provides fixes
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def check_python_version():
    """Check Python version"""
    print_header("CHECKING PYTHON VERSION")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print_header("CHECKING DEPENDENCIES")
    
    required = [
        'fastapi', 'uvicorn', 'pymongo', 'pydantic', 'passlib', 'bcrypt',
        'python-jose', 'scikit-learn', 'numpy', 'pandas', 'python-dotenv',
        'pdfminer', 'docx'
    ]
    
    missing = []
    for package in required:
        try:
            if package == 'pdfminer':
                import pdfminer
            elif package == 'docx':
                import docx
            else:
                __import__(package.replace('-', '_'))
            print_success(f"{package} - Installed")
        except ImportError:
            print_error(f"{package} - MISSING")
            missing.append(package)
    
    if missing:
        print_warning(f"\nMissing packages: {', '.join(missing)}")
        print_info("Install with: pip install -r backend/requirements.txt")
        return False
    return True

def check_mongodb():
    """Check MongoDB connection"""
    print_header("CHECKING MONGODB CONNECTION")
    
    try:
        from pymongo import MongoClient
        from backend.app.core.config import MONGODB_URL, MONGODB_DB_NAME
        
        print_info(f"MongoDB URL: {MONGODB_URL}")
        print_info(f"Database: {MONGODB_DB_NAME}")
        
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        print_success("MongoDB connection successful")
        
        # Check collections
        db = client[MONGODB_DB_NAME]
        collections = db.list_collection_names()
        print_info(f"Collections found: {len(collections)}")
        
        if 'dataset_skills' in collections:
            count = db.dataset_skills.count_documents({})
            print_success(f"dataset_skills: {count} documents")
        else:
            print_warning("dataset_skills collection not found - Run init_dataset.py")
        
        if 'dataset_roles' in collections:
            count = db.dataset_roles.count_documents({})
            print_success(f"dataset_roles: {count} documents")
        else:
            print_warning("dataset_roles collection not found - Run init_dataset.py")
        
        return True
    except Exception as e:
        print_error(f"MongoDB connection failed: {e}")
        print_info("Make sure MongoDB is running or check connection string in backend/.env")
        return False

def check_dataset_file():
    """Check if dataset file exists"""
    print_header("CHECKING DATASET FILE")
    
    possible_paths = [
        Path("backend/data/raw/job_dataset.csv"),
        Path("backend/data/raw/jobs_dataset.csv"),
        Path("data/raw/job_dataset.csv"),
        Path("data/raw/jobs_dataset.csv"),
    ]
    
    for path in possible_paths:
        if path.exists():
            print_success(f"Dataset found: {path}")
            # Check file size
            size = path.stat().st_size
            print_info(f"File size: {size:,} bytes")
            
            # Check first few lines
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:5]
                    if len(lines) > 0:
                        print_info(f"First line: {lines[0][:80]}...")
                        if 'Skills' in lines[0] or 'Title' in lines[0]:
                            print_success("File appears to be valid CSV")
                        else:
                            print_warning("File may not have expected columns")
            except Exception as e:
                print_error(f"Error reading file: {e}")
            
            return True
    
    print_error("Dataset file not found!")
    print_info("Expected locations:")
    for path in possible_paths:
        print_info(f"  - {path}")
    return False

def check_backend_structure():
    """Check backend file structure"""
    print_header("CHECKING BACKEND STRUCTURE")
    
    required_files = [
        "backend/app/main.py",
        "backend/app/core/config.py",
        "backend/app/core/database.py",
        "backend/app/core/security.py",
        "backend/app/api/routes/auth.py",
        "backend/app/api/routes/skills.py",
        "backend/app/api/routes/data.py",
        "backend/app/services/extended_dataset.py",
        "backend/app/services/dataset_normalizer.py",
        "backend/requirements.txt",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print_success(f"{file_path} - Exists")
        else:
            print_error(f"{file_path} - MISSING")
            all_exist = False
    
    return all_exist

def check_frontend_structure():
    """Check frontend file structure"""
    print_header("CHECKING FRONTEND STRUCTURE")
    
    required_files = [
        "frontend/index.html",
        "frontend/app.html",
        "frontend/server.py",
        "frontend/static/app.js",
        "frontend/static/main.css",
        "frontend/static/upload.js",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print_success(f"{file_path} - Exists")
        else:
            print_error(f"{file_path} - MISSING")
            all_exist = False
    
    return all_exist

def check_ports():
    """Check if ports are available"""
    print_header("CHECKING PORTS")
    
    import socket
    
    ports = {
        8000: "Backend",
        3000: "Frontend"
    }
    
    all_available = True
    for port, name in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print_warning(f"Port {port} ({name}) - IN USE")
            print_info(f"  Another process is using port {port}")
            print_info(f"  Solution: Stop the process or change port")
            all_available = False
        else:
            print_success(f"Port {port} ({name}) - Available")
    
    return all_available

def check_imports():
    """Check if backend modules can be imported"""
    print_header("CHECKING BACKEND IMPORTS")
    
    # Add backend to path
    backend_path = Path("backend")
    if backend_path.exists():
        sys.path.insert(0, str(backend_path.absolute()))
    
    modules_to_check = [
        ("app.main", "FastAPI app"),
        ("app.core.config", "Config"),
        ("app.core.database", "Database"),
        ("app.core.security", "Security"),
        ("app.api.routes.auth", "Auth routes"),
        ("app.api.routes.skills", "Skills routes"),
        ("app.api.routes.data", "Data routes"),
        ("app.services.extended_dataset", "Extended dataset"),
        ("app.services.dataset_normalizer", "Dataset normalizer"),
    ]
    
    all_ok = True
    for module_name, description in modules_to_check:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                print_error(f"{description} ({module_name}) - Cannot find module")
                all_ok = False
            else:
                print_success(f"{description} - OK")
        except Exception as e:
            print_error(f"{description} ({module_name}) - Error: {e}")
            all_ok = False
    
    return all_ok

def check_env_file():
    """Check .env file"""
    print_header("CHECKING ENVIRONMENT CONFIGURATION")
    
    env_path = Path("backend/.env")
    if env_path.exists():
        print_success(".env file exists")
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                if 'MONGODB_URL' in content:
                    print_success("MONGODB_URL found in .env")
                else:
                    print_warning("MONGODB_URL not found in .env (using default)")
        except Exception as e:
            print_error(f"Error reading .env: {e}")
    else:
        print_warning(".env file not found (using defaults)")
        print_info("Create backend/.env with MONGODB_URL if needed")
    
    return True

def generate_fix_script():
    """Generate a fix script based on errors found"""
    print_header("GENERATING FIX SCRIPT")
    
    fix_script = """#!/bin/bash
# Auto-generated fix script

echo "Installing dependencies..."
cd backend
pip install -r requirements.txt

echo "Checking MongoDB..."
# Add your MongoDB connection check here

echo "Initializing dataset..."
python scripts/init_dataset.py --dataset data/raw/job_dataset.csv

echo "Done! Now start servers:"
echo "  Terminal 1: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "  Terminal 2: cd frontend && python server.py"
"""
    
    with open("fix_all.sh", "w") as f:
        f.write(fix_script)
    
    print_success("Fix script created: fix_all.sh")
    print_info("Run: bash fix_all.sh (Linux/Mac) or fix_all.bat (Windows)")

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║       SKILL GAP ANALYZER - ERROR DIAGNOSTIC TOOL              ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Run all checks
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Backend Structure", check_backend_structure()))
    results.append(("Frontend Structure", check_frontend_structure()))
    results.append(("Environment Config", check_env_file()))
    results.append(("Backend Imports", check_imports()))
    results.append(("MongoDB Connection", check_mongodb()))
    results.append(("Dataset File", check_dataset_file()))
    results.append(("Ports", check_ports()))
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "="*70)
    print(f"Total: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your setup looks good.")
        print("\nTo start the application:")
        print("  1. Terminal 1: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("  2. Terminal 2: cd frontend && python server.py")
        print("  3. Browser: http://localhost:3000/index.html")
    else:
        print(f"\n⚠️  {total - passed} check(s) failed")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip install -r backend/requirements.txt")
        print("  2. Initialize dataset: python backend/scripts/init_dataset.py --dataset backend/data/raw/job_dataset.csv")
        print("  3. Start MongoDB (if using local)")
        print("  4. Check backend/.env for MongoDB URL")
        
        generate_fix_script()
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Diagnostic error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
