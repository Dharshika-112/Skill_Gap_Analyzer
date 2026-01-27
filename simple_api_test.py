#!/usr/bin/env python3
"""
Simple API Test with longer timeouts
"""

import requests
import time
import json

def test_api_with_timeout():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing API with extended timeouts...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/", timeout=30)
        print(f"✅ Health check: {response.status_code} - {response.json().get('status')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: API Info
    try:
        response = requests.get(f"{base_url}/api/info", timeout=30)
        print(f"✅ API Info: {response.status_code} - Version {response.json().get('version')}")
    except Exception as e:
        print(f"❌ API Info failed: {e}")
        return False
    
    # Test 3: Signup
    test_email = f"simpletest_{int(time.time())}@example.com"
    signup_data = {
        "name": "Simple Test User",
        "email": test_email,
        "password": "test123"
    }
    
    try:
        print(f"📝 Testing signup with email: {test_email}")
        response = requests.post(f"{base_url}/api/auth/signup", json=signup_data, timeout=30)
        print(f"Signup response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user_id")
            print(f"✅ Signup successful: User ID {user_id}")
            
            # Test 4: Profile access
            headers = {"Authorization": f"Bearer {token}"}
            profile_response = requests.get(f"{base_url}/api/auth/me", headers=headers, timeout=30)
            print(f"✅ Profile access: {profile_response.status_code}")
            
            return True
        else:
            print(f"❌ Signup failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Signup test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_api_with_timeout()
    print(f"\n🎯 Simple API Test: {'PASSED' if success else 'FAILED'}")