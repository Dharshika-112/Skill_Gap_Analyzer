#!/usr/bin/env python3
"""
Debug Specific Error
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def debug_error():
    print("🔍 DEBUGGING SPECIFIC ERROR")
    print("=" * 50)
    
    # Test 1: Basic API health
    try:
        response = requests.get(f"{BASE_URL}/api/resume/all-skills", timeout=5)
        print(f"✅ Basic API: {response.status_code}")
    except Exception as e:
        print(f"❌ Basic API Error: {e}")
        return
    
    # Test 2: Authentication
    try:
        user_data = {
            "name": "Debug User",
            "email": "debug@test.com",
            "password": "test123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=user_data, timeout=10)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"✅ Authentication: {response.status_code}")
        else:
            print(f"❌ Authentication: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Authentication Error: {e}")
        return
    
    # Test 3: ATS Analysis
    try:
        ats_request = {
            "user_skills": ["Python", "JavaScript", "React"],
            "experience_years": 2,
            "education": "Bachelor's",
            "certifications": [],
            "target_role": "Software Engineer",
            "projects_count": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resume/ats-analysis",
            json=ats_request,
            headers={'Authorization': f'Bearer {token}'},
            timeout=30
        )
        
        print(f"ATS Analysis Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error Response: {response.text}")
        else:
            data = response.json()
            print(f"✅ ATS Analysis: Working")
            print(f"   ATS Score: {data.get('ats_scoring', {}).get('ats_score', 'N/A')}")
            
    except Exception as e:
        print(f"❌ ATS Analysis Error: {e}")
    
    # Test 4: Resume-JD Similarity (the failing one)
    try:
        similarity_request = {
            "resume_text": "Python developer with React experience",
            "job_description": "Looking for Python and React developer"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resume/resume-jd-similarity",
            json=similarity_request,
            headers={'Authorization': f'Bearer {token}'},
            timeout=15
        )
        
        print(f"Resume-JD Similarity Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error Response: {response.text}")
            try:
                error_data = response.json()
                print(f"Error Details: {error_data}")
            except:
                pass
        else:
            print(f"✅ Resume-JD Similarity: Working")
            
    except Exception as e:
        print(f"❌ Resume-JD Similarity Error: {e}")

if __name__ == "__main__":
    debug_error()