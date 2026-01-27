#!/usr/bin/env python3
"""
Complete System Test - End to End
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_complete_system():
    print("🚀 TESTING COMPLETE SKILL GAP ANALYZER SYSTEM")
    print("=" * 70)
    
    # Step 1: Create a test user
    print("1️⃣ TESTING USER AUTHENTICATION")
    print("-" * 50)
    
    timestamp = int(time.time())
    user_data = {
        "name": "Complete Test User",
        "email": f"completetest_{timestamp}@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=user_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ User signup successful")
        else:
            print(f"❌ User signup failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User signup error: {e}")
        return False
    
    # Step 2: Test resume upload and analysis
    print(f"\n2️⃣ TESTING RESUME UPLOAD & AI ANALYSIS")
    print("-" * 50)
    
    resume_content = """
    Jane Smith
    Full Stack Developer
    
    TECHNICAL SKILLS
    • Programming Languages: Python, JavaScript, TypeScript, Java, C++
    • Frontend: React, Angular, Vue.js, HTML5, CSS3, Bootstrap
    • Backend: Node.js, Express, Django, Flask, Spring Boot
    • Databases: PostgreSQL, MongoDB, MySQL, Redis
    • Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, Git, GitHub
    • Machine Learning: TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy
    • Mobile: React Native, Flutter
    
    CERTIFICATIONS
    • AWS Certified Solutions Architect
    • Google Cloud Professional Developer
    
    EXPERIENCE
    Senior Full Stack Developer at TechCorp (3 years)
    - Led development of microservices architecture
    - Implemented CI/CD pipelines with Jenkins and Docker
    - Built ML-powered recommendation systems
    """
    
    # Save as text file
    with open('complete_test_resume.txt', 'w') as f:
        f.write(resume_content)
    
    try:
        with open('complete_test_resume.txt', 'rb') as f:
            files = {'file': ('complete_test_resume.txt', f, 'text/plain')}
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.post(
                f"{BASE_URL}/api/resume/upload-and-analyze",
                files=files,
                headers=headers,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resume upload successful")
            
            extracted_skills = data.get('extracted_skills', [])
            print(f"📋 Extracted Skills ({len(extracted_skills)}):")
            for i, skill in enumerate(extracted_skills[:10], 1):
                print(f"   {i}. {skill}")
            if len(extracted_skills) > 10:
                print(f"   ... and {len(extracted_skills) - 10} more")
            
            resume_score = data.get('resume_score', {})
            print(f"📊 Resume Score: {resume_score.get('overall_score', 0)}% ({resume_score.get('category', 'Unknown')})")
            
            intelligent_matches = data.get('intelligent_role_matches', [])
            print(f"🧠 AI Role Matches ({len(intelligent_matches)}):")
            for i, match in enumerate(intelligent_matches[:3], 1):
                print(f"   {i}. {match['role']}: {match['intelligent_score']}% AI Score")
            
            # Check extraction quality
            expected_skills = ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker', 'TensorFlow', 'PostgreSQL']
            found_count = 0
            for expected in expected_skills:
                if any(expected.lower() in extracted.lower() for extracted in extracted_skills):
                    found_count += 1
            
            extraction_rate = (found_count / len(expected_skills)) * 100
            print(f"🎯 Skill Extraction Quality: {extraction_rate:.1f}%")
            
        else:
            print(f"❌ Resume upload failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Resume upload error: {e}")
        return False
    
    # Step 3: Test role analysis
    print(f"\n3️⃣ TESTING INTELLIGENT ROLE ANALYSIS")
    print("-" * 50)
    
    try:
        analysis_data = {
            "role_title": "Full Stack Developer",
            "user_skills": extracted_skills[:15]  # Use first 15 skills
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resume/intelligent-role-analysis",
            json=analysis_data,
            headers={'Authorization': f'Bearer {token}'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Intelligent role analysis successful")
            
            analysis = data.get('analysis', {})
            match_data = analysis.get('intelligent_match_data', {})
            if match_data:
                print(f"🎯 AI Match Score: {match_data.get('intelligent_score', 0)}%")
                print(f"🔥 High Priority Matches: {match_data.get('high_priority_matches', 0)}")
            
            skill_importance = analysis.get('user_skill_importance', [])
            print(f"📈 Top Skills by Market Importance:")
            for i, skill_data in enumerate(skill_importance[:5], 1):
                print(f"   {i}. {skill_data['skill']}: {skill_data['priority']} ({skill_data['importance_score']:.3f})")
            
        else:
            print(f"❌ Role analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Role analysis error: {e}")
        return False
    
    # Step 4: Test market analysis
    print(f"\n4️⃣ TESTING MARKET ANALYSIS")
    print("-" * 50)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/resume/skill-market-analysis",
            headers={'Authorization': f'Bearer {token}'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Market analysis successful")
            
            skills_analysis = data.get('user_skills_analysis', {})
            print(f"💼 Portfolio: {skills_analysis.get('total_skills', 0)} total skills, {skills_analysis.get('high_value_skills', 0)} high-value")
            
            career_insights = data.get('career_insights', {})
            print(f"🎯 Career Readiness: {career_insights.get('career_readiness', 'Unknown')}")
            print(f"💪 Strongest Area: {career_insights.get('strongest_skill_category', 'Unknown')}")
            
        else:
            print(f"❌ Market analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Market analysis error: {e}")
        return False
    
    # Step 5: Test dataset statistics
    print(f"\n5️⃣ TESTING DATASET INTEGRATION")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/resume/dataset-stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dataset integration working")
            print(f"📊 Dataset Stats:")
            print(f"   • Total Jobs: {data.get('total_jobs', 0)}")
            print(f"   • Total Roles: {data.get('total_roles', 0)}")
            print(f"   • Total Skills: {data.get('total_skills', 0)}")
            
            top_skills = data.get('top_skills', [])[:5]
            print(f"🔥 Top Skills in Market:")
            for i, skill_data in enumerate(top_skills, 1):
                print(f"   {i}. {skill_data['skill']}: {skill_data['frequency']} jobs")
            
        else:
            print(f"❌ Dataset stats failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dataset stats error: {e}")
        return False
    
    # Cleanup
    try:
        import os
        os.remove('complete_test_resume.txt')
    except:
        pass
    
    return True

if __name__ == "__main__":
    success = test_complete_system()
    
    print(f"\n{'='*70}")
    if success:
        print("🎉 COMPLETE SYSTEM TEST SUCCESSFUL!")
        print("✅ All components working correctly:")
        print("   • User Authentication")
        print("   • Resume Upload & AI Analysis") 
        print("   • Intelligent Role Matching")
        print("   • Market Analysis")
        print("   • Real Dataset Integration")
        print(f"\n🌐 Frontend Available: http://localhost:3000/index.html")
        print(f"🔧 Backend API: http://localhost:8000")
        print(f"📖 API Docs: http://localhost:8000/docs")
    else:
        print("❌ SYSTEM TEST FAILED!")
        print("Check the backend server and try again.")