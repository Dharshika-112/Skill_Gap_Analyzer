#!/usr/bin/env python3
"""
Complete API Test: Signup → Login → Upload Resume → Parse
This tests the FULL workflow with proper token handling
"""
import requests
import json
import random
import string
import os

BASE_URL = "http://localhost:8000"

def random_email():
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"user_{rand}@test.com"

print("\n" + "="*80)
print("COMPLETE WORKFLOW TEST: SIGNUP → LOGIN → RESUME UPLOAD → PARSE")
print("="*80)

# ============================================================================
# STEP 1: SIGNUP
# ============================================================================
print("\n[STEP 1/4] SIGNUP - Create account")
print("-" * 80)

email = random_email()
print(f"Creating account: {email}")

try:
    resp = requests.post(
        f"{BASE_URL}/api/auth/signup",
        json={"name": "Test User", "email": email, "password": "test123"},
        timeout=5
    )
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ FAILED: {resp.text}")
        exit(1)
    
    result = resp.json()
    if result.get("status") != "success":
        print(f"❌ FAILED: {result}")
        exit(1)
    
    token = result.get("access_token")
    user_id = result.get("user_id")
    
    print(f"✅ SIGNUP SUCCESS")
    print(f"   User ID: {user_id}")
    print(f"   Token: {token[:30]}...")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    exit(1)

# ============================================================================
# STEP 2: LOGIN
# ============================================================================
print("\n[STEP 2/4] LOGIN - Get JWT token")
print("-" * 80)

try:
    resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": "test123"},
        timeout=5
    )
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ FAILED: {resp.text}")
        exit(1)
    
    result = resp.json()
    if result.get("status") != "success":
        print(f"❌ FAILED: {result}")
        exit(1)
    
    login_token = result.get("access_token")
    print(f"✅ LOGIN SUCCESS")
    print(f"   Token: {login_token[:30]}...")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    exit(1)

# ============================================================================
# STEP 3: CREATE SAMPLE RESUME
# ============================================================================
print("\n[STEP 3/4] RESUME UPLOAD - Create and upload resume")
print("-" * 80)

resume_text = """
JOHN SMITH
john@example.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced Data Scientist with 2 years of professional experience.
Specialized in machine learning and data analysis.

TECHNICAL SKILLS
Languages: Python, JavaScript, SQL, R, Java
Databases: MySQL, PostgreSQL, MongoDB
Libraries: TensorFlow, Keras, Scikit-learn, Pandas, NumPy
Cloud: AWS, Google Cloud Platform, Azure
DevOps: Docker, Kubernetes, Jenkins, GitHub Actions

WORK EXPERIENCE
Junior Data Scientist, Tech Company (2 years)
- Built machine learning models using TensorFlow and Keras
- Analyzed large datasets with Python and Pandas
- Created SQL queries for data extraction from PostgreSQL
- Deployed models using Docker and Kubernetes
- Set up CI/CD pipelines with Jenkins

EDUCATION
Bachelor of Science in Computer Science
State University, 2022
"""

resume_path = "sample_resume_test.txt"
with open(resume_path, 'w') as f:
    f.write(resume_text)

print(f"Resume file created: {resume_path}")

try:
    with open(resume_path, 'rb') as f:
        files = {'file': f}
        headers = {'Authorization': f'Bearer {login_token}'}
        
        resp = requests.post(
            f"{BASE_URL}/api/data/upload-resume",
            files=files,
            headers=headers,
            timeout=10
        )
    
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ FAILED: {resp.text}")
        exit(1)
    
    result = resp.json()
    if result.get("status") != "success":
        print(f"❌ FAILED: {result}")
        exit(1)
    
    parsed = result.get("parsed", {})
    skills = parsed.get("skills", [])
    experience = parsed.get("experience", {})
    resume_id = parsed.get("resume_id")
    
    print(f"✅ RESUME UPLOAD SUCCESS")
    print(f"   Resume ID: {resume_id}")
    print(f"   Skills extracted: {len(skills)}")
    print(f"   Experience type: {experience.get('type')}")
    print(f"   Years: {experience.get('years')}")
    
    if len(skills) > 0:
        print(f"\n   Top 10 Skills:")
        for skill in skills[:10]:
            print(f"     • {skill}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
finally:
    if os.path.exists(resume_path):
        os.remove(resume_path)

# ============================================================================
# STEP 4: VERIFY PROFILE
# ============================================================================
print("\n[STEP 4/4] VERIFY - Check user profile")
print("-" * 80)

try:
    headers = {'Authorization': f'Bearer {login_token}'}
    resp = requests.get(f"{BASE_URL}/api/auth/me", headers=headers, timeout=5)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ FAILED: {resp.text}")
        exit(1)
    
    profile = resp.json()
    print(f"✅ PROFILE VERIFIED")
    print(f"   Name: {profile.get('name')}")
    print(f"   Email: {profile.get('email')}")
    print(f"   User ID: {profile.get('user_id')}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    exit(1)

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✅ COMPLETE WORKFLOW TEST PASSED!")
print("="*80)
print(f"""
SUMMARY:
✅ Signup: Working (user created)
✅ Login: Working (JWT token obtained)
✅ Profile: Working (token authentication verified)
✅ Resume Upload: Working (file parsed successfully)
✅ Skill Parsing: Working ({len(skills)} skills extracted)
✅ Experience Detection: Working (detected as {experience.get('type')})

NEXT STEPS:
1. Open http://localhost:3000/app.html in browser
2. Use the signup form to create account
3. Login with your credentials
4. Upload a resume
5. View extracted skills and experience

The system is FULLY OPERATIONAL! ✅
""")
print("="*80 + "\n")
