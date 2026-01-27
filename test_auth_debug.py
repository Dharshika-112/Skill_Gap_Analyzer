#!/usr/bin/env python3
"""
Debug Authentication Issues
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_auth_debug():
    print("🔍 DEBUGGING AUTHENTICATION ISSUES")
    print("=" * 60)
    
    # Test 1: Check if auth endpoints exist
    print("1️⃣ TESTING AUTH ENDPOINTS AVAILABILITY")
    print("-" * 50)
    
    try:
        # Test signup endpoint
        response = requests.options(f"{BASE_URL}/api/auth/signup", timeout=5)
        print(f"✅ Signup endpoint exists: {response.status_code}")
        
        # Test login endpoint  
        response = requests.options(f"{BASE_URL}/api/auth/login", timeout=5)
        print(f"✅ Login endpoint exists: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Endpoint check failed: {e}")
        return False
    
    # Test 2: Test signup with detailed error handling
    print(f"\n2️⃣ TESTING SIGNUP WITH DEBUG INFO")
    print("-" * 50)
    
    timestamp = int(time.time())
    signup_data = {
        "name": "Debug User",
        "email": f"debug_{timestamp}@test.com",
        "password": "debugpass123"
    }
    
    try:
        print(f"Sending signup request to: {BASE_URL}/api/auth/signup")
        print(f"Data: {json.dumps(signup_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/auth/signup", 
            json=signup_data, 
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
            
            if response.status_code == 200:
                print("✅ Signup successful!")
                token = response_data.get('access_token')
                user_id = response_data.get('user_id')
                
                # Test 3: Test login with the same user
                print(f"\n3️⃣ TESTING LOGIN WITH CREATED USER")
                print("-" * 50)
                
                login_data = {
                    "email": signup_data["email"],
                    "password": signup_data["password"]
                }
                
                login_response = requests.post(
                    f"{BASE_URL}/api/auth/login",
                    json=login_data,
                    timeout=10,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Login response status: {login_response.status_code}")
                login_response_data = login_response.json()
                print(f"Login response data: {json.dumps(login_response_data, indent=2)}")
                
                if login_response.status_code == 200:
                    print("✅ Login successful!")
                    login_token = login_response_data.get('access_token')
                    
                    # Test 4: Test profile access
                    print(f"\n4️⃣ TESTING PROFILE ACCESS")
                    print("-" * 50)
                    
                    profile_response = requests.get(
                        f"{BASE_URL}/api/auth/me",
                        headers={"Authorization": f"Bearer {login_token}"},
                        timeout=10
                    )
                    
                    print(f"Profile response status: {profile_response.status_code}")
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        print(f"Profile data: {json.dumps(profile_data, indent=2)}")
                        print("✅ Profile access successful!")
                        return True
                    else:
                        print(f"❌ Profile access failed: {profile_response.text}")
                else:
                    print(f"❌ Login failed: {login_response_data}")
            else:
                print(f"❌ Signup failed: {response_data}")
                
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - server might be slow or not responding")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - server might not be running")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    return False

def test_cors_and_headers():
    print(f"\n5️⃣ TESTING CORS AND HEADERS")
    print("-" * 50)
    
    try:
        # Test CORS preflight
        response = requests.options(
            f"{BASE_URL}/api/auth/signup",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=5
        )
        
        print(f"CORS preflight status: {response.status_code}")
        print(f"CORS headers: {dict(response.headers)}")
        
        if 'access-control-allow-origin' in response.headers:
            print("✅ CORS is properly configured")
        else:
            print("⚠️ CORS might not be properly configured")
            
    except Exception as e:
        print(f"❌ CORS test failed: {e}")

if __name__ == "__main__":
    success = test_auth_debug()
    test_cors_and_headers()
    
    if success:
        print(f"\n🎉 AUTHENTICATION IS WORKING!")
        print("The issue might be in the frontend JavaScript.")
    else:
        print(f"\n❌ AUTHENTICATION HAS ISSUES")
        print("Check the backend server logs for more details.")