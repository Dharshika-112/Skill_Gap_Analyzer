#!/usr/bin/env python3
"""
Test all API endpoints to verify they're working
Run this after starting the backend server
"""

import requests
import json
import sys

API_URL = "http://localhost:8000"

def test_endpoint(method, path, data=None, headers=None, description=""):
    """Test a single endpoint"""
    url = f"{API_URL}{path}"
    try:
        if method == "GET":
            res = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            res = requests.post(url, json=data, headers=headers, timeout=5)
        else:
            print(f"❌ Unknown method: {method}")
            return False
        
        if res.status_code < 400:
            print(f"✅ {description or path}: {res.status_code}")
            return True
        else:
            print(f"❌ {description or path}: {res.status_code} - {res.text[:100]}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {description or path}: Connection failed - Is backend running?")
        return False
    except Exception as e:
        print(f"❌ {description or path}: {str(e)}")
        return False

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║       TESTING ALL API ENDPOINTS                                ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Health check
    print("\n📡 Testing Health Check...")
    results.append(("Health Check", test_endpoint("GET", "/", description="Health Check")))
    
    # Public endpoints
    print("\n📡 Testing Public Endpoints...")
    results.append(("Get Skills", test_endpoint("GET", "/api/data/skills", description="Get Skills")))
    results.append(("Get Roles", test_endpoint("GET", "/api/data/roles", description="Get Roles")))
    results.append(("Dataset Info", test_endpoint("GET", "/api/data/dataset-info", description="Dataset Info")))
    
    # Auth endpoints (without token)
    print("\n📡 Testing Auth Endpoints...")
    results.append(("Signup (test)", test_endpoint("POST", "/api/auth/signup", 
        data={"name": "Test User", "email": "test@test.com", "password": "test123"},
        description="Signup")))
    
    # Test signup then login
    print("\n📡 Testing Login Flow...")
    signup_res = requests.post(f"{API_URL}/api/auth/signup", 
        json={"name": "Test User 2", "email": "test2@test.com", "password": "test123"},
        timeout=5)
    
    if signup_res.status_code == 200:
        token = signup_res.json().get("access_token")
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            results.append(("Get Profile", test_endpoint("GET", "/api/auth/me", headers=headers, description="Get Profile")))
            results.append(("Get User Skills", test_endpoint("GET", "/api/skills/user-skills", headers=headers, description="Get User Skills")))
            results.append(("Save Skills", test_endpoint("POST", "/api/skills/save", 
                data={"skills": ["Python", "Java", "SQL"]}, headers=headers, description="Save Skills")))
    
    # Data endpoints
    print("\n📡 Testing Data Endpoints...")
    results.append(("Skill Gap Analysis", test_endpoint("POST", "/api/data/skill-gap",
        data={"user_skills": ["Python", "Java"], "role_skills": ["Python", "Java", "SQL"], "role_name": "Software Engineer"},
        description="Skill Gap Analysis")))
    results.append(("Recommend Roles", test_endpoint("POST", "/api/data/recommend-roles",
        data={"skills": ["Python", "Java", "SQL"]},
        description="Recommend Roles")))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("="*60)
    print(f"Total: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All endpoints are working!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} endpoint(s) failed")
        print("Check backend logs for details")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        sys.exit(1)
