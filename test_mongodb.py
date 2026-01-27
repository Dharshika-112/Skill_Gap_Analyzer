#!/usr/bin/env python3
"""
Test MongoDB Connection
"""

import sys
sys.path.append('backend')

try:
    from backend.app.core.database import get_database, get_collection
    from pymongo.errors import ServerSelectionTimeoutError
    
    print("🔍 Testing MongoDB Connection...")
    
    try:
        # Test database connection
        db = get_database()
        print(f"✅ Database connected: {db.name}")
        
        # Test collection access
        users = get_collection('users')
        print(f"✅ Users collection accessible")
        
        # Test basic operation
        count = users.count_documents({})
        print(f"✅ Current user count: {count}")
        
        # Test insert/delete
        test_doc = {"test": "connection", "timestamp": "now"}
        result = users.insert_one(test_doc)
        print(f"✅ Test insert successful: {result.inserted_id}")
        
        # Clean up
        users.delete_one({"_id": result.inserted_id})
        print(f"✅ Test cleanup successful")
        
        print("\n🎯 MongoDB Connection: WORKING")
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ MongoDB connection timeout: {e}")
        print("💡 Make sure MongoDB is running on localhost:27017")
        
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")