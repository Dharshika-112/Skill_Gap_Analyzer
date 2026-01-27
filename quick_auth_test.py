#!/usr/bin/env python3
"""
Quick Authentication Test
Tests basic signup/login functionality
"""

import requests
import time
import json

def test_auth():
    base_url = "http://localhost:8000"
    test_email = f"quicktest_{int(time.time())}@example.com"
    test_password = "test123"
    
    print(f"🧪 Testing authentication with email: {test_email}")
    
    # Test server health
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Server is running: {response.json().get('status')}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return False
    
    # Test signup
    print("\n📝 Testing Signup...")
    signup_data = {
        "name": "Quick Test User",
        "email": test_email,
        "password": test_password
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/signup", json=signup_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user_id")
            print(f"✅ Signup successful! User ID: {user_id}")
            print(f"🔑 Token received: {bool(token)}")
            
            # Test profile access
            print("\n👤 Testing Profile Access...")
            headers = {"Authorization": f"Bearer {token}"}
            profile_response = requests.get(f"{base_url}/api/auth/me", headers=headers)
            print(f"Profile Status: {profile_response.status_code}")
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print(f"✅ Profile access successful: {profile_data.get('email')}")
            else:
                print(f"❌ Profile access failed: {profile_response.text}")
            
            return True
        else:
            print(f"❌ Signup failed: {response.text}")
            
            # Try login instead
            print("\n🔐 Testing Login...")
            login_data = {
                "email": test_email,
                "password": test_password
            }
            login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
            print(f"Login Status: {login_response.status_code}")
            print(f"Login Response: {login_response.text}")
            
            return login_response.status_code == 200
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_auth()
    print(f"\n🎯 Authentication Test: {'PASSED' if success else 'FAILED'}")