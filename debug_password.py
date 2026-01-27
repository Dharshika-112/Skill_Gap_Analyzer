#!/usr/bin/env python3
"""
Debug password hashing issue
"""

import sys
import os
sys.path.append('backend')

try:
    from backend.app.core.security import hash_password, verify_password
    
    test_password = "test123"
    print(f"Testing password: '{test_password}' (length: {len(test_password)})")
    
    # Test hashing
    try:
        hashed = hash_password(test_password)
        print(f"✅ Password hashed successfully")
        print(f"Hash: {hashed[:50]}...")
        
        # Test verification
        is_valid = verify_password(test_password, hashed)
        print(f"✅ Password verification: {is_valid}")
        
    except Exception as e:
        print(f"❌ Password hashing failed: {e}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure the backend dependencies are installed")