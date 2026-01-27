#!/usr/bin/env python3
"""
Test resume parsing end-to-end:
1. Signup user
2. Login and get token
3. Upload resume
4. Verify skills are extracted
"""

import requests
import json
import os
import random
import string
from datetime import datetime

BASE_URL = "http://localhost:8000"

def random_email():
    """Generate random email"""
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"testuser_{rand}@test.com"

def test_resume_parsing():
    """Full E2E test"""
    print("\n" + "="*60)
    print("RESUME PARSING TEST")
    print("="*60)
    
    # 1. SIGNUP
    print("\n[1] SIGNUP")
    email = random_email()
    print(f"Creating user: {email}")
    
    signup_data = {
        "name": "Test User",
        "email": email,
        "password": "test123"
    }
    
    resp = requests.post(f"{BASE_URL}/api/auth/signup", json=signup_data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    
    if resp.status_code != 200:
        print("❌ Signup failed!")
        return False
    
    signup_result = resp.json()
    token = signup_result.get("access_token")
    user_id = signup_result.get("user_id")
    
    if not token:
        print("❌ No token returned from signup!")
        return False
    
    print(f"✅ Token received: {token[:20]}...")
    
    # 2. CREATE SAMPLE RESUME
    print("\n[2] CREATE SAMPLE RESUME")
    
    sample_resume = """
    JOHN SMITH
    john@example.com | LinkedIn.com/in/john
    
    PROFESSIONAL SUMMARY
    Experienced Data Scientist with 2 years of internship and professional experience.
    Specialized in machine learning and data analysis.
    
    TECHNICAL SKILLS
    Languages: Python, JavaScript, SQL, R
    Databases: MySQL, PostgreSQL, MongoDB
    Tools: TensorFlow, Keras, Scikit-learn, Pandas
    Cloud: AWS, Google Cloud Platform
    DevOps: Docker, Kubernetes, Jenkins
    
    EXPERIENCE
    Data Science Intern, Tech Company (6 months)
    - Built machine learning models using TensorFlow and Keras
    - Analyzed data using Python and Pandas
    - Deployed models using Docker
    
    Junior Data Scientist, Analytics Corp (1.5 years)
    - Developed skill gap analysis using scikit-learn
    - Created SQL queries for data extraction
    - Managed MongoDB databases
    - Implemented CI/CD using Jenkins
    
    EDUCATION
    Bachelor of Science in Computer Science
    """
    
    resume_path = "backend/data/raw/uploads/test_resume.txt"
    os.makedirs(os.path.dirname(resume_path), exist_ok=True)
    
    with open(resume_path, 'w') as f:
        f.write(sample_resume)
    
    print(f"✅ Created resume: {resume_path}")
    
    # 3. UPLOAD RESUME
    print("\n[3] UPLOAD RESUME")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(resume_path, 'rb') as f:
        files = {'file': f}
        resp = requests.post(
            f"{BASE_URL}/api/data/upload-resume",
            files=files,
            headers=headers
        )
    
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    
    if resp.status_code != 200:
        print("❌ Upload failed!")
        print(f"Response text: {resp.text}")
        return False
    
    upload_result = resp.json()
    
    if upload_result.get("status") != "success":
        print("❌ Upload status is not success!")
        return False
    
    print("✅ Upload successful!")
    
    # 4. CHECK PARSED SKILLS
    print("\n[4] EXTRACTED SKILLS")
    
    parsed = upload_result.get("parsed", {})
    skills = parsed.get("skills", [])
    experience = parsed.get("experience", {})
    
    print(f"\nExtracted Skills ({len(skills)}):")
    for skill in skills:
        print(f"  • {skill}")
    
    print(f"\nExperience Detected:")
    print(f"  Type: {experience.get('type')}")
    print(f"  Years: {experience.get('years')}")
    
    # 5. VERIFY SKILLS
    print("\n[5] VERIFICATION")
    
    expected_skills = ['Python', 'SQL', 'TensorFlow', 'Keras', 'Docker', 'Kubernetes']
    found_skills = []
    missing_skills = []
    
    for skill in expected_skills:
        if any(skill.lower() in s.lower() for s in skills):
            found_skills.append(skill)
        else:
            missing_skills.append(skill)
    
    print(f"\n✅ Found {len(found_skills)} expected skills:")
    for skill in found_skills:
        print(f"  ✓ {skill}")
    
    if missing_skills:
        print(f"\n⚠️  Missing {len(missing_skills)} expected skills:")
        for skill in missing_skills:
            print(f"  ✗ {skill}")
    
    # 6. TEST RESULT
    print("\n" + "="*60)
    if len(skills) > 0 and len(found_skills) >= 4:
        print("✅ RESUME PARSING WORKING!")
        print(f"   {len(skills)} skills extracted successfully")
        return True
    else:
        print("❌ RESUME PARSING NOT WORKING!")
        print(f"   Only {len(skills)} skills extracted (expected 8+)")
        return False

if __name__ == "__main__":
    try:
        success = test_resume_parsing()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
