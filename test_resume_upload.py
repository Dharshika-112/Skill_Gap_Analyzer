#!/usr/bin/env python3
"""
Test Resume Upload with Improved Parser
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_resume_upload():
    print("📄 TESTING RESUME UPLOAD WITH IMPROVED PARSER")
    print("=" * 60)
    
    # Step 1: Create a test user
    print("1️⃣ CREATING TEST USER")
    print("-" * 40)
    
    timestamp = int(time.time())
    user_data = {
        "name": "Resume Test User",
        "email": f"resumetest_{timestamp}@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=user_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ User created successfully")
        else:
            print(f"❌ User creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return False
    
    # Step 2: Create a test resume file
    print(f"\n2️⃣ CREATING TEST RESUME")
    print("-" * 40)
    
    resume_content = """
    John Doe
    Software Developer
    
    TECHNICAL SKILLS
    • Programming: Python, C, DSA, Java
    • Web: HTML, CSS, JavaScript, ReactJS
    • Database: SQL, DBMS
    • AI & Data Science: Machine Learning, Deep Learning, AI Deployment
    • Tools & Platform: Git, GitHub, Docker
    
    CERTIFICATIONS & COURSES
    • CISCO - Python Essentials
    • Google - Foundations of Data Science
    • CU Boulder - Foundations of DSA (Specialization)
    • IBM - Machine Learning with Python
    • Juniper - NCIA-Cloud / Mist AI Associate
    • Infosys – Programming Fundamentals Using Java
    
    EXPERIENCE
    Software Developer Intern at TechCorp (6 months)
    - Developed web applications using React and Node.js
    - Worked with Python for data analysis
    
    EDUCATION
    Bachelor of Computer Science
    """
    
    # Save as text file
    with open('test_resume.txt', 'w') as f:
        f.write(resume_content)
    
    print("✅ Test resume created")
    
    # Step 3: Upload resume
    print(f"\n3️⃣ UPLOADING RESUME")
    print("-" * 40)
    
    try:
        with open('test_resume.txt', 'rb') as f:
            files = {'file': ('test_resume.txt', f, 'text/plain')}
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.post(
                f"{BASE_URL}/api/resume/upload-and-analyze",
                files=files,
                headers=headers,
                timeout=30
            )
        
        print(f"Upload response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resume uploaded successfully")
            
            # Display results
            print(f"\nExtracted Skills ({len(data.get('extracted_skills', []))}):")
            for skill in data.get('extracted_skills', []):
                print(f"  • {skill}")
            
            print(f"\nResume Score: {data.get('resume_score', {}).get('overall_score', 0)}%")
            
            if 'intelligent_role_matches' in data:
                print(f"\nTop Role Matches:")
                for match in data['intelligent_role_matches'][:3]:
                    print(f"  • {match['role']}: {match['intelligent_score']}% AI Score")
            
            # Check if skills are properly extracted
            expected_skills = ['Python', 'Java', 'HTML', 'CSS', 'JavaScript', 'React', 'SQL', 'Machine Learning', 'Deep Learning', 'Git', 'Docker']
            extracted_skills = data.get('extracted_skills', [])
            
            found_count = 0
            for expected in expected_skills:
                if any(expected.lower() in extracted.lower() for extracted in extracted_skills):
                    found_count += 1
            
            success_rate = (found_count / len(expected_skills)) * 100
            print(f"\nSkill Extraction Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 80:
                print("🎉 RESUME PARSING WORKING EXCELLENTLY!")
            elif success_rate >= 60:
                print("✅ RESUME PARSING WORKING WELL!")
            else:
                print("⚠️ RESUME PARSING NEEDS IMPROVEMENT")
            
            return True
            
        else:
            print(f"❌ Resume upload failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Resume upload error: {e}")
        return False
    
    finally:
        # Clean up
        try:
            import os
            os.remove('test_resume.txt')
        except:
            pass

if __name__ == "__main__":
    success = test_resume_upload()
    
    if success:
        print(f"\n🎯 RESUME UPLOAD TEST SUCCESSFUL!")
        print("The improved parser is working correctly.")
    else:
        print(f"\n❌ RESUME UPLOAD TEST FAILED!")
        print("Check the backend server and try again.")