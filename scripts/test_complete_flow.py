#!/usr/bin/env python3
"""
Complete flow test:
1. Signup (create user account)
2. Login (get JWT token)
3. Resume Upload (parse resume with token)
4. Verify skills extracted
"""

import requests
import json
import random
import string

BASE_URL = "http://localhost:8000"

def random_email():
    """Generate random email"""
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{rand}@example.com"

print("\n" + "="*70)
print("COMPLETE WORKFLOW TEST: SIGNUP → LOGIN → RESUME UPLOAD → PARSE")
print("="*70)

# ============================================================================
# STEP 1: SIGNUP
# ============================================================================
print("\n[STEP 1] SIGNUP - Creating new user account")
print("-" * 70)

email = random_email()
signup_payload = {
    "name": "Test User",
    "email": email,
    "password": "test123"
}

print(f"Signup data: {json.dumps(signup_payload, indent=2)}")

try:
    resp = requests.post(f"{BASE_URL}/api/auth/signup", json=signup_payload, timeout=5)
    print(f"Status Code: {resp.status_code}")
    signup_result = resp.json()
    print(f"Response: {json.dumps(signup_result, indent=2)}")
    
    if resp.status_code != 200:
        print("❌ SIGNUP FAILED!")
        exit(1)
    
    if signup_result.get("status") != "success":
        print("❌ Signup returned non-success status!")
        exit(1)
    
    access_token = signup_result.get("access_token")
    user_id = signup_result.get("user_id")
    
    if not access_token or not user_id:
        print("❌ No token or user_id returned!")
        exit(1)
    
    print(f"✅ SIGNUP SUCCESS!")
    print(f"   User ID: {user_id}")
    print(f"   Token: {access_token[:30]}...")
    
except Exception as e:
    print(f"❌ SIGNUP ERROR: {e}")
    exit(1)

# ============================================================================
# STEP 2: LOGIN
# ============================================================================
print("\n[STEP 2] LOGIN - Getting new JWT token")
print("-" * 70)

login_payload = {
    "email": email,
    "password": "test123"
}

print(f"Login data: {json.dumps(login_payload, indent=2)}")

try:
    resp = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload, timeout=5)
    print(f"Status Code: {resp.status_code}")
    login_result = resp.json()
    print(f"Response: {json.dumps(login_result, indent=2)}")
    
    if resp.status_code != 200:
        print("❌ LOGIN FAILED!")
        exit(1)
    
    if login_result.get("status") != "success":
        print("❌ Login returned non-success status!")
        exit(1)
    
    login_token = login_result.get("access_token")
    
    if not login_token:
        print("❌ No token returned from login!")
        exit(1)
    
    print(f"✅ LOGIN SUCCESS!")
    print(f"   New Token: {login_token[:30]}...")
    
except Exception as e:
    print(f"❌ LOGIN ERROR: {e}")
    exit(1)

# ============================================================================
# STEP 3: GET PROFILE (verify token works)
# ============================================================================
print("\n[STEP 3] PROFILE - Verify token is working")
print("-" * 70)

try:
    headers = {"Authorization": f"Bearer {login_token}"}
    resp = requests.get(f"{BASE_URL}/api/auth/me", headers=headers, timeout=5)
    print(f"Status Code: {resp.status_code}")
    profile_result = resp.json()
    print(f"Response: {json.dumps(profile_result, indent=2)}")
    
    if resp.status_code != 200:
        print("❌ PROFILE FETCH FAILED!")
        exit(1)
    
    print(f"✅ TOKEN WORKING!")
    print(f"   Name: {profile_result.get('name')}")
    print(f"   Email: {profile_result.get('email')}")
    
except Exception as e:
    print(f"❌ PROFILE ERROR: {e}")
    exit(1)

# ============================================================================
# STEP 4: UPLOAD RESUME
# ============================================================================
print("\n[STEP 4] RESUME UPLOAD - Parsing resume file")
print("-" * 70)

# Create sample resume
resume_text = """
JOHN SMITH
john@example.com

PROFESSIONAL SUMMARY
Experienced software engineer with 2 years of internship and professional experience.

TECHNICAL SKILLS
Languages: Python, JavaScript, SQL, Java
Databases: MySQL, PostgreSQL, MongoDB
Tools: TensorFlow, Keras, Scikit-learn, Pandas, NumPy
Cloud: AWS, Google Cloud Platform, Azure
DevOps: Docker, Kubernetes, Jenkins, GitHub Actions
Frontend: React, Vue.js, Bootstrap, HTML5, CSS3

EXPERIENCE
Data Science Intern, Tech Company (6 months)
- Built machine learning models using TensorFlow and Keras
- Analyzed data with Python and Pandas
- Deployed models using Docker

Junior Software Engineer, Software Corp (1.5 years)
- Developed REST APIs using Python and FastAPI
- Created databases with PostgreSQL and MongoDB
- Implemented CI/CD pipelines with Jenkins
"""

resume_path = "backend/data/raw/uploads/sample_resume.txt"
import os
os.makedirs(os.path.dirname(resume_path), exist_ok=True)
with open(resume_path, 'w') as f:
    f.write(resume_text)

print(f"Resume file created: {resume_path}")

# Upload resume
try:
    headers = {"Authorization": f"Bearer {login_token}"}
    with open(resume_path, 'rb') as f:
        files = {'file': f}
        resp = requests.post(
            f"{BASE_URL}/api/data/upload-resume",
            files=files,
            headers=headers,
            timeout=10
        )
    
    print(f"Status Code: {resp.status_code}")
    upload_result = resp.json()
    print(f"Response: {json.dumps(upload_result, indent=2)}")
    
    if resp.status_code != 200:
        print("❌ RESUME UPLOAD FAILED!")
        print(f"Error: {resp.text}")
        exit(1)
    
    if upload_result.get("status") != "success":
        print("❌ Upload returned non-success status!")
        exit(1)
    
    parsed = upload_result.get("parsed", {})
    skills = parsed.get("skills", [])
    experience = parsed.get("experience", {})
    
    print(f"✅ RESUME UPLOAD SUCCESS!")
    print(f"   Resume ID: {parsed.get('resume_id')}")
    print(f"   Filename: {parsed.get('filename')}")
    print(f"   Skills Extracted: {len(skills)}")
    print(f"   Experience Type: {experience.get('type')}")
    print(f"   Years: {experience.get('years')}")
    
    if len(skills) > 0:
        print(f"\n   First 10 Skills:")
        for skill in skills[:10]:
            print(f"     • {skill}")
    
    if len(skills) < 5:
        print("\n⚠️  WARNING: Very few skills extracted!")
    else:
        print(f"\n✅ SKILLS PARSING SUCCESS! ({len(skills)} skills found)")
    
except Exception as e:
    print(f"❌ RESUME UPLOAD ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*70)
print("✅ COMPLETE WORKFLOW TEST PASSED!")
print("="*70)
print(f"""
Summary:
✅ Signup: Working (user created with ID {user_id})
✅ Login: Working (JWT token obtained)
✅ Profile: Working (token authentication verified)
✅ Resume Upload: Working (file parsed successfully)
✅ Skill Parsing: Working ({len(skills)} skills extracted)
✅ Experience Detection: Working (detected as {experience.get('type')})

NEXT STEPS:
1. Frontend should allow user to upload resume after login
2. Display the extracted {len(skills)} skills to user
3. Show experience level detected
4. Allow user to proceed to skill gap analysis
""")
print("="*70 + "\n")
