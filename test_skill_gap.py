#!/usr/bin/env python3
"""
Test Skill Gap Analysis endpoint specifically
"""

import requests
import time

def test_skill_gap():
    base_url = "http://localhost:8000"
    
    # First signup to get a token
    test_email = f"skilltest_{int(time.time())}@example.com"
    signup_data = {
        "name": "Skill Test User",
        "email": test_email,
        "password": "test123"
    }
    
    response = requests.post(f"{base_url}/api/auth/signup", json=signup_data)
    if response.status_code != 200:
        print(f"❌ Signup failed: {response.text}")
        return False
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test skill gap analysis
    print("🧪 Testing Skill Gap Analysis...")
    
    # Check available endpoints
    print("\n📍 Checking available endpoints:")
    try:
        response = requests.get(f"{base_url}/api/skills/", timeout=10)
        print(f"GET /api/skills/: {response.status_code}")
    except Exception as e:
        print(f"GET /api/skills/: Error - {e}")
    
    try:
        response = requests.get(f"{base_url}/api/skills/gap-analysis", headers=headers, timeout=10)
        print(f"GET /api/skills/gap-analysis: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"GET /api/skills/gap-analysis: Error - {e}")
    
    # Try the data endpoint instead
    try:
        gap_data = {
            "user_skills": ["Python", "JavaScript", "SQL"],
            "role_skills": ["Python", "JavaScript", "React", "Node.js", "MongoDB"],
            "role_name": "Full Stack Developer"
        }
        response = requests.post(f"{base_url}/api/data/skill-gap", json=gap_data, timeout=15)
        print(f"POST /api/data/skill-gap: {response.status_code}")
        if response.status_code == 200:
            print("✅ Skill gap analysis working via /api/data/skill-gap")
            return True
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"POST /api/data/skill-gap: Error - {e}")
    
    return False

if __name__ == "__main__":
    success = test_skill_gap()
    print(f"\n🎯 Skill Gap Test: {'PASSED' if success else 'FAILED'}")