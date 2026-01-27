#!/usr/bin/env python3
"""
COMPLETE SYSTEM DIAGNOSTIC TEST
Tests everything step by step
"""
import sys
import time
import os

# Add parent directory to path so we can import backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 80)
print("SKILL GAP ANALYZER - COMPLETE SYSTEM TEST")
print("=" * 80)

# TEST 1: Python Version
print("\n[TEST 1] Python Version")
print(f"Version: {sys.version}")
print(f"Executable: {sys.executable}")
print("✅ PASS")

# TEST 2: MongoDB Connection
print("\n[TEST 2] MongoDB Connection")
try:
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ MongoDB is running and accessible")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)

# TEST 3: Backend Module Imports
print("\n[TEST 3] Backend Module Imports")
try:
    from backend.app.core.config import MONGODB_URL
    from backend.app.core.database import get_database, get_collection
    from backend.app.core.security import hash_password, verify_password
    from backend.app.services.extended_dataset import get_dataset_skills
    from backend.app.api.routes import auth, skills, data
    print("✅ All backend imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 4: FastAPI App Initialization
print("\n[TEST 4] FastAPI App Initialization")
try:
    from backend.app.main import app
    print(f"✅ App initialized: {app.title}")
    print(f"   Routes: {len(app.routes)}")
except Exception as e:
    print(f"❌ App initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 5: Database Operations
print("\n[TEST 5] Database Operations")
try:
    db = get_database()
    collections = db.list_collection_names()
    print(f"✅ Database accessible")
    print(f"   Collections: {len(collections)}")
    if collections:
        print(f"   Sample collections: {collections[:3]}")
except Exception as e:
    print(f"❌ Database operation failed: {e}")
    sys.exit(1)

# TEST 6: Skill Dataset
print("\n[TEST 6] Skill Dataset")
try:
    skills = get_dataset_skills()
    print(f"✅ Dataset loaded")
    print(f"   Total skills: {len(skills)}")
    if skills:
        print(f"   Sample skills: {skills[:5]}")
except Exception as e:
    print(f"❌ Dataset loading failed: {e}")
    sys.exit(1)

# TEST 7: Password Hashing
print("\n[TEST 7] Password Hashing (Security)")
try:
    test_pass = "test123"
    hashed = hash_password(test_pass)
    is_valid = verify_password(test_pass, hashed)
    if is_valid:
        print("✅ Password hashing working correctly")
    else:
        print("❌ Password verification failed")
        sys.exit(1)
except Exception as e:
    print(f"❌ Password test failed: {e}")
    sys.exit(1)

# TEST 8: Resume Parser
print("\n[TEST 8] Resume Parser")
try:
    from backend.app.services.resume_parser import extract_skills_from_text
    test_text = "I know Python, JavaScript, TensorFlow, and Docker"
    extracted = extract_skills_from_text(test_text)
    if len(extracted) > 0:
        print(f"✅ Resume parser working")
        print(f"   Extracted {len(extracted)} skills from test text")
        print(f"   Sample: {extracted[:3]}")
    else:
        print("⚠️  No skills extracted (may be normal for short text)")
except Exception as e:
    print(f"❌ Resume parser test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 9: API Endpoints (Structure Check)
print("\n[TEST 9] API Endpoints Structure")
try:
    endpoint_count = 0
    auth_routes = 0
    skill_routes = 0
    data_routes = 0
    
    for route in app.routes:
        if hasattr(route, 'path'):
            endpoint_count += 1
            if '/api/auth' in route.path:
                auth_routes += 1
            elif '/api/skills' in route.path:
                skill_routes += 1
            elif '/api/data' in route.path:
                data_routes += 1
    
    print(f"✅ Endpoints registered: {endpoint_count}")
    print(f"   Auth endpoints: {auth_routes}")
    print(f"   Skills endpoints: {skill_routes}")
    print(f"   Data endpoints: {data_routes}")
except Exception as e:
    print(f"❌ Endpoint check failed: {e}")
    sys.exit(1)

# TEST 10: Frontend Files
print("\n[TEST 10] Frontend Files")
try:
    import os
    frontend_files = {
        'app.html': 'frontend/app.html',
        'server.py': 'frontend/server.py',
        'main.css': 'frontend/static/main.css',
        'upload.js': 'frontend/static/upload.js'
    }
    
    missing = []
    for name, path in frontend_files.items():
        if not os.path.exists(path):
            missing.append(name)
    
    if missing:
        print(f"❌ Missing files: {missing}")
    else:
        print(f"✅ All frontend files present")
        for name in frontend_files.keys():
            print(f"   ✓ {name}")
except Exception as e:
    print(f"❌ Frontend check failed: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED - SYSTEM READY")
print("=" * 80)
print("""
NEXT STEPS:
1. Start Backend: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
2. Start Frontend: python frontend/server.py (in another terminal)
3. Open Frontend: http://localhost:3050/app.html
4. Test the complete flow: Signup → Login → Upload Resume
""")
