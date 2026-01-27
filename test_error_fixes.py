#!/usr/bin/env python3
"""
Test Error Fixes
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_error_fixes():
    print("🔧 TESTING ERROR FIXES")
    print("=" * 50)
    
    # Test 1: Authentication with unique email
    timestamp = int(time.time())
    user_data = {
        "name": "Error Fix Test User",
        "email": f"errorfix_{timestamp}@test.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=user_data, timeout=10)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"✅ Authentication: Fixed")
        else:
            print(f"❌ Authentication: Still failing - {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Authentication Error: {e}")
        return False
    
    # Test 2: ATS Analysis (Database collection fix)
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
        
        if response.status_code == 200:
            print(f"✅ ATS Analysis & Database: Fixed")
        else:
            print(f"❌ ATS Analysis: Still failing - {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ATS Analysis Error: {e}")
    
    # Test 3: Resume Ranking (500 error fix)
    try:
        ranking_request = {
            "job_description": "Python developer position",
            "target_role": "Software Engineer"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resume/rank-resumes",
            json=ranking_request,
            headers={'Authorization': f'Bearer {token}'},
            timeout=15
        )
        
        if response.status_code == 200:
            print(f"✅ Resume Ranking: Fixed")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message', 'No message')}")
        else:
            print(f"❌ Resume Ranking: Still failing - {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Resume Ranking Error: {e}")
    
    # Test 4: Upload and Analyze (404 error fix)
    try:
        # Create a simple test resume
        resume_content = "John Doe\nSoftware Engineer\n\nTECHNICAL SKILLS\nPython, JavaScript, React"
        
        with open('error_fix_test_resume.txt', 'w') as f:
            f.write(resume_content)
        
        with open('error_fix_test_resume.txt', 'rb') as f:
            files = {'file': ('error_fix_test_resume.txt', f, 'text/plain')}
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.post(
                f"{BASE_URL}/api/resume/upload-and-analyze",
                files=files,
                headers=headers,
                timeout=30
            )
        
        if response.status_code == 200:
            print(f"✅ Upload and Analyze: Fixed")
        else:
            print(f"❌ Upload and Analyze: Still failing - {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Upload and Analyze Error: {e}")
    finally:
        # Clean up
        try:
            import os
            os.remove('error_fix_test_resume.txt')
        except:
            pass
    
    return True

if __name__ == "__main__":
    test_error_fixes()
    print(f"\n🎯 ERROR FIX TEST COMPLETED")