#!/usr/bin/env python3
"""
Test the Complete Intelligent Role Matching System
"""

import sys
import requests
import json
from pathlib import Path

# Add backend to path
sys.path.append('backend')

from backend.app.services.intelligent_role_matcher import (
    find_intelligent_matches,
    get_skill_recommendations,
    get_skill_importance
)
from backend.app.services.resume_parser import extract_skills_from_text

def test_intelligent_role_matching():
    print("🧠 TESTING INTELLIGENT ROLE MATCHING SYSTEM")
    print("=" * 60)
    
    # Test with user's resume skills
    user_resume_text = """
    TECHNICAL SKILLS                           CERTIFICATIONS & COURSES
    •    Programming: Python, C, DSA, Java                •    CISCO - Python Essentials
    •    Web: HTML, CSS, JavaScript, ReactJS              •    Google - Foundations of Data Science
    •    Database: SQL, DBMS                              •    CU Boulder - Foundations of DSA (Specialization)
    •    AI & Data Science: Machine Learning, Deep Learning, AI    •    IBM - Machine Learning with Python
         Deployment                                       •    Juniper - NCIA-Cloud / Mist AI Associate
    •    Tools & Platform: Git, GitHub, Docker           •    Infosys – Programming Fundamentals Using Java
    """
    
    print("1️⃣ EXTRACTING SKILLS FROM RESUME")
    extracted_skills = extract_skills_from_text(user_resume_text)
    print(f"Extracted Skills ({len(extracted_skills)}):")
    for i, skill in enumerate(extracted_skills, 1):
        print(f"  {i}. {skill}")
    
    if not extracted_skills:
        print("❌ No skills extracted! Check resume parser.")
        return False
    
    print(f"\n2️⃣ TESTING SKILL IMPORTANCE ANALYSIS")
    print("Skill Importance Scores:")
    skill_scores = []
    for skill in extracted_skills:
        importance = get_skill_importance(skill)
        skill_scores.append((skill, importance))
        priority = "High" if importance > 0.5 else "Medium" if importance > 0.2 else "Low"
        print(f"  • {skill}: {importance:.3f} ({priority})")
    
    # Sort by importance
    skill_scores.sort(key=lambda x: x[1], reverse=True)
    print(f"\nTop 5 Most Important Skills:")
    for skill, score in skill_scores[:5]:
        print(f"  🔥 {skill}: {score:.3f}")
    
    print(f"\n3️⃣ TESTING INTELLIGENT ROLE MATCHING")
    intelligent_matches = find_intelligent_matches(extracted_skills, top_n=5)
    
    if not intelligent_matches:
        print("❌ No intelligent matches found!")
        return False
    
    print(f"Found {len(intelligent_matches)} intelligent role matches:")
    for i, match in enumerate(intelligent_matches, 1):
        print(f"\n  {i}. {match['role']}")
        print(f"     AI Score: {match['intelligent_score']}%")
        print(f"     Priority Match: {match['high_priority_match_percentage']}%")
        print(f"     Matching Skills: {match['total_matching_skills']}")
        print(f"     Missing Skills: {match['total_missing_skills']}")
        print(f"     Top Missing: {', '.join(match['missing_skills'][:3])}")
    
    print(f"\n4️⃣ TESTING SKILL RECOMMENDATIONS")
    recommendations = get_skill_recommendations(extracted_skills)
    
    if recommendations.get('high_priority_skills'):
        print(f"High Priority Skills to Learn ({len(recommendations['high_priority_skills'])}):")
        for skill_data in recommendations['high_priority_skills'][:5]:
            print(f"  💡 {skill_data['skill']}: {skill_data['importance']:.3f} importance, {skill_data['job_count']} jobs")
    
    if recommendations.get('market_trends', {}).get('top_skills_by_demand'):
        print(f"\nTop Market Demand Skills:")
        for skill_data in recommendations['market_trends']['top_skills_by_demand'][:5]:
            print(f"  📈 {skill_data['skill']}: {skill_data['job_count']} jobs")
    
    return True

def test_api_endpoints():
    print(f"\n5️⃣ TESTING API ENDPOINTS")
    print("-" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test dataset roles endpoint
    try:
        response = requests.get(f"{base_url}/api/resume/dataset-roles", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dataset Roles API: {data.get('total_roles', 0)} roles available")
        else:
            print(f"❌ Dataset Roles API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dataset Roles API error: {e}")
    
    # Test dataset stats endpoint
    try:
        response = requests.get(f"{base_url}/api/resume/dataset-stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dataset Stats API: {data.get('total_jobs', 0)} jobs, {data.get('total_skills', 0)} skills")
        else:
            print(f"❌ Dataset Stats API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dataset Stats API error: {e}")

def test_complete_workflow():
    print(f"\n6️⃣ TESTING COMPLETE WORKFLOW")
    print("-" * 40)
    
    # Simulate complete workflow
    user_skills = ['Python', 'Machine Learning', 'JavaScript', 'React', 'SQL', 'Git']
    
    print(f"User Skills: {', '.join(user_skills)}")
    
    # Step 1: Get skill importance
    print(f"\nStep 1: Skill Importance Analysis")
    for skill in user_skills:
        importance = get_skill_importance(skill)
        priority = "🔥 High" if importance > 0.5 else "📖 Medium" if importance > 0.2 else "📝 Low"
        print(f"  {skill}: {priority} ({importance:.3f})")
    
    # Step 2: Get intelligent matches
    print(f"\nStep 2: Intelligent Role Matching")
    matches = find_intelligent_matches(user_skills, top_n=3)
    for match in matches:
        print(f"  🎯 {match['role']}: {match['intelligent_score']}% AI Score")
    
    # Step 3: Get recommendations
    print(f"\nStep 3: Skill Recommendations")
    recs = get_skill_recommendations(user_skills)
    if recs.get('high_priority_skills'):
        for skill_data in recs['high_priority_skills'][:3]:
            print(f"  💡 Learn: {skill_data['skill']} (importance: {skill_data['importance']:.3f})")
    
    return True

if __name__ == "__main__":
    print("🚀 STARTING INTELLIGENT SYSTEM TESTS")
    print("=" * 60)
    
    try:
        # Test 1: Core intelligent matching
        success1 = test_intelligent_role_matching()
        
        # Test 2: API endpoints
        test_api_endpoints()
        
        # Test 3: Complete workflow
        success3 = test_complete_workflow()
        
        print(f"\n" + "=" * 60)
        if success1 and success3:
            print("🎉 ALL TESTS PASSED! Intelligent system is working!")
            print("\n📋 NEXT STEPS:")
            print("1. Start the backend server: python backend/app/main.py")
            print("2. Open frontend: http://localhost:3000/index.html")
            print("3. Upload your resume to test the complete workflow")
            print("4. Try the new AI-powered role matching features")
        else:
            print("❌ Some tests failed. Check the implementation.")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()