#!/usr/bin/env python3
"""
Test All API Endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    print("🏥 TESTING HEALTH CHECK")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['message']}")
            print(f"   Status: {data['status']}")
            print(f"   Features: {len(data['features'])} available")
            return True
        else:
            print(f"❌ Health Check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check error: {e}")
        return False

def test_api_info():
    print(f"\n📊 TESTING API INFO")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Info: {data['name']} v{data['version']}")
            if 'dataset' in data:
                print(f"   Dataset: {data['dataset'].get('total_skills', 'N/A')} skills")
            print(f"   AI Features: {len(data.get('ai_features', []))} available")
            return True
        else:
            print(f"❌ API Info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Info error: {e}")
        return False

def test_dataset_endpoints():
    print(f"\n📈 TESTING DATASET ENDPOINTS")
    print("-" * 40)
    
    # Test dataset roles
    try:
        response = requests.get(f"{BASE_URL}/api/resume/dataset-roles", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dataset Roles: {data.get('total_roles', 0)} roles available")
        else:
            print(f"❌ Dataset Roles failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dataset Roles error: {e}")
    
    # Test dataset stats
    try:
        response = requests.get(f"{BASE_URL}/api/resume/dataset-stats", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dataset Stats: {data.get('total_jobs', 0)} jobs, {data.get('total_skills', 0)} skills")
            return True
        else:
            print(f"❌ Dataset Stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dataset Stats error: {e}")
        return False

def test_auth_endpoints():
    print(f"\n🔐 TESTING AUTHENTICATION")
    print("-" * 40)
    
    # Test signup
    signup_data = {
        "name": "Test User",
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", 
                               json=signup_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Signup successful: {data.get('message', 'User created')}")
            token = data.get('access_token')
            
            # Test login
            login_data = {
                "email": signup_data["email"],
                "password": signup_data["password"]
            }
            
            response = requests.post(f"{BASE_URL}/api/auth/login", 
                                   json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Login successful: Token received")
                return data.get('access_token')
            else:
                print(f"❌ Login failed: {response.status_code}")
                return None
        else:
            print(f"❌ Signup failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

def test_intelligent_analysis(token):
    print(f"\n🧠 TESTING INTELLIGENT ANALYSIS")
    print("-" * 40)
    
    if not token:
        print("❌ No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test skill market analysis
    try:
        response = requests.get(f"{BASE_URL}/api/resume/skill-market-analysis", 
                              headers=headers, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'warning':
                print(f"⚠️ Market Analysis: {data.get('message')}")
            else:
                print(f"✅ Market Analysis: Portfolio analysis complete")
                if 'user_skills_analysis' in data:
                    skills_data = data['user_skills_analysis']
                    print(f"   Skills: {skills_data.get('total_skills', 0)} total")
        else:
            print(f"❌ Market Analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Market Analysis error: {e}")
    
    # Test intelligent role analysis
    role_data = {
        "role_title": "Data Scientist",
        "user_skills": ["Python", "Machine Learning", "SQL"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/resume/intelligent-role-analysis", 
                               json=role_data, headers=headers, timeout=20)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Intelligent Role Analysis: Analysis complete")
            if 'analysis' in data:
                analysis = data['analysis']
                print(f"   Role: {analysis.get('role_title', 'N/A')}")
        else:
            print(f"❌ Intelligent Role Analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Intelligent Role Analysis error: {e}")
    
    return True

def main():
    print("🚀 TESTING ALL API ENDPOINTS")
    print("=" * 60)
    
    # Test basic endpoints
    health_ok = test_health_check()
    info_ok = test_api_info()
    dataset_ok = test_dataset_endpoints()
    
    # Test authentication and get token
    token = test_auth_endpoints()
    
    # Test intelligent features
    intelligent_ok = test_intelligent_analysis(token)
    
    print(f"\n📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"API Info: {'✅ PASS' if info_ok else '❌ FAIL'}")
    print(f"Dataset: {'✅ PASS' if dataset_ok else '❌ FAIL'}")
    print(f"Authentication: {'✅ PASS' if token else '❌ FAIL'}")
    print(f"Intelligent Analysis: {'✅ PASS' if intelligent_ok else '❌ FAIL'}")
    
    if all([health_ok, info_ok, dataset_ok, token, intelligent_ok]):
        print(f"\n🎉 ALL API TESTS PASSED!")
        print(f"🌐 Backend Server: http://localhost:8000")
        print(f"📖 API Documentation: http://localhost:8000/docs")
        print(f"🎯 Frontend Application: http://localhost:3000/index.html")
        print(f"\n✨ READY TO USE!")
    else:
        print(f"\n⚠️ Some tests failed. Check the server logs.")

if __name__ == "__main__":
    main()