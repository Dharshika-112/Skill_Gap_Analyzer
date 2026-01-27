#!/usr/bin/env python3
"""
Debug role matching issue
"""

import requests
import json

def debug_role_matching():
    base_url = "http://localhost:8000"
    
    user_skills_data = {
        "skills": ["Python", "JavaScript", "React"],
        "experience": {"type": "internship", "years": 0.5}
    }
    
    print("🔍 Debugging Role Matching...")
    print(f"Request data: {json.dumps(user_skills_data, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}/api/data/recommend-roles", json=user_skills_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Recommendations: {len(data.get('recommendations', []))}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_role_matching()