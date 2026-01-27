#!/usr/bin/env python3
"""
Test Database Connection and Setup
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / 'backend'))

def test_database():
    print("🗄️ TESTING DATABASE CONNECTION")
    print("=" * 50)
    
    try:
        from backend.app.core.database import get_database, get_collection
        
        # Test database connection
        print("[*] Testing MongoDB connection...")
        db = get_database()
        print(f"[✓] Connected to database: {db.name}")
        
        # Test collections
        collections = ['users', 'skills', 'resumes', 'analyses']
        for col_name in collections:
            col = get_collection(col_name)
            count = col.count_documents({})
            print(f"[✓] Collection '{col_name}': {count} documents")
        
        # Test a simple operation
        from backend.app.core.database import get_database
        db = get_database()
        test_col = db['test_connection']  # Use direct database access
        test_doc = {'test': 'connection', 'timestamp': 'now'}
        result = test_col.insert_one(test_doc)
        print(f"[✓] Test insert successful: {result.inserted_id}")
        
        # Clean up test
        test_col.delete_one({'_id': result.inserted_id})
        print("[✓] Test cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"[✗] Database error: {e}")
        print("\n💡 Solutions:")
        print("1. Make sure MongoDB is running: mongod")
        print("2. Check connection URL in backend/app/core/config.py")
        print("3. Install MongoDB: https://www.mongodb.com/try/download/community")
        return False

def test_dataset():
    print(f"\n📊 TESTING DATASET")
    print("=" * 50)
    
    try:
        from backend.app.services.dataset_loader import JobDatasetLoader
        
        loader = JobDatasetLoader()
        if loader.df is not None:
            print(f"[✓] Dataset loaded: {len(loader.df)} jobs")
            print(f"[✓] Unique roles: {len(loader.df['Title'].unique())}")
            print(f"[✓] Sample roles: {list(loader.df['Title'].unique())[:5]}")
            return True
        else:
            print("[✗] Dataset not loaded")
            return False
            
    except Exception as e:
        print(f"[✗] Dataset error: {e}")
        return False

def test_ai_models():
    print(f"\n🧠 TESTING AI MODELS")
    print("=" * 50)
    
    try:
        from backend.app.services.intelligent_role_matcher import intelligent_matcher
        
        # Test skill importance
        test_skills = ['Python', 'JavaScript', 'SQL']
        print("[*] Testing skill importance analysis...")
        
        for skill in test_skills:
            importance = intelligent_matcher.get_skill_importance_score(skill)
            print(f"[✓] {skill}: {importance:.3f} importance")
        
        # Test role matching
        print("[*] Testing intelligent role matching...")
        matches = intelligent_matcher.find_intelligent_role_matches(test_skills, top_n=3)
        
        if matches:
            print(f"[✓] Found {len(matches)} role matches")
            for match in matches:
                print(f"    • {match['role']}: {match['intelligent_score']}% AI score")
        else:
            print("[⚠] No role matches found")
        
        return True
        
    except Exception as e:
        print(f"[✗] AI models error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 SYSTEM DIAGNOSTICS")
    print("=" * 60)
    
    db_ok = test_database()
    dataset_ok = test_dataset()
    ai_ok = test_ai_models()
    
    print(f"\n📋 RESULTS SUMMARY")
    print("=" * 60)
    print(f"Database: {'✓ OK' if db_ok else '✗ FAILED'}")
    print(f"Dataset: {'✓ OK' if dataset_ok else '✗ FAILED'}")
    print(f"AI Models: {'✓ OK' if ai_ok else '✗ FAILED'}")
    
    if db_ok and dataset_ok and ai_ok:
        print(f"\n🎉 ALL SYSTEMS READY!")
        print("You can now start the server with: python run_server.py")
    else:
        print(f"\n⚠️ SOME ISSUES FOUND - Please fix before starting server")